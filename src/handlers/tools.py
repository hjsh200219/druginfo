"""
도구 핸들러 - DrugInfo API 도구들을 MCP 도구로 변환
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool
from pydantic import BaseModel, Field

from src.druginfo import (
    list_main_ingredient,
    get_main_ingredient_by_code,
    list_product,
    get_product_by_code,
    list_main_ingredient_drug_effect,
    get_main_ingredient_drug_effect_by_id,
    list_main_ingredient_drug_kind,
    list_main_ingredient_guide_a4,
    list_main_ingredient_guide_a5,
    list_main_ingredient_picto,
    get_main_ingredient_picto_by_code,
    list_product_edicode,
    list_product_edicode_same_ingredient,
    UnauthorizedError,
    DrugInfoError,
)

logger = logging.getLogger(__name__)


# 스키마 캐시 (필요할 때만 로드)
_SCHEMA_CACHE = {}


def _get_schema(tool_name: str) -> Dict[str, Any]:
    """도구 스키마를 on-demand로 로드"""
    if tool_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[tool_name]

    schemas = {
        "login": {
            "type": "object",
            "properties": {
                "userId": {"type": "string"},
                "password": {"type": "string"},
                "force": {"type": "boolean", "default": False},
            },
            "required": ["userId", "password"],
        },
        "search_druginfo": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["ingredient", "product"],
                    "description": "ingredient=주성분, product=제품"
                },
                "query": {"type": "string", "description": "검색어"},
                "PageSize": {"type": "integer", "default": 20},
                "Page": {"type": "integer", "default": 1},
            },
            "required": ["type", "query"],
        },
        "get_druginfo_detail": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["ingredient", "product"],
                    "description": "ingredient=주성분(9자리), product=제품(15자리)"
                },
                "code": {"type": "string", "description": "코드"},
            },
            "required": ["type", "code"],
        },
        "find_same_ingredient": {
            "type": "object",
            "properties": {
                "ProductCode": {"type": "string"},
                "MasterIngredientCode": {"type": "string"},
                "PageSize": {"type": "integer", "default": 20},
            },
        },
    }

    schema = schemas.get(tool_name, {})
    _SCHEMA_CACHE[tool_name] = schema
    return schema


def setup_tool_handlers(server: Server, auth_manager):
    """도구 핸들러 설정"""

    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """사용 가능한 도구 목록 반환 - 스키마는 최소화"""
        tools = [
            Tool(
                name="login",
                description="EDB 로그인",
                inputSchema={"type": "object"},  # 최소 스키마
            ),
            Tool(
                name="search_druginfo",
                description="의약품 검색 (주성분/제품명/통합검색)",
                inputSchema={"type": "object"},
            ),
            Tool(
                name="get_druginfo_detail",
                description="의약품 상세 조회 (코드 필요)",
                inputSchema={"type": "object"},
            ),
            Tool(
                name="find_same_ingredient",
                description="동일 성분 의약품 검색",
                inputSchema={"type": "object"},
            ),
        ]
        return tools

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """도구 실행 - 실행 시점에 스키마 로드"""
        logger.info(f"도구 실행: {name}, 인자: {arguments}")

        # 필요할 때만 상세 스키마 로드 (검증용)
        schema = _get_schema(name)
        logger.debug(f"스키마 로드됨: {name}")

        try:
            # 로그인
            if name == "login":
                token = await auth_manager.login(
                    arguments.get("userId"),
                    arguments.get("password"),
                    arguments.get("force", False)
                )
                return [{"type": "text", "text": f"로그인 성공. 토큰: {token[:20]}..."}]

            # 통합 검색
            elif name == "search_druginfo":
                search_type = arguments.get("type")
                query = arguments.get("query")
                page_size = arguments.get("PageSize", 20)
                page = arguments.get("Page", 1)

                try:
                    if search_type == "ingredient":
                        result = list_main_ingredient(
                            ingredientNameKor=query,
                            PageSize=page_size,
                            Page=page
                        )
                    else:  # product
                        result = list_product(
                            pillName=query,
                            PageSize=page_size,
                            Page=page
                        )
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    if search_type == "ingredient":
                        result = list_main_ingredient(
                            ingredientNameKor=query,
                            PageSize=page_size,
                            Page=page
                        )
                    else:
                        result = list_product(
                            pillName=query,
                            PageSize=page_size,
                            Page=page
                        )
                return [{"type": "text", "text": str(result)}]

            # 상세 조회
            elif name == "get_druginfo_detail":
                detail_type = arguments.get("type")
                code = arguments.get("code")

                try:
                    if detail_type == "ingredient":
                        result = get_main_ingredient_by_code(code)
                    else:  # product
                        result = get_product_by_code(code)
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    if detail_type == "ingredient":
                        result = get_main_ingredient_by_code(code)
                    else:
                        result = get_product_by_code(code)
                return [{"type": "text", "text": str(result)}]

            # 동일 성분 검색
            elif name == "find_same_ingredient":
                try:
                    result = list_product_edicode_same_ingredient(**arguments)
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    result = list_product_edicode_same_ingredient(**arguments)
                return [{"type": "text", "text": str(result)}]

            else:
                raise ValueError(f"알 수 없는 도구: {name}")

        except DrugInfoError as e:
            logger.error(f"DrugInfo 오류: {e}")
            return [{"type": "text", "text": f"오류: {str(e)}"}]
        except Exception as e:
            logger.error(f"도구 실행 오류: {e}")
            return [{"type": "text", "text": f"도구 실행 중 오류 발생: {str(e)}"}]
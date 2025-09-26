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


def setup_tool_handlers(server: Server, auth_manager):
    """도구 핸들러 설정"""

    # 로그인 도구
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """사용 가능한 도구 목록 반환"""
        tools = [
            Tool(
                name="login",
                description="EDB 시스템에 로그인하여 인증 토큰을 받습니다",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "userId": {
                            "type": "string",
                            "description": "사용자 ID (이메일 형식)"
                        },
                        "password": {
                            "type": "string",
                            "description": "비밀번호"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "중복 로그인 강제 해제 여부",
                            "default": False
                        },
                    },
                    "required": ["userId", "password"],
                },
            ),
            Tool(
                name="druginfo_list_main_ingredient",
                description="주성분 목록을 검색합니다",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ingredientNameKor": {
                            "type": "string",
                            "description": "한글 주성분명 (검색어)"
                        },
                        "q": {
                            "type": "string",
                            "description": "통합 검색어"
                        },
                        "PageSize": {
                            "type": "integer",
                            "description": "페이지 당 결과 수",
                            "default": 20
                        },
                        "Page": {
                            "type": "integer",
                            "description": "페이지 번호",
                            "default": 1
                        },
                    },
                },
            ),
            Tool(
                name="druginfo_get_main_ingredient_by_code",
                description="주성분 코드로 상세 정보를 조회합니다",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "주성분 코드 (9자리)"
                        },
                    },
                    "required": ["code"],
                },
            ),
            Tool(
                name="druginfo_list_product",
                description="의약품 제품 목록을 검색합니다",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pillName": {
                            "type": "string",
                            "description": "의약품 이름 (검색어)"
                        },
                        "q": {
                            "type": "string",
                            "description": "통합 검색어"
                        },
                        "PageSize": {
                            "type": "integer",
                            "description": "페이지 당 결과 수",
                            "default": 20
                        },
                        "Page": {
                            "type": "integer",
                            "description": "페이지 번호",
                            "default": 1
                        },
                    },
                },
            ),
            Tool(
                name="druginfo_get_product_by_code",
                description="제품 코드로 상세 정보를 조회합니다 (korange 필드 포함)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "제품 코드 (ProductCode, 15자리)"
                        },
                    },
                    "required": ["code"],
                },
            ),
            Tool(
                name="druginfo_list_product_edicode_same_ingredient",
                description="동일 성분 의약품을 검색합니다 (토큰 효율적)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ProductCode": {
                            "type": "string",
                            "description": "기준 제품 코드"
                        },
                        "MasterIngredientCode": {
                            "type": "string",
                            "description": "주성분 코드"
                        },
                        "PageSize": {
                            "type": "integer",
                            "description": "페이지 당 결과 수",
                            "default": 20
                        },
                    },
                },
            ),
            Tool(
                name="druginfo_list_product_edicode",
                description="EDI 코드로 제품을 검색합니다",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "EdiCode": {
                            "type": "string",
                            "description": "EDI 코드 (9자리 보험코드)"
                        },
                        "PageSize": {
                            "type": "integer",
                            "description": "페이지 당 결과 수",
                            "default": 20
                        },
                    },
                },
            ),
        ]
        return tools

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """도구 실행"""
        logger.info(f"도구 실행: {name}, 인자: {arguments}")

        try:
            # 로그인 도구
            if name == "login":
                token = await auth_manager.login(
                    arguments.get("userId"),
                    arguments.get("password"),
                    arguments.get("force", False)
                )
                return [{"type": "text", "text": f"로그인 성공. 토큰: {token[:20]}..."}]

            # 주성분 검색
            elif name == "druginfo_list_main_ingredient":
                try:
                    result = list_main_ingredient(**arguments)
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    result = list_main_ingredient(**arguments)
                return [{"type": "text", "text": str(result)}]

            # 주성분 상세
            elif name == "druginfo_get_main_ingredient_by_code":
                try:
                    result = get_main_ingredient_by_code(arguments["code"])
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    result = get_main_ingredient_by_code(arguments["code"])
                return [{"type": "text", "text": str(result)}]

            # 제품 검색
            elif name == "druginfo_list_product":
                try:
                    result = list_product(**arguments)
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    result = list_product(**arguments)
                return [{"type": "text", "text": str(result)}]

            # 제품 상세
            elif name == "druginfo_get_product_by_code":
                try:
                    result = get_product_by_code(arguments["code"])
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    result = get_product_by_code(arguments["code"])
                return [{"type": "text", "text": str(result)}]

            # 동일 성분 검색
            elif name == "druginfo_list_product_edicode_same_ingredient":
                try:
                    result = list_product_edicode_same_ingredient(**arguments)
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    result = list_product_edicode_same_ingredient(**arguments)
                return [{"type": "text", "text": str(result)}]

            # EDI 코드 검색
            elif name == "druginfo_list_product_edicode":
                try:
                    result = list_product_edicode(**arguments)
                except UnauthorizedError:
                    await auth_manager.auto_login()
                    result = list_product_edicode(**arguments)
                return [{"type": "text", "text": str(result)}]

            else:
                raise ValueError(f"알 수 없는 도구: {name}")

        except DrugInfoError as e:
            logger.error(f"DrugInfo 오류: {e}")
            return [{"type": "text", "text": f"오류: {str(e)}"}]
        except Exception as e:
            logger.error(f"도구 실행 오류: {e}")
            return [{"type": "text", "text": f"도구 실행 중 오류 발생: {str(e)}"}]
"""
프롬프트 핸들러 - 시스템 프롬프트를 메타데이터와 함께 제공
"""

import logging
from typing import List, Optional

from mcp.server import Server
from mcp.types import (
    Prompt,
    PromptMessage,
    PromptArgument,
    GetPromptResult,
    TextContent,
)

logger = logging.getLogger(__name__)


def setup_prompt_handlers(server: Server):
    """프롬프트 핸들러 설정"""

    @server.list_prompts()
    async def handle_list_prompts() -> List[Prompt]:
        """사용 가능한 프롬프트 목록 반환"""
        prompts = [
            Prompt(
                name="druginfo_usage_guide",
                description="DrugInfo MCP 도구 사용 가이드라인 - 토큰 최적화와 효율적인 검색 전략",
                arguments=[],
            ),
            Prompt(
                name="query_patterns",
                description="자주 사용하는 쿼리 패턴과 워크플로우",
                arguments=[],
            ),
            Prompt(
                name="search_product",
                description="의약품 검색 워크플로우 - 제품명으로 검색 후 상세 정보 조회",
                arguments=[
                    PromptArgument(
                        name="product_name",
                        description="검색할 의약품 이름",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name="find_bioequivalent",
                description="생물학적동등성 의약품 검색 가이드",
                arguments=[
                    PromptArgument(
                        name="ingredient_code",
                        description="주성분 코드 (선택)",
                        required=False,
                    ),
                ],
            ),
        ]
        return prompts

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: Optional[dict] = None
    ) -> GetPromptResult:
        """프롬프트 내용 반환"""
        logger.info(f"프롬프트 요청: {name}, 인자: {arguments}")

        if name == "druginfo_usage_guide":
            messages = [
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text="""DrugInfo MCP 도구 사용 가이드라인:

1. 토큰 최적화 원칙:
   - 범용 검색(druginfo_list_product) 대신 전용 도구 우선 사용
   - 동일 성분 검색 시: druginfo_list_product_edicode_same_ingredient 사용
   - PageSize는 필요한 만큼만 설정 (기본 20, 탐색용은 1-5)
   - 결과가 많을 때는 응답을 요약하여 필요 필드만 출력

2. 효율적인 검색 전략:
   - 주성분코드/EDI코드/제품코드가 있으면 바로 활용
   - 단계적 접근: 1) 대표 제품 1건 조회 → 2) 동일성분군 조회
   - 생동PK 필터링은 응답 후 korange.생동PK 필드로 로컬 처리

3. 도구별 사용법:
   - login: 환경변수 설정 시 인자 생략 가능, force=true로 중복로그인 해결
   - druginfo_list_main_ingredient: 주성분 검색, ingredientNameKor 또는 q 사용
   - druginfo_list_product: 제품 검색, pillName 또는 q 사용
   - druginfo_list_product_edicode_same_ingredient: 동일성분 검색 (토큰 절약)
   - druginfo_get_*_by_code: 상세 조회, code 필수

4. 응답 처리:
   - korange 필드: 생물학적동등성 정보 (생동PK, 제네릭, 공공대조약 등)
   - 생동PK 값: "True"/"False" 문자열로 반환
   - 에러 시 UnauthorizedError는 자동 재로그인 처리됨""",
                    ),
                ),
            ]
            return GetPromptResult(
                description="DrugInfo MCP 도구 사용을 위한 가이드라인",
                messages=messages,
            )

        elif name == "query_patterns":
            messages = [
                PromptMessage(
                    role="system",
                    content=TextContent(
                        type="text",
                        text="""자주 사용하는 쿼리 패턴:

1. 동일 성분 + 생동PK=True 검색:
   druginfo_list_product_edicode_same_ingredient(MasterIngredientCode="553304ATD")
   → 응답에서 korange.생동PK가 "True"인 항목만 필터링

2. 제품명으로 ProductCode 찾기 및 상세 정보 조회:
   // Step 1: 의약품 이름으로 ProductCode 찾기
   druginfo_list_product(pillName="타이레놀", PageSize=5)
   → items[].productCode 중에서 원하는 제품 선택

   // Step 2: ProductCode로 상세 정보 조회
   druginfo_get_product_by_code(code="선택한_ProductCode")
   → 제품의 상세 정보, korange 필드, 이미지 정보 등 제공

3. 주성분 정보 조회:
   druginfo_list_main_ingredient(ingredientNameKor="실데나필", PageSize=10)

4. EDI 코드 기반 검색:
   druginfo_list_product_edicode(EdiCode="640905240")

5. 생물학적동등성(korange) 필드 해석:
   - 생동PK: "True"/"False" - PK 생동성시험 완료 여부
   - 제네릭: "True"/"False" - 제네릭 의약품 여부
   - 공공대조약: "True"/"False" - 공공 대조약품 여부
   - 특허: "True"/"False" - 특허 보호 여부""",
                    ),
                ),
            ]
            return GetPromptResult(
                description="자주 사용하는 DrugInfo API 쿼리 패턴",
                messages=messages,
            )

        elif name == "search_product":
            product_name = arguments.get("product_name", "타이레놀") if arguments else "타이레놀"
            messages = [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"{product_name} 정보를 알려주세요.",
                    ),
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        type="text",
                        text=f"""{product_name} 검색을 위한 워크플로우:

1. 먼저 제품 목록을 검색합니다:
   druginfo_list_product(pillName="{product_name}", PageSize=5)

2. 검색 결과에서 원하는 제품의 ProductCode를 선택합니다.

3. 선택한 ProductCode로 상세 정보를 조회합니다:
   druginfo_get_product_by_code(code="선택한_ProductCode")

4. 필요시 동일 성분 의약품을 검색합니다:
   druginfo_list_product_edicode_same_ingredient(
       ProductCode="선택한_ProductCode",
       MasterIngredientCode="주성분코드"
   )

이 과정을 통해 제품명, 제조사, 성분, 용량, 생동성 정보, 이미지 등을 종합적으로 제공할 수 있습니다.""",
                    ),
                ),
            ]
            return GetPromptResult(
                description=f"{product_name} 검색 워크플로우",
                messages=messages,
            )

        elif name == "find_bioequivalent":
            ingredient_code = arguments.get("ingredient_code") if arguments else None

            if ingredient_code:
                content = f"""주성분코드 {ingredient_code}의 생물학적동등성 의약품 검색:

1. 동일 성분 의약품 목록 조회:
   druginfo_list_product_edicode_same_ingredient(
       MasterIngredientCode="{ingredient_code}",
       PageSize=50
   )

2. 응답에서 korange.생동PK == "True" 필터링:
   - 생동PK가 "True"인 제품만 선택
   - 제네릭 여부도 함께 확인 (korange.제네릭)

3. 필요시 각 제품의 상세 정보 조회:
   druginfo_get_product_by_code(code="ProductCode")"""
            else:
                content = """생물학적동등성 의약품 검색 가이드:

1. 먼저 기준 의약품을 검색합니다:
   druginfo_list_product(pillName="의약품명", PageSize=5)

2. 기준 의약품의 주성분코드를 확인합니다:
   druginfo_get_product_by_code(code="ProductCode")
   → masterIngredientCode 필드 확인

3. 동일 성분 의약품을 검색합니다:
   druginfo_list_product_edicode_same_ingredient(
       MasterIngredientCode="주성분코드",
       PageSize=50
   )

4. korange.생동PK == "True" 필터링:
   - PK 생동성시험이 완료된 제품만 선택
   - 제네릭 의약품 여부도 확인

5. 생동성 정보 해석:
   - 생동PK: 약물동태학 생동성시험 완료
   - 제네릭: 제네릭 의약품 여부
   - 공공대조약: 생동성 시험의 대조약품"""

            messages = [
                PromptMessage(
                    role="system",
                    content=TextContent(type="text", text=content),
                ),
            ]
            return GetPromptResult(
                description="생물학적동등성 의약품 검색 가이드",
                messages=messages,
            )

        else:
            raise ValueError(f"알 수 없는 프롬프트: {name}")
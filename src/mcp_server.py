import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.mcp_tools import (
    register_auth_tools,
    register_druginfo_tools,
)


# Load env once
load_dotenv(".env", override=False)
load_dotenv(".env.local", override=False)


def register_system_prompts(mcp: FastMCP) -> None:
    """DrugInfo MCP 도구 사용 가이드라인을 시스템 프롬프트로 등록"""
    @mcp.prompt()
    def druginfo_tool_usage_guide() -> str:
        """DrugInfo MCP 도구 사용 가이드라인"""
        return """
DrugInfo MCP 도구 사용 가이드라인:

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
   - 생동PK 값: "True"/"False" 또는 "1"/"0" 문자열로 반환
   - 에러 시 UnauthorizedError는 자동 재로그인 처리됨

5. 환경 설정:
   - .env.local에 EDB_BASE_URL, EDB_LOGIN_URL, EDB_USER_ID, EDB_PASSWORD 설정
   - 서버 시작 시 자동 로그인되어 토큰 캐시됨
   - timeout 기본값 15초, 필요시 조정
        """

    @mcp.prompt()
    def druginfo_common_queries() -> str:
        """DrugInfo 자주 사용하는 쿼리 패턴"""
        return """
DrugInfo 자주 사용하는 쿼리 패턴:

1. 동일 성분 + 생동PK=True 검색:
   ```
   druginfo_list_product_edicode_same_ingredient({
     "MasterIngredientCode": "553304ATD"
   })
   → 응답에서 korange.생동PK가 "True"인 항목만 필터링
   ```

2. 제품명으로 빠른 탐색:
   ```
   druginfo_list_product({
     "pillName": "비아그라",
     "PageSize": 1
   })
   → productCode 추출 후 동일성분 검색에 활용
   ```

3. 주성분 정보 조회:
   ```
   druginfo_list_main_ingredient({
     "ingredientNameKor": "실데나필",
     "PageSize": 10
   })
   ```

4. 제품 상세 정보:
   ```
   druginfo_get_product_by_code({
     "code": "E201301617ATB8J"
   })
   → korange 필드에서 생동성 정보 확인
   ```

5. EDI 코드 기반 검색:
   ```
   druginfo_list_product_edicode({
     "EdiCode": "640905240"
   })
   ```
        """


def create_server() -> FastMCP:
    mcp = FastMCP("druginfo-mcp")
    register_system_prompts(mcp)
    register_auth_tools(mcp)
    register_druginfo_tools(mcp)
    return mcp


if __name__ == "__main__":
    create_server().run()



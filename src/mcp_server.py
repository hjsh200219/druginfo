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
   - 의약품 이름 질의 시: pillName으로 검색 → ProductCode 추출 → 상세 정보 제공

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

6. 의약품 코드 체계 이해 (참조: https://edb.atlassian.net/wiki/external/N2U4M2QxM2ZhNjNlNDBjZTlhMzJlNDVjMjEwMTAyYWI):
   - 보험코드(= EdiCode, 9자리): 건강보험심사평가원 부여, 월 1회 업데이트, 코드 변경 가능
   - 표준코드(13자리): 건강보험심사평가원 부여, 매주 업데이트, 코드 변경 가능
   - 품목기준코드(9자리): 식품의약품안전처 부여, 상시 업데이트, 코드 변경 없음
   - 주성분코드(9자리): 매월 업데이트, 동일 성분 의약품은 동일 코드 공유
     * 구조: 주성분일련번호(1-3자리) + 함량일련번호(4-6자리) + 투여경로(7자리: A내복/B주사/C외용/D기타) + 제형(8-9자리)
     * 동일성분 판별: 1-4자리(주성분일련번호)와 7자리(투여경로)가 동일하면 동일성분
   - ATC코드(7자리): WHO 부여, 매년 업데이트
   - DUR성분코드: 실질적 유효성분 기준으로 약 3,200개 코드 개발
   - ProductCode(15자리): 터울 자체 생성 코드 (참조: https://edb.atlassian.net/wiki/external/MmFlOTg2ZDlkNzBiNGZlNGI0MjdjNWY5OWExNzNiYzU)
     * 구조: 의약품구분(1자리) + 품목기준코드(9자리) + 주성분코드마지막3자리(3자리) + 난수(2자리)
     * 의약품구분: E(전문의약품), O(일반의약품), T(터울자체생성)
     * 예시: E201207542ATB7D (카나브정30밀리그램)
       - E: 전문의약품
       - 201207542: 품목기준코드
       - ATB: 주성분코드 마지막 3자리 (투여경로 및 제형)
       - 7D: 구별용 난수
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

2. 제품명으로 ProductCode 찾기 및 상세 정보 조회:
   ```
   // 1단계: 의약품 이름으로 ProductCode 찾기
   druginfo_list_product({
     "pillName": "타이레놀",
     "PageSize": 5
   })
   → items[].productCode 중에서 원하는 제품 선택
   
   // 2단계: ProductCode로 상세 정보 조회
   druginfo_get_product_by_code({
     "code": "선택한_ProductCode"
   })
   → 제품의 상세 정보, korange 필드, 이미지 정보 등 제공
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

6. 생물학적동등성(korange) 필드 해석:
   - 공공대조약: "True"/"False" - 공공 대조약품 여부
   - 제네릭: "True"/"False" - 제네릭 의약품 여부  
   - 생동PK: "True"/"False" - PK(약물동태학) 생동성시험 완료 여부
   - 취하일: 날짜 또는 빈 문자열 - 허가 취하일
   - 특허: "True"/"False" - 특허 보호 여부
   - 함량: 수치+단위 - 주성분 함량 (예: "70.23MG")

7. 주성분코드 구조 이해:
   - 예시: 553304ATD
     * 553: 주성분 일련번호 (실데나필)
     * 304: 함량별 일련번호
     * A: 투여경로 (내복제)
     * TD: 제형 (정제)
   - 동일성분 판별: 앞 4자리(5533)와 7번째 자리(A)가 같으면 동일성분

8. ProductCode 구조 이해:
   - 예시: E201207542ATB7D (카나브정30밀리그램)
     * E: 전문의약품
     * 201207542: 품목기준코드
     * ATB: 주성분코드 마지막 3자리 (투여경로 및 제형)
     * 7D: 구별용 난수 (동일 품목기준코드+투여경로+제형에서 용량 구분용)

9. 의약품 이름 질의 처리 워크플로우:
   - 사용자가 "타이레놀 정보 알려줘" 같은 질문을 하면:
     1) druginfo_list_product로 pillName="타이레놀" 검색 (PageSize=5-10)
     2) 검색 결과에서 적절한 ProductCode 선택 (여러 개면 사용자에게 선택지 제시)
     3) druginfo_get_product_by_code로 선택된 ProductCode의 상세 정보 조회
     4) 제품명, 제조사, 성분, 용량, 생동성 정보, 이미지 등을 종합하여 응답
   - 검색 결과가 많을 때는 vendor, 용량 등으로 추가 필터링 가능
        """


def create_server() -> FastMCP:
    mcp = FastMCP("druginfo-mcp")
    register_system_prompts(mcp)
    register_auth_tools(mcp)
    register_druginfo_tools(mcp)
    return mcp


if __name__ == "__main__":
    create_server().run()



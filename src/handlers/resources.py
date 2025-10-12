"""
리소스 핸들러 - 설정 파일, 문서 등을 리소스로 제공
"""

import logging
from typing import List
from pathlib import Path

from mcp.server import Server
from mcp.types import Resource, ResourceContents, TextResourceContents

logger = logging.getLogger(__name__)


# 리소스 콘텐츠 캐시 (필요할 때만 로드)
_RESOURCE_CACHE = {}


def _get_resource_content(uri: str) -> str:
    """리소스 콘텐츠를 on-demand로 로드"""
    if uri in _RESOURCE_CACHE:
        return _RESOURCE_CACHE[uri]

    contents = {
        "druginfo://config/env-template": """# DrugInfo MCP 환경 설정
# .env.local 파일로 저장하여 사용하세요

# 필수 설정
EDB_BASE_URL=https://dev-adminapi.edbintra.co.kr
# 실서버: https://webconsole-api.edbintra.co.kr
EDB_LOGIN_URL=https://dev-adminapi.edbintra.co.kr/v1/auth/login

# 자동 로그인용 (선택)
EDB_USER_ID=your_email@example.com
EDB_PASSWORD=your_password

# 기타 옵션
EDB_TIMEOUT=15  # API 호출 타임아웃 (초)
EDB_FORCE_LOGIN=false  # 중복 로그인 강제 해제
""",
        "druginfo://docs/code-system": """# 의약품 코드 체계

## ProductCode (15자리)
터울 자체 생성 코드입니다.

구조: `[의약품구분(1)][품목기준코드(9)][주성분코드끝3자리(3)][난수(2)]`

예시: `E201207542ATB7D` (카나브정30밀리그램)
- E: 전문의약품 (O: 일반의약품, T: 터울자체생성)
- 201207542: 품목기준코드
- ATB: 주성분코드 마지막 3자리 (투여경로 및 제형)
- 7D: 구별용 난수

## 주성분코드 (9자리)
구조: `[주성분번호(3)][함량번호(3)][투여경로(1)][제형(2)]`

예시: `553304ATD`
- 553: 주성분 (실데나필)
- 304: 함량
- A: 내복 (B:주사, C:외용, D:기타)
- TD: 정제

동일성분 판별: 앞 4자리 + 7번째 자리 동일

## EDI 코드 (보험코드, 9자리)
건강보험심사평가원에서 부여하는 보험청구용 코드입니다.

## 표준코드 (13자리)
건강보험심사평가원에서 부여하는 표준화된 약품코드입니다.

## 품목기준코드 (9자리)
식품의약품안전처에서 부여하는 의약품 허가 코드입니다.
""",
        "druginfo://docs/query-patterns": """# 자주 사용하는 쿼리 패턴

## 1. 동일 성분 + 생동PK 검색
```python
# 동일 성분 검색
druginfo_list_product_edicode_same_ingredient(
    MasterIngredientCode="553304ATD"
)
# 응답에서 korange.생동PK == "True" 필터링
```

## 2. 제품명으로 상세 정보 조회
```python
# Step 1: 제품 검색
druginfo_list_product(
    pillName="타이레놀",
    PageSize=5
)
# → ProductCode 추출

# Step 2: 상세 정보 조회
druginfo_get_product_by_code(
    code="선택한_ProductCode"
)
```

## 3. 주성분 정보 조회
```python
druginfo_list_main_ingredient(
    ingredientNameKor="실데나필",
    PageSize=10
)
```

## 4. EDI 코드 기반 검색
```python
druginfo_list_product_edicode(
    EdiCode="640905240"
)
```
""",
        "druginfo://docs/korange-fields": """# korange 필드 설명

생물학적동등성 및 제네릭 관련 정보를 담고 있는 필드입니다.

## 주요 필드

### 생동PK
- 타입: "True" / "False" (문자열)
- 의미: PK(약물동태학) 생물학적동등성 시험 완료 여부
- 활용: 제네릭 의약품의 오리지널 대비 동등성 확인

### 제네릭
- 타입: "True" / "False" (문자열)
- 의미: 제네릭 의약품 여부
- 활용: 오리지널/제네릭 구분

### 공공대조약
- 타입: "True" / "False" (문자열)
- 의미: 공공 대조약품 여부
- 활용: 생물학적동등성 시험의 대조약으로 사용

### 특허
- 타입: "True" / "False" (문자열)
- 의미: 특허 보호 여부
- 활용: 특허 만료 확인

### 취하일
- 타입: 날짜 문자열 또는 빈 문자열
- 의미: 허가 취하일
- 활용: 판매 중단 의약품 확인

### 함량
- 타입: 수치+단위 (예: "70.23MG")
- 의미: 주성분 함량
- 활용: 용량 확인
""",
    }

    content = contents.get(uri)
    if content:
        _RESOURCE_CACHE[uri] = content
    return content


def setup_resource_handlers(server: Server, config):
    """리소스 핸들러 설정"""

    @server.list_resources()
    async def handle_list_resources() -> List[Resource]:
        """사용 가능한 리소스 목록 반환 - 메타데이터만"""
        resources = [
            Resource(
                uri="druginfo://config/env-template",
                name="환경 설정 템플릿",
                description=".env.local 파일 템플릿",
                mimeType="text/plain",
            ),
            Resource(
                uri="druginfo://docs/code-system",
                name="의약품 코드 체계",
                description="ProductCode, 주성분코드 등",
                mimeType="text/markdown",
            ),
            Resource(
                uri="druginfo://docs/query-patterns",
                name="쿼리 패턴",
                description="자주 사용하는 API 패턴",
                mimeType="text/markdown",
            ),
            Resource(
                uri="druginfo://docs/korange-fields",
                name="korange 필드",
                description="생동PK 등 필드 설명",
                mimeType="text/markdown",
            ),
        ]
        return resources

    @server.read_resource()
    async def handle_read_resource(uri: str) -> ResourceContents:
        """리소스 내용 읽기 - 요청 시점에 로드"""
        logger.info(f"리소스 읽기: {uri}")

        # 캐시에서 로드 또는 생성
        content = _get_resource_content(uri)
        if not content:
            raise ValueError(f"알 수 없는 리소스 URI: {uri}")

        # MIME 타입 결정
        mime_type = "text/markdown" if uri.startswith("druginfo://docs/") else "text/plain"

        return TextResourceContents(
            uri=uri,
            mimeType=mime_type,
            text=content,
        )
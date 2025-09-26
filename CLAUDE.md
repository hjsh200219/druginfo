# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

의약품 정보 시스템(EDB)을 위한 Python 기반 MCP (Model Context Protocol) 서버입니다. 표준 MCP SDK를 사용하여 의약품 정보 조회 도구, 리소스, 프롬프트를 MCP 클라이언트에 제공합니다.

## 개발 명령어

### 개발 환경 설정
```bash
# 가상 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치 (requests, python-dotenv, mcp)
pip install -r requirements.txt
```

### MCP 서버 실행
```bash
# 표준 MCP 서버 실행
python -m src.server

# 직접 인증 테스트 (CLI)
python -m src.login_jwt --url "$EDB_LOGIN_URL" --userId "ID" --password "PW"

# Bearer 토큰으로 API 호출 테스트
python -m src.login_jwt --get "https://dev-adminapi.edbintra.co.kr/v1/druginfo/product?pillName=타이레놀" --token "TOKEN"
```

### 필수 환경 변수

`.env.local` 파일에 설정 (프로젝트 루트):
```ini
# 필수 설정
EDB_BASE_URL=https://dev-adminapi.edbintra.co.kr  # 또는 실서버: https://webconsole-api.edbintra.co.kr
EDB_LOGIN_URL=https://dev-adminapi.edbintra.co.kr/v1/auth/login

# 자동 로그인용 (선택)
EDB_USER_ID=사용자_이메일
EDB_PASSWORD=비밀번호

# 기타 옵션
EDB_TIMEOUT=15  # API 호출 타임아웃 (초)
EDB_FORCE_LOGIN=false  # 중복 로그인 강제 해제
```

## 코드 아키텍처

### MCP 서버 구조
```
src/
├── server.py              # 표준 MCP 서버 진입점
├── auth.py               # 인증 로직 (토큰 추출, 중복 로그인 처리)
├── login_jwt.py          # CLI 유틸리티 (직접 테스트용)
├── handlers/
│   ├── __init__.py       # 핸들러 모듈
│   ├── tools.py          # 도구 핸들러 (druginfo_* 도구들)
│   ├── resources.py      # 리소스 핸들러 (설정, 문서)
│   └── prompts.py        # 프롬프트 핸들러 (시스템 프롬프트)
├── auth/
│   ├── __init__.py
│   └── manager.py        # 인증 관리자 (토큰 관리, 자동 로그인)
├── utils/
│   ├── __init__.py
│   └── config.py         # 환경 설정 관리
├── mcp_tools/            # 기존 도구 (호환성 유지)
│   ├── auth_tools.py
│   └── druginfo_tools.py
└── druginfo/
    ├── client.py         # API 클라이언트 (HTTP 요청 처리)
    └── __init__.py       # druginfo 함수들 export
```

### 핵심 아키텍처 패턴

1. **자동 인증 재시도 패턴**:
   - 모든 druginfo 도구는 UnauthorizedError(401) 발생 시 자동으로 `_try_auto_login()` 호출
   - 재로그인 후 동일 요청 재시도 (1회)
   - 토큰은 전역 변수 `_AUTO_TOKEN`과 환경 변수 `EDB_TOKEN`에 캐시

2. **중복 로그인 처리**:
   - `auth.py`의 `_is_duplicate_login_error()`가 응답 분석
   - resultCode "4100" 또는 "중복로그인" 메시지 감지
   - 자동으로 force=true로 재시도

3. **토큰 추출 로직** (`extract_token()`):
   - 다양한 응답 형식 지원 (accessToken, access_token, token, jwt 등)
   - 중첩된 JSON 구조 재귀 탐색 (data, result, payload 필드)

4. **환경 변수 우선순위**:
   - `.env.local` > `.env` > 시스템 환경 변수
   - `EDB_BASE_URL` 없으면 `EDB_LOGIN_URL`에서 호스트 추출

5. **모듈 import 호환성 처리**:
   - 표준 import 시도 후 실패 시 sys.path 추가
   - Claude Desktop의 경로 문제 해결

## 의약품 정보 도구 사용 가이드

### 효율적인 검색 전략
1. **제품 검색 워크플로우**:
   ```python
   # Step 1: 제품명으로 검색
   druginfo_list_product(pillName="타이레놀", PageSize=5)
   # → ProductCode 추출

   # Step 2: 상세 정보 조회
   druginfo_get_product_by_code(code="추출한_ProductCode")
   # → 성분, korange 필드, 이미지 등 확인
   ```

2. **동일 성분 의약품 검색**:
   ```python
   # 토큰 효율적인 전용 도구 사용
   druginfo_list_product_edicode_same_ingredient(
       ProductCode="기준제품코드",
       MasterIngredientCode="주성분코드"
   )
   ```

3. **생물학적동등성(생동) 필터링**:
   - API에서 직접 필터링 불가
   - 응답 후 `korange.생동PK == "True"` 로컬 필터링

### 의약품 코드 체계

**ProductCode (15자리)** - 터울 자체 생성 코드:
- 구조: `[의약품구분(1)][품목기준코드(9)][주성분코드끝3자리(3)][난수(2)]`
- 예시: `E201207542ATB7D`
  - E: 전문의약품 (O: 일반, T: 터울자체)
  - 201207542: 품목기준코드
  - ATB: 주성분 투여경로+제형
  - 7D: 구별용 난수

**주성분코드 (9자리)**:
- 구조: `[주성분번호(3)][함량번호(3)][투여경로(1)][제형(2)]`
- 예시: `553304ATD`
  - 553: 주성분 (실데나필)
  - 304: 함량
  - A: 내복 (B:주사, C:외용, D:기타)
  - TD: 정제
- 동일성분 판별: 앞 4자리 + 7번째 자리 동일

**korange 필드 해석**:
- `생동PK`: "True"/"False" - PK 생동성시험 완료
- `제네릭`: "True"/"False" - 제네릭 의약품
- `공공대조약`: "True"/"False" - 공공 대조약품
- `특허`: "True"/"False" - 특허 보호 여부

## MCP 기능

### 도구 (Tools)
- `login`: EDB 시스템 로그인
- `druginfo_list_main_ingredient`: 주성분 목록 검색
- `druginfo_get_main_ingredient_by_code`: 주성분 상세 조회
- `druginfo_list_product`: 제품 목록 검색
- `druginfo_get_product_by_code`: 제품 상세 조회
- `druginfo_list_product_edicode_same_ingredient`: 동일 성분 검색
- `druginfo_list_product_edicode`: EDI 코드 검색

### 리소스 (Resources)
- `druginfo://config/env-template`: 환경 설정 템플릿
- `druginfo://docs/code-system`: 의약품 코드 체계 문서
- `druginfo://docs/query-patterns`: 자주 사용하는 쿼리 패턴
- `druginfo://docs/korange-fields`: korange 필드 설명

### 프롬프트 (Prompts)
- `druginfo_usage_guide`: 도구 사용 가이드라인
- `query_patterns`: 자주 사용하는 쿼리 패턴
- `search_product`: 제품 검색 워크플로우
- `find_bioequivalent`: 생물학적동등성 검색 가이드


## 🔴 중요 규칙

### 언어 설정
- 답변은 한글로 작성

### 토큰 최적화
- PageSize는 필요한 만큼만 (기본 20, 탐색용 1-5)
- 범용 도구보다 전용 도구 우선 사용
- 응답 요약하여 필요 필드만 출력
# DrugInfo MCP - Architecture Patterns (Reference)

> CLAUDE.md 및 root ARCHITECTURE.md에서 분리된 상세 패턴 문서

## 핵심 아키텍처 패턴

### 1. 자동 인증 재시도 패턴
- 모든 druginfo 도구는 UnauthorizedError(401) 발생 시 자동으로 `_try_auto_login()` 호출
- 재로그인 후 동일 요청 재시도 (1회)
- 토큰은 전역 변수 `_AUTO_TOKEN`과 환경 변수 `EDB_TOKEN`에 캐시

### 2. 중복 로그인 처리
- `auth/login.py`의 `_is_duplicate_login_error()`가 응답 분석
- resultCode "4100" 또는 "중복로그인" 메시지 감지
- 자동으로 force=true로 재시도

### 3. 토큰 추출 로직 (`extract_token()`)
- 다양한 응답 형식 지원 (accessToken, access_token, token, jwt 등)
- 중첩된 JSON 구조 재귀 탐색 (data, result, payload 필드)

### 4. 환경 변수 우선순위
- `.env.local` > `.env` > 시스템 환경 변수
- `EDB_BASE_URL` 없으면 `EDB_LOGIN_URL`에서 호스트 추출

### 5. 모듈 import 호환성 처리
- 표준 import 시도 후 실패 시 sys.path 추가
- Claude Desktop의 경로 문제 해결

## MCP 서버 구조 (상세)

```
src/
├── server.py              # 표준 MCP 서버 진입점
├── mcp_server.py          # FastMCP 서버 진입점
├── login_jwt.py           # CLI 유틸리티 (직접 테스트용)
├── handlers/
│   ├── __init__.py        # 핸들러 모듈
│   ├── tools.py           # 도구 핸들러 (search_druginfo 등)
│   ├── resources.py       # 리소스 핸들러 (설정, 문서)
│   └── prompts.py         # 프롬프트 핸들러 (시스템 프롬프트)
├── auth/
│   ├── __init__.py
│   ├── login.py           # 로그인 및 토큰 추출
│   └── manager.py         # 인증 관리자 (토큰 관리, 자동 로그인)
├── utils/
│   ├── __init__.py
│   └── config.py          # 환경 설정 관리
├── mcp_tools/             # FastMCP 도구 등록 (호환성 유지)
│   ├── auth_tools.py
│   └── druginfo_tools.py
└── druginfo/
    ├── client.py          # API 클라이언트 (HTTP 요청 처리)
    ├── response_filters.py # 응답 토큰 최적화 필터
    └── __init__.py        # druginfo 함수들 export
```

## 확장 가이드

### 새로운 도구 추가
1. **DrugInfo API 클라이언트 확장** (`src/druginfo/client.py`)
2. **도구 등록 파일 수정** (`src/mcp_tools/druginfo_tools.py`)
3. **핸들러에서 도구 등록** (`src/handlers/tools.py`)

### 새로운 프롬프트 추가
1. **프롬프트 핸들러 수정** (`src/handlers/prompts.py`)
2. `list_prompts()`에 프롬프트 추가
3. `get_prompt()`에 프롬프트 내용 추가

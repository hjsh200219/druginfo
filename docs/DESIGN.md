# DrugInfo MCP - Design Patterns

## API 설계 패턴

### 1. Dual Entry Point Pattern

두 개의 서버 진입점이 동일한 비즈니스 로직을 공유:

```
server.py (Standard MCP SDK)         mcp_server.py (FastMCP)
    |                                      |
    v                                      v
handlers/ (on-demand schema)         mcp_tools/ (decorator 등록)
    |                                      |
    +-----------> druginfo/ <--------------+
                     |
                     v
              EDB Admin API
```

- **server.py 경로**: 세밀한 MCP 프로토콜 제어, on-demand 스키마 로딩
- **mcp_server.py 경로**: FastMCP 데코레이터 기반 간편 등록, response compaction 적용

### 2. Auto-Retry Authentication Pattern

모든 API 도구에 적용되는 인증 재시도 패턴:

```python
try:
    result = api_call(...)
except UnauthorizedError:
    _try_auto_login(timeout)       # 재로그인
    result = api_call(...)         # 1회 재시도
except DrugInfoError as e:
    raise RuntimeError(str(e))     # 에러 전파
```

### 3. Response Compaction Pattern

`response_filters.py`가 토큰 효율적 응답을 생성:

```python
def _safe_compact(compactor, payload):
    try:
        compacted = compactor(payload)
        return compacted if compacted is not None else payload
    except Exception:
        return payload  # fallback: 원본 반환
```

핵심 필터:
- `compact_main_ingredient_list/detail`: 주성분 정보 압축
- `compact_product_list/detail`: 제품 정보 압축
- `compact_same_ingredient_list`: 동일 성분 목록 압축

### 4. Token Extraction Pattern

다양한 JWT 응답 형식을 재귀적으로 탐색:

```python
def extract_token(data):
    # accessToken, access_token, token, jwt, id_token 등 탐색
    # data, result, payload 등 중첩 구조 재귀 탐색
```

### 5. On-Demand Schema Loading (server.py)

`list_tools()`에서는 최소 스키마(`{"type": "object"}`) 반환. `call_tool()` 시점에 상세 스키마를 로드하여 디스커버리 비용 절감.

## 확장 가이드

### 새 API 엔드포인트 추가

1. `src/druginfo/client.py`에 API 호출 함수 추가
2. `src/druginfo/response_filters.py`에 응답 압축 함수 추가
3. `src/mcp_tools/druginfo_tools.py`에 FastMCP 도구 등록
4. `src/handlers/tools.py`에 Standard MCP 핸들러 추가
5. `docs/references/druginfo-tools-guide.md` 업데이트

### 새 MCP 리소스 추가

1. `src/handlers/resources.py`의 `_get_resource_content()`에 콘텐츠 추가
2. `handle_list_resources()`에 Resource 메타데이터 추가

### 새 MCP 프롬프트 추가

1. `src/handlers/prompts.py`의 `handle_get_prompt()`에 콘텐츠 추가
2. `handle_list_prompts()`에 Prompt 메타데이터 추가
3. `src/mcp_server.py`의 `register_system_prompts()`에 FastMCP 프롬프트 추가

# DrugInfo MCP - Architecture

## Domain Map

```
druginfo/
  Domain: 의약품 정보 조회 MCP 서버
  External API: EDB Admin API (dev / prod)
  Protocol: MCP (Model Context Protocol) over stdio
```

## Layer Structure

```
┌─────────────────────────────────────────────────────┐
│  Entry Points                                        │
│  server.py (Standard MCP SDK)                       │
│  mcp_server.py (FastMCP)                            │
├─────────────────────────────────────────────────────┤
│  Handler Layer                   src/handlers/       │
│  tools.py   resources.py   prompts.py               │
├─────────────────────────────────────────────────────┤
│  Tool Registration Layer         src/mcp_tools/      │
│  auth_tools.py   druginfo_tools.py                  │
├─────────────────────────────────────────────────────┤
│  Business Logic Layer            src/druginfo/       │
│  client.py   response_filters.py                    │
├─────────────────────────────────────────────────────┤
│  Auth Layer                      src/auth/           │
│  login.py   manager.py                              │
├─────────────────────────────────────────────────────┤
│  Utility Layer                   src/utils/          │
│  config.py                                          │
└─────────────────────────────────────────────────────┘
         │
         ▼
  External: EDB Admin API (REST/JSON)
```

## Dependency Directions (Top-Down Only)

```
Entry Points
  ├──► Handler Layer
  │     ├──► Tool Registration (mcp_tools/)
  │     │     ├──► Business Logic (druginfo/)
  │     │     └──► Auth (auth/)
  │     ├──► Business Logic (druginfo/)
  │     └──► Auth (auth/manager.py)
  ├──► Auth Layer
  └──► Utility Layer (config.py)

Business Logic ──► Utility (env vars only, no import)
Auth Layer ──► Utility (env vars only, no import)
```

## Dual Entry Point Architecture

이 프로젝트는 두 개의 서버 진입점을 유지합니다:

| Entry Point | SDK | 용도 |
|---|---|---|
| `src/server.py` | Standard MCP SDK (`mcp.server.Server`) | 세밀한 제어, 프로덕션 |
| `src/mcp_server.py` | FastMCP (`mcp.server.fastmcp.FastMCP`) | 간편 등록, Claude Desktop |

- `server.py` 경로: Server -> handlers/ -> druginfo/ (on-demand schema)
- `mcp_server.py` 경로: FastMCP -> mcp_tools/ -> druginfo/ (response_filters 적용)

## Key Patterns

### 1. Auto-Retry Authentication
모든 API 호출에서 `UnauthorizedError(401)` 발생 시:
1. `_try_auto_login()` / `auth_manager.auto_login()` 호출
2. 새 토큰을 `os.environ["EDB_TOKEN"]`에 캐시
3. 동일 요청 1회 재시도

### 2. Duplicate Login Handling
`resultCode "4100"` 또는 `"중복로그인"` 감지 시 `force=true`로 재로그인

### 3. On-Demand Schema Loading (server.py)
`list_tools()`에서는 최소 스키마 반환, `call_tool()` 시점에 상세 스키마 로드

### 4. Response Compaction (mcp_server.py)
`response_filters.py`가 API 응답을 토큰 효율적 형태로 압축

### 5. Token Extraction
재귀적으로 `accessToken`, `access_token`, `token`, `jwt` 등의 키를 탐색

## Data Flow

```
MCP Client (Claude Desktop / Agent)
    │ stdio
    ▼
MCP Server (server.py / mcp_server.py)
    │
    ▼
Handler / Tool Registration
    │
    ▼
druginfo/client.py ──HTTP GET──► EDB Admin API
    │                               │
    ▼                               ▼
response_filters.py            JSON Response
    │
    ▼
Compacted JSON → MCP Client
```

## Module Inventory

| Module | Files | Responsibility |
|---|---|---|
| Entry | `server.py`, `mcp_server.py` | 서버 초기화 및 실행 |
| Handlers | `handlers/tools.py`, `resources.py`, `prompts.py` | MCP 프로토콜 요청 처리 |
| MCP Tools | `mcp_tools/auth_tools.py`, `druginfo_tools.py` | FastMCP 도구 등록 |
| DrugInfo | `druginfo/client.py`, `response_filters.py` | API 호출 및 응답 압축 |
| Auth | `auth/login.py`, `auth/manager.py` | JWT 토큰 관리 |
| Utils | `utils/config.py` | 환경 설정 관리 |

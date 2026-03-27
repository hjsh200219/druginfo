# DrugInfo MCP - Architecture

## Overview

Python MCP 서버로, EDB Admin API의 의약품 정보를 MCP 프로토콜(stdio)을 통해 AI 에이전트에 제공합니다.

| Attribute | Value |
|---|---|
| Language | Python 3.9+ |
| Protocol | MCP over stdio |
| SDK | MCP SDK (Standard + FastMCP) |
| External API | EDB Admin API (REST/JSON) |
| Auth | JWT (auto-retry on 401) |
| Dependencies | requests, python-dotenv, mcp, pydantic |

## Directory Structure

```
druginfo/
├── src/
│   ├── server.py              # Standard MCP SDK 진입점
│   ├── mcp_server.py          # FastMCP 진입점 (Claude Desktop)
│   ├── login_jwt.py           # CLI 유틸리티
│   ├── handlers/              # MCP 프로토콜 핸들러 (Standard SDK)
│   │   ├── tools.py           # 도구 핸들러 (search, detail, same_ingredient)
│   │   ├── resources.py       # 리소스 핸들러 (설정, 문서)
│   │   └── prompts.py         # 프롬프트 핸들러 (시스템 프롬프트)
│   ├── mcp_tools/             # FastMCP 도구 등록
│   │   ├── auth_tools.py      # login 도구 + _try_auto_login
│   │   └── druginfo_tools.py  # DrugInfo 13개 도구 (response compaction)
│   ├── druginfo/              # 비즈니스 로직
│   │   ├── client.py          # EDB API 호출 (HTTP GET)
│   │   └── response_filters.py # 응답 토큰 최적화 필터
│   ├── auth/                  # 인증 모듈
│   │   ├── login.py           # 로그인 + 토큰 추출
│   │   └── manager.py         # AuthManager (토큰 관리)
│   └── utils/
│       └── config.py          # 환경 설정 관리
├── docs/                      # 문서
├── requirements.txt
├── mcp.json                   # MCP 매니페스트
└── .env.local                 # 로컬 환경 변수 (gitignored)
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

역방향 import 금지. 상세 규칙: [docs/design-docs/layer-rules.md](docs/design-docs/layer-rules.md)

## Dual Entry Point Architecture

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

### 2. Response Compaction
`response_filters.py`가 API 응답을 토큰 효율적 형태로 압축. `_safe_compact()`로 실패 시 원본 반환.

### 3. On-Demand Schema Loading
`list_tools()`에서는 최소 스키마 반환, `call_tool()` 시점에 상세 스키마 로드.

### 4. Token Extraction
재귀적으로 `accessToken`, `access_token`, `token`, `jwt` 등의 키를 탐색.

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

## MCP Capabilities

- **Tools**: login, search_druginfo, get_druginfo_detail, find_same_ingredient + 9개 세부 도구
- **Resources**: env-template, code-system, query-patterns, korange-fields
- **Prompts**: druginfo_usage_guide, query_patterns, search_product, find_bioequivalent

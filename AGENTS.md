# agent.md

의약품 정보 시스템(EDB)을 위한 Python MCP 서버. 의약품 정보 조회 도구를 MCP 클라이언트에 제공.

> 전체 에이전트 네비게이션: [AGENTS.md](AGENTS.md)

## Tech Stack
- Python 3.9+, MCP SDK (standard + FastMCP), requests, python-dotenv, pydantic
- Protocol: MCP over stdio
- External API: EDB Admin API (REST/JSON)

## Commands
```bash
# 개발 환경
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 서버 실행
python -m src.server        # Standard MCP SDK
python -m src.mcp_server    # FastMCP (Claude Desktop용)

# CLI 테스트
python -m src.login_jwt --url "$EDB_LOGIN_URL" --userId "ID" --password "PW"
```

## Environment (.env.local)
```ini
EDB_BASE_URL=https://dev-adminapi.edbintra.co.kr
EDB_LOGIN_URL=https://dev-adminapi.edbintra.co.kr/v1/auth/login
EDB_USER_ID=사용자_이메일    # 선택 (자동 로그인용)
EDB_PASSWORD=비밀번호        # 선택
EDB_TIMEOUT=15              # 선택
EDB_FORCE_LOGIN=false       # 선택
```

## Architecture (Quick View)
```
Entry Points → Handlers/Tools → DrugInfo Client → EDB API
                                  ↳ Auth (auto-retry on 401)
```
- `src/server.py`: Standard MCP SDK 진입점 (on-demand schema)
- `src/mcp_server.py`: FastMCP 진입점 (response compaction)
- `src/handlers/`: MCP 프로토콜 핸들러 (tools, resources, prompts)
- `src/mcp_tools/`: FastMCP 도구 등록 (auth, druginfo)
- `src/druginfo/`: API 클라이언트 + 응답 필터
- `src/auth/`: JWT 토큰 관리
- `src/utils/`: 환경 설정

> 상세: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Core Invariants
1. **Import 방향**: Entry → Handlers → Business Logic → Auth → Utils (역방향 금지)
2. **API 호출**: 반드시 `druginfo/client.py` 경유 (직접 requests 금지)
3. **인증 재시도**: 401 발생 시 auto_login() 후 1회 재시도 패턴 준수
4. **토큰 저장**: `os.environ["EDB_TOKEN"]`에 캐시
5. **에러 전파**: DrugInfoError → RuntimeError → MCP 응답

> 상세 규칙: [docs/design-docs/layer-rules.md](docs/design-docs/layer-rules.md)

## Key Tools
| Tool | 용도 |
|---|---|
| `login` | EDB 로그인 |
| `search_druginfo` | 통합 검색 (주성분/제품) |
| `get_druginfo_detail` | 상세 조회 (코드 기반) |
| `find_same_ingredient` | 동일 성분 검색 |

> 전체 도구 목록: [docs/references/druginfo-tools-guide.md](docs/references/druginfo-tools-guide.md)

## Search Strategy
1. 제품명으로 검색 → ProductCode 추출 → 상세 조회
2. 동일 성분은 전용 도구 사용 (토큰 절약)
3. 생동PK 필터링: 응답 후 `korange.생동PK == "True"` 로컬 처리
4. PageSize는 필요한 만큼만 (기본 20, 탐색용 1-5)

## Knowledge Base (docs/)
```
docs/
├── ARCHITECTURE.md              # 레이어 구조, 의존성, 데이터 흐름
├── DESIGN.md                    # API 설계 패턴 및 확장 가이드
├── FRONTEND.md                  # N/A (백엔드 전용)
├── PLANS.md                     # 로드맵 및 개선 계획
├── PRODUCT_SENSE.md             # 제품 컨텍스트 및 사용 시나리오
├── QUALITY.md                   # 도메인별 품질 점수표 (legacy)
├── QUALITY_SCORE.md             # 도메인별 품질 점수표
├── RELIABILITY.md               # 안정성 기준 및 장애 대응
├── SECURITY.md                  # 인증, 토큰 관리, 보안
├── design-docs/
│   ├── index.md
│   ├── core-beliefs.md          # 핵심 설계 원칙
│   └── layer-rules.md          # import/의존성 린트 규칙
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md    # 기술 부채 추적
├── generated/
│   └── db-schema.md            # API 응답 스키마
├── product-specs/
│   └── index.md
└── references/
    ├── druginfo-tools-guide.md  # 도구 상세 가이드
    └── architecture-patterns.md # 아키텍처 패턴 상세
```

## Rules
- 답변은 한글로 작성
- 범용 도구보다 전용 도구 우선 사용
- 응답 요약하여 필요 필드만 출력
- 기존 파일 삭제 금지, 기존 패턴 존중


---

# AGENTS.md - DrugInfo MCP Server

## Project Identity

DrugInfo MCP Server: EDB 의약품 정보 API를 MCP 프로토콜로 노출하는 Python 서버.
주성분/제품/EDI코드/생동성 정보를 Claude Desktop 및 MCP 호환 클라이언트에서 조회.

## Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python -m src.mcp_server  # FastMCP (Claude Desktop)
python -m src.server       # Standard MCP SDK
```

## Agent Entry Points

### Primary Instructions
- [agent.md](agent.md) (= CLAUDE.md) -- 코어 규칙, 명령어, 아키텍처 요약

### Architecture & Design
- [ARCHITECTURE.md](ARCHITECTURE.md) -- 전체 아키텍처, 레이어 구조, 데이터 흐름
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) -- 상세 레이어 구조 및 모듈 인벤토리
- [docs/design-docs/index.md](docs/design-docs/index.md) -- 설계 문서 목차
- [docs/design-docs/core-beliefs.md](docs/design-docs/core-beliefs.md) -- 핵심 설계 원칙
- [docs/design-docs/layer-rules.md](docs/design-docs/layer-rules.md) -- import/의존성 규칙

### Quality & Reliability
- [docs/QUALITY_SCORE.md](docs/QUALITY_SCORE.md) -- 도메인별 품질 점수
- [docs/RELIABILITY.md](docs/RELIABILITY.md) -- SLO, 장애 모드, 복구 절차
- [docs/SECURITY.md](docs/SECURITY.md) -- 인증, 토큰 관리, 환경 변수 보안

### Product & Planning
- [docs/PRODUCT_SENSE.md](docs/PRODUCT_SENSE.md) -- 제품 컨텍스트 및 사용자 워크플로우
- [docs/product-specs/index.md](docs/product-specs/index.md) -- 제품 스펙 목차
- [docs/PLANS.md](docs/PLANS.md) -- 로드맵 및 개선 계획
- [docs/exec-plans/](docs/exec-plans/) -- 실행 계획 (active/completed)
- [docs/exec-plans/tech-debt-tracker.md](docs/exec-plans/tech-debt-tracker.md) -- 기술 부채 추적

### Implementation Reference
- [docs/DESIGN.md](docs/DESIGN.md) -- API 설계 패턴 및 확장 가이드
- [docs/FRONTEND.md](docs/FRONTEND.md) -- N/A (백엔드 전용 프로젝트)
- [docs/generated/db-schema.md](docs/generated/db-schema.md) -- 데이터 모델 (API 응답 스키마)
- [docs/references/druginfo-tools-guide.md](docs/references/druginfo-tools-guide.md) -- MCP 도구 상세 가이드
- [docs/references/architecture-patterns.md](docs/references/architecture-patterns.md) -- 아키텍처 패턴 참조

## Layer Map (Dependency Direction: Top-Down Only)

```
Entry Points (server.py, mcp_server.py)
  -> Handlers (handlers/) / Tool Registration (mcp_tools/)
    -> Business Logic (druginfo/client.py, response_filters.py)
      -> Auth (auth/login.py, manager.py)
        -> Utils (utils/config.py)
          -> External: EDB Admin API
```

## Core Invariants

1. Import 방향: Entry -> Handlers -> Business Logic -> Auth -> Utils (역방향 금지)
2. API 호출: 반드시 `druginfo/client.py` 경유 (직접 requests 금지)
3. 인증 재시도: 401 -> auto_login() -> 1회 재시도 패턴 준수
4. 토큰 저장: `os.environ["EDB_TOKEN"]`에 캐시
5. 에러 전파: DrugInfoError -> RuntimeError -> MCP 응답

## Rules

- 답변은 한글로 작성
- 범용 도구보다 전용 도구 우선 사용
- 응답 요약하여 필요 필드만 출력
- 기존 파일 삭제 금지, 기존 패턴 존중

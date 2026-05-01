# AGENTS.md

의약품 정보 시스템(EDB)을 위한 Python MCP 서버. 의약품 정보 조회 도구를 MCP 클라이언트에 제공.

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

## Agent Entry Points

### Primary Instructions
- AGENTS.md (= CLAUDE.md symlink) -- 코어 규칙, 명령어, 아키텍처 요약

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

## Rules
- 답변은 한글로 작성
- 범용 도구보다 전용 도구 우선 사용
- 응답 요약하여 필요 필드만 출력
- 기존 파일 삭제 금지, 기존 패턴 존중

> Be concise. No filler. Straight to the point. Use fewer words.


## TDD 필수

모든 새 기능/로직 변경은 반드시 TDD로 개발한다.
1. Red: 실패하는 테스트 먼저 작성
2. Green: 테스트를 통과하는 최소 코드 작성
3. Refactor: 코드 정리
테스트 없는 코드 변경은 허용하지 않는다.

---

## Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

Tradeoff: These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## 세션 시작 시 Handoff 강제

세션을 시작할 때 프로젝트 루트에 `handoff.md` 파일이 있는지 먼저 확인한다.
- `handoff.md`가 존재하면 다른 어떤 작업보다 먼저 **반드시 전체를 읽고 인수인계 컨텍스트를 파악한 뒤 시작**한다.
- 파일이 없으면 정상 진행한다.

이 규칙은 이전 세션의 미완료 작업·결정 사항·주의사항을 놓치지 않기 위한 강제 사항이다.

**이 프로젝트의 handoff 위치**: 없음 (생성 시 `.claude-project/HANDOFF.md` 권장)

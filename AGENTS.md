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

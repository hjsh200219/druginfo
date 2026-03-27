# Tech Debt Tracker - DrugInfo MCP

마지막 업데이트: 2026-03-27

## Active Debt

### TD-001: 중복 코드 (try-except-retry 패턴)
- **위치**: `src/mcp_tools/druginfo_tools.py`
- **설명**: 13개 도구에서 동일한 UnauthorizedError catch -> auto_login -> 재시도 패턴 반복
- **영향**: 코드 417줄, 유지보수 비용 증가
- **해결책**: retry 데코레이터 또는 공통 wrapper 함수 도입
- **우선순위**: High
- **예상 공수**: 2시간

### TD-002: Config 클래스 Pydantic 불일치
- **위치**: `src/utils/config.py`
- **설명**: ARCHITECTURE.md에는 Pydantic BaseSettings로 기술되어 있으나 실제로는 일반 Python 클래스
- **영향**: 환경 변수 검증 미흡, 문서와 코드 불일치
- **해결책**: Config를 Pydantic BaseSettings로 전환
- **우선순위**: Medium
- **예상 공수**: 1시간

### TD-003: 글로벌 토큰 이중 저장
- **위치**: `src/mcp_tools/auth_tools.py`, `src/auth/manager.py`
- **설명**: `_AUTO_TOKEN` 전역 변수 + `os.environ["EDB_TOKEN"]` 이중 관리
- **영향**: 두 서버 경로(server.py vs mcp_server.py)에서 토큰 상태 불일치 가능
- **해결책**: AuthManager를 단일 토큰 소스로 통합
- **우선순위**: Medium
- **예상 공수**: 1.5시간

### TD-004: sys.path 조작
- **위치**: `src/mcp_tools/auth_tools.py`
- **설명**: Claude Desktop 호환성을 위한 sys.path.append 핵
- **영향**: import 경로 예측 불가, 디버깅 어려움
- **해결책**: 패키지 설치(setup.py/pyproject.toml) 또는 PYTHONPATH 표준화
- **우선순위**: Low
- **예상 공수**: 2시간

### TD-005: 테스트 부재
- **위치**: 프로젝트 전체
- **설명**: 단위 테스트, 통합 테스트 모두 없음
- **영향**: 리팩토링 시 회귀 위험, 품질 보증 불가
- **해결책**: pytest 기반 테스트 추가 (client.py, login.py, response_filters.py 우선)
- **우선순위**: High
- **예상 공수**: 8시간

### TD-006: 이중 서버 진입점
- **위치**: `src/server.py`, `src/mcp_server.py`
- **설명**: 동일 기능을 Standard MCP SDK와 FastMCP로 각각 구현
- **영향**: 기능 추가 시 양쪽 모두 수정 필요
- **해결책**: 역할을 명확히 분리하거나 하나로 통합
- **우선순위**: Low
- **예상 공수**: 4시간

## Resolved Debt

(없음)

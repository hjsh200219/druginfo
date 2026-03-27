# DrugInfo MCP - Quality Scorecard

마지막 업데이트: 2026-03-27

## Domain/Layer Quality Ratings

| Layer | Test Coverage | Type Safety | Error Handling | Complexity | Overall |
|---|---|---|---|---|---|
| Entry Points | F | B | B | A | C |
| Handlers | F | B | A | B | C |
| MCP Tools | F | B | A | D | C |
| DrugInfo Client | F | B | B | B | C |
| Response Filters | F | B | A | B | C |
| Auth | F | B | B | A | C |
| Utils/Config | F | C | C | A | D |

## Detailed Assessment

### Test Coverage: F (all layers)
- 테스트 파일 없음. 단위 테스트, 통합 테스트 모두 부재.
- 개선 우선순위: druginfo/client.py > response_filters.py > auth/login.py

### Type Safety: B (average)
- Python typing 모듈 사용 (Optional, Dict, Any, List)
- 대부분 `Dict[str, Any]` 수준의 느슨한 타이핑
- Pydantic BaseModel 선언되어 있으나 실질적 검증 미사용 (server.py에서 import만 존재)
- Config 클래스가 Pydantic BaseSettings 미사용 (일반 클래스로 구현)

### Error Handling: A-B
- `UnauthorizedError` / `DrugInfoError` 커스텀 예외 계층 구현
- 401 자동 재시도 패턴 일관 적용
- 중복 로그인 에러 자동 감지 및 처리
- 약점: response_filters.py에서 예외 발생 시 원본 데이터 반환 (silent fallback)

### Complexity
- MCP Tools 레이어(D): druginfo_tools.py가 417줄, 모든 도구에 동일한 try/except 패턴 반복
- 나머지 레이어는 적절한 수준

## Technical Debt

1. **중복 코드**: mcp_tools/druginfo_tools.py의 try-except-retry 패턴이 13회 반복
2. **이중 서버**: server.py와 mcp_server.py가 동일 기능을 다른 SDK로 구현
3. **Config 불일치**: utils/config.py는 일반 클래스이나 ARCHITECTURE.md에는 Pydantic BaseSettings로 기술
4. **글로벌 상태**: `_AUTO_TOKEN` 전역 변수 + `os.environ["EDB_TOKEN"]` 이중 토큰 저장
5. **Import 호환성 핵**: auth_tools.py에 sys.path 조작 코드 존재

## Improvement Priorities

| Priority | Item | Impact | Effort |
|---|---|---|---|
| 1 | 핵심 경로 테스트 추가 (client.py, login.py) | High | Medium |
| 2 | retry 데코레이터로 중복 코드 제거 | Medium | Low |
| 3 | Config를 Pydantic BaseSettings로 전환 | Medium | Low |
| 4 | 서버 진입점 통합 또는 명확한 역할 분리 | Medium | Medium |
| 5 | 전역 토큰 상태를 AuthManager로 통합 | Low | Low |

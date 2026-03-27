# Layer Dependency Rules

## Import Direction: Top-Down Only

```
Entry Points (server.py, mcp_server.py)
    │ can import
    ▼
Handlers (handlers/) / Tool Registration (mcp_tools/)
    │ can import
    ▼
Business Logic (druginfo/)
    │ can import
    ▼
Auth (auth/)
    │ can import
    ▼
Utils (utils/)
```

## Rules

### R1: No Upward Imports
하위 레이어는 상위 레이어를 import하지 않는다.
- druginfo/ -> handlers/ (금지)
- auth/ -> mcp_tools/ (금지)
- utils/ -> 어디든 (금지)

### R2: No Circular References
동일 레이어 내 모듈 간 순환 참조 금지.
- handlers/tools.py <-> handlers/prompts.py (금지)
- auth/login.py <-> auth/manager.py (허용: manager -> login 단방향만)

### R3: Cross-Domain Access via Interface
외부 API 호출은 반드시 druginfo/client.py를 경유한다.
- handlers/tools.py가 직접 requests.get() 호출 (금지)
- mcp_tools/druginfo_tools.py가 직접 requests.get() 호출 (금지)

### R4: Auth State Single Source
토큰 상태는 AuthManager (server.py 경로) 또는 _AUTO_TOKEN + os.environ (mcp_server.py 경로) 중 하나만 사용한다.
- 두 경로 간 토큰 상태 공유 금지 (각자 독립 관리)

### R5: Environment Access
환경 변수 접근은 utils/config.py 또는 모듈 최상위에서만 수행한다.
- 함수 내부에서 os.getenv() 직접 호출 최소화 (현재 client.py에서 위반 중 - 개선 대상)

### R6: Error Propagation
- druginfo/ 레이어: DrugInfoError / UnauthorizedError 발생
- mcp_tools/ 레이어: catch 후 RuntimeError로 변환 또는 재시도
- handlers/ 레이어: catch 후 MCP 응답 형식으로 변환

## Allowed Exceptions

1. `mcp_tools/auth_tools.py`의 sys.path 조작: Claude Desktop 호환성을 위한 임시 허용
2. `druginfo/client.py`의 os.getenv(): 토큰 헤더 설정을 위한 직접 접근 허용 (Config 주입으로 개선 예정)

## Lint Automation (Future)

향후 다음 도구로 자동 검증 예정:
- `import-linter` (Python import 방향 검증)
- 커스텀 pre-commit hook (순환 참조 감지)

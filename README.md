### DrugInfo MCP (Local MCP Server)


이 프로젝트는 MCP 호환 클라이언트에서 사용할 수 있는 로컬 MCP 서버를 제공합니다. 로그인 도구와 DrugInfo(의약품/주성분/제품) 조회 도구들을 MCP Tool 로 노출합니다.

### 요구 사항
- Python 3.9+

### 설치
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 환경 변수 설정
프로젝트 루트에 `.env.local` 파일을 생성하세요.
- 필수
  - `EDB_BASE_URL` (예: https://dev-adminapi.edbintra.co.kr)
  - `EDB_LOGIN_URL` (예: https://dev-adminapi.edbintra.co.kr/v1/auth/login)
- 선택
  - `EDB_USER_ID`, `EDB_PASSWORD` (로그인 시 기본값)
  - `EDB_FORCE_LOGIN` (true/false)
  - `EDB_TIMEOUT` (기본 15)

#### 환경 변수 예시 (.env.local)
개발 서버 예시
```ini
EDB_BASE_URL=https://dev-adminapi.edbintra.co.kr
EDB_LOGIN_URL=https://dev-adminapi.edbintra.co.kr/v1/auth/login
EDB_USER_ID=YOUR_ID
EDB_PASSWORD=YOUR_PASSWORD
```

실서버 예시
```ini
EDB_BASE_URL=https://webconsole-api.edbintra.co.kr
EDB_LOGIN_URL=https://webconsole-api.edbintra.co.kr/v1/auth/login
EDB_USER_ID=YOUR_ID
EDB_PASSWORD=YOUR_PASSWORD
```

### 서버 환경
- 개발 서버: `https://dev-adminapi.edbintra.co.kr`
- 실서버: `https://webconsole-api.edbintra.co.kr/`

### 서버 실행
- 단독 실행
```bash
python -m src.mcp_server
```

- 매니페스트 (MCP 클라이언트용)
```json
{
  "name": "druginfo-mcp",
  "version": "0.1.0",
  "entry": "python -m src.mcp_server"
}
```
MCP 호환 클라이언트(예: IDE/Agent)에서 이 디렉토리를 로컬 서버로 등록하세요.

### 제공 도구 (Tools)
- `login(userId?, password?, force?, loginUrl?, timeout?) -> token`
  - 미지정 시 환경변수 사용: `EDB_USER_ID`, `EDB_PASSWORD`, `EDB_LOGIN_URL`
- `druginfo_list_main_ingredient(a4?, a4Off?, a5?, a5Off?, drugkind?, drugkindOff?, effect?, effectOff?, showMapped?, IngredientCode?, ingredientNameKor?, drugKind?, PageSize?, Page?, SortBy?, q?, page?, size?, timeout?) -> JSON`
- `druginfo_get_main_ingredient_by_code(code, timeout?) -> JSON`
- `druginfo_list_product(crop?, cropOff?, base64?, base64Off?, watermark?, watermarkOff?, confirm?, confirmOff?, teoulLengthShort?, teoulLengthShortOff?, teoulLengthLong?, teoulLengthLongOff?, minCount?, ProductCode?, pillName?, vendor?, PageSize?, Page?, SortBy?, q?, page?, size?, timeout?) -> JSON`
- `druginfo_get_product_by_code(code, timeout?) -> JSON`
- `druginfo_list_main_ingredient_drug_effect(edit?, pageSize?, page?, sortBy?, timeout?) -> JSON`
- `druginfo_get_main_ingredient_drug_effect_by_id(effectId, timeout?) -> JSON`
- `druginfo_list_main_ingredient_drug_kind(edit?, pageSize?, page?, sortBy?, timeout?) -> JSON`
- `druginfo_list_main_ingredient_guide_a4(edit?, pageSize?, page?, sortBy?, timeout?) -> JSON`
- `druginfo_list_main_ingredient_guide_a5(edit?, pageSize?, page?, sortBy?, timeout?) -> JSON`
- `druginfo_list_main_ingredient_picto(IsDeleted?, Title?, PageSize?, Page?, SortBy?, timeout?) -> JSON`
- `druginfo_get_main_ingredient_picto_by_code(code, timeout?) -> JSON`
- `druginfo_list_product_edicode(ProductCode?, EdiCode?, PageSize?, Page?, SortBy?, timeout?) -> JSON`
- `druginfo_list_product_edicode(ProductCode?, EdiCode?, PageSize?, Page?, SortBy?, timeout?) -> JSON`
- `druginfo_list_product_edicode_same_ingredient(ProductCode?, EdiCode?, MasterIngredientCode?, timeout?) -> JSON`

### 간단 호출 예 (개념)
- 토큰 발급: `login({ userId, password, force: true })`
- 주성분 검색: `druginfo_list_main_ingredient({ ingredientNameKor: "아세트아미노펜", PageSize: 20 })`
- 주성분 상세: `druginfo_get_main_ingredient_by_code({ code: "ING-0001" })`
- 제품 검색: `druginfo_list_product({ pillName: "타이레놀", PageSize: 20 })`
- 제품 상세: `druginfo_get_product_by_code({ code: "PRD-0001" })`
- 약효 목록: `druginfo_list_main_ingredient_drug_effect({ pageSize: 50 })`

### CLI (선택)
토큰 발급 및 Bearer GET 테스트를 위한 CLI 유틸이 있습니다.

```bash
# 로그인 후 토큰만 출력
python -m src.login_jwt --url "$EDB_LOGIN_URL" --userId "YOUR_ID" --password "YOUR_PASSWORD"

# 전체 로그인 응답(JSON) 출력
python -m src.login_jwt --url "$EDB_LOGIN_URL" --userId "YOUR_ID" --password "YOUR_PASSWORD" --raw

# 토큰으로 임의의 GET 수행
python -m src.login_jwt --get "https://dev-adminapi.edbintra.co.kr/v1/druginfo/product?pillName=타이레놀" --token "YOUR_TOKEN"
```

<!-- Pilldoc 관련 섹션 제거: 본 프로젝트의 현재 도구 세트에는 포함되지 않습니다. -->

### 디렉토리
- `src/mcp_server.py`: MCP 서버 엔트리
- `src/auth.py`: 로그인/토큰 유틸
- `src/mcp_tools/auth_tools.py`: `login` MCP 도구 등록 및 자동 로그인 처리
- `src/mcp_tools/druginfo_tools.py`: DrugInfo 조회 MCP 도구들 등록
- `src/druginfo/`: DrugInfo API 호출 모듈

### Claude Desktop 설정
macOS(로컬)에서 Claude Desktop과 연동하려면 아래 설정 파일을 생성하세요.

1) 가상환경과 의존성 준비
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) 설정 파일 생성 (macOS)
- 경로: `~/Library/Application Support/Claude/claude_desktop_config.json`
- 예시 내용(경로를 사용자의 실제 경로로 변경하세요). `-c` 실행 방식:
```json
{
  "mcpServers": {
    "druginfo-mcp": {
      "command": "/ABSOLUTE/PROJECT/PATH/.venv/bin/python",
      "args": [
        "-c",
        "import sys; sys.path.insert(0, '/ABSOLUTE/PROJECT/PATH'); from src.mcp_server import create_server; create_server().run()"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/ABSOLUTE/PROJECT/PATH",
        "EDB_BASE_URL": "https://dev-adminapi.edbintra.co.kr",
        "EDB_LOGIN_URL": "https://dev-adminapi.edbintra.co.kr/v1/auth/login",
        "EDB_USER_ID": "EMAIL",
        "EDB_PASSWORD": "PASSWORD"
      }
    }
  }
}
```

실서버 예시
```json
{
  "mcpServers": {
    "druginfo-mcp": {
      "command": "/ABSOLUTE/PROJECT/PATH/.venv/bin/python",
      "args": [
        "-c",
        "import sys; sys.path.insert(0, '/ABSOLUTE/PROJECT/PATH'); from src.mcp_server import create_server; create_server().run()"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/ABSOLUTE/PROJECT/PATH",
        "EDB_BASE_URL": "https://webconsole-api.edbintra.co.kr",
        "EDB_LOGIN_URL": "https://webconsole-api.edbintra.co.kr/v1/auth/login",
        "EDB_USER_ID": "EMAIL",
        "EDB_PASSWORD": "PASSWORD"
      }
    }
  }
}
```

참고: Claude Desktop은 `cwd`를 무시할 수 있습니다. 위 예시처럼 `sys.path.insert(0, PROJECT_PATH)` 또는 `env.PYTHONPATH`에 프로젝트 경로를 추가해야 `import src...`가 정상 동작합니다. 로그에 `ModuleNotFoundError: No module named 'src'`가 보이면 이 설정을 확인하세요.

3) Claude Desktop 재시작 후 사용
- Claude 대화 입력창에서 등록된 MCP 도구들을 사용할 수 있습니다.
- 환경변수는 프로젝트 루트의 `.env.local`를 활용하세요.

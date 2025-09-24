# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드를 작업할 때 필요한 가이드를 제공합니다.

## 프로젝트 개요

의약품 정보 시스템(Pilldoc/EDB)을 위한 Python 기반 MCP (Model Context Protocol) 서버입니다. 현재 구현된 기능:
- **인증 도구**: 로그인 및 토큰 관리
- **약물 정보 도구**: 주성분, 제품, 약효, 가이드, 픽토그램 조회

주의: README.md에는 많은 추가 pilldoc 도구들(accounts, user, pharm 등)이 나열되어 있지만 실제 코드베이스에는 아직 구현되지 않았습니다.

## 개발 명령어

### 초기 설정
```bash
# 가상 환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 서버 실행
```bash
# 독립형 MCP 서버로 실행
python -m src.mcp_server

# 인증 기능 테스트
python -c "from src.auth import login_and_get_token; print(login_and_get_token('LOGIN_URL', 'USER_ID', 'PASSWORD'))"

# 약물 정보 기능 테스트 (환경에 유효한 토큰 필요)
python -c "from src.druginfo import list_main_ingredient; print(list_main_ingredient())"
```

### 환경 변수
환경 변수 설정 (Claude Desktop config나 시스템 환경에 설정):
- `EDB_BASE_URL`: EDB 관리자 API 기본 URL (예: https://dev-adminapi.edbintra.co.kr)
- `EDB_LOGIN_URL`: 로그인 엔드포인트 URL (예: https://dev-adminapi.edbintra.co.kr/v1/auth/login)
- `EDB_USER_ID`: 인증용 기본 사용자 이메일
- `EDB_PASSWORD`: 인증용 기본 비밀번호

선택 사항:
- `EDB_FORCE_LOGIN`: 강제 재로그인 (true/false)
- `EDB_TOKEN`: 기존 인증 토큰 (로그인 후 자동 설정됨)

## 아키텍처

### MCP 서버 구조
FastMCP 프레임워크를 사용하여 도구들을 노출:

1. **진입점** (`src/mcp_server.py`):
   - "druginfo-mcp"라는 이름으로 FastMCP 인스턴스 생성
   - auth와 druginfo 도구 모듈 등록
   - 환경 설정 파일 로드

2. **도구 모듈** (`src/mcp_tools/`):
   - `auth_tools.py`: 로그인 도구 및 자동 로그인 기능
   - `druginfo_tools.py`: 약물 정보 API 도구, 401 에러 시 자동 재시도
   - `__init__.py`: 두 모듈의 등록 함수 내보내기

3. **핵심 모듈**:
   - `src/auth.py`: 토큰 추출 및 재시도 메커니즘을 가진 인증 로직
   - `src/druginfo/client.py`: 약물 정보 엔드포인트용 API 클라이언트
   - 둘 다 다양한 응답 형식과 자동 에러 처리 지원

### 도구 구현

**인증 도구** (`src/mcp_tools/auth_tools.py`):
- `login(userId?, password?, force?, loginUrl?, timeout?)`: 인증 토큰 반환
  - 환경 변수를 기본값으로 사용
  - 토큰을 전역적으로 캐시하여 재사용
  - 중복 로그인 에러(코드 4100) 시 자동 재시도

**약물 정보 도구** (`src/mcp_tools/druginfo_tools.py`):
- `druginfo_list_main_ingredient`: 필터링된 주성분 목록 조회
- `druginfo_get_main_ingredient_by_code`: 특정 주성분 상세 정보
- `druginfo_list_product`: 이미지 옵션과 함께 약물 제품 목록 조회
- `druginfo_get_product_by_code`: 특정 제품 상세 정보
- `druginfo_list_main_ingredient_drug_effect`: 약효 목록 조회
- `druginfo_get_main_ingredient_drug_effect_by_id`: 특정 약효 정보
- `druginfo_list_main_ingredient_drug_kind`: 약물 종류 목록
- `druginfo_list_main_ingredient_guide_a4`: A4 가이드 목록
- `druginfo_list_main_ingredient_guide_a5`: A5 가이드 목록
- `druginfo_list_main_ingredient_picto`: 픽토그램 목록
- `druginfo_get_main_ingredient_picto_by_code`: 특정 픽토그램
- `druginfo_list_product_edicode`: EDI 코드 목록

모든 druginfo 도구는 인증 실패(401 에러) 시 자동으로 로그인 후 재시도합니다.

### 인증 흐름
1. 서버 시작 시 환경 변수가 설정되어 있으면 자동 로그인 시도
2. 로그인 도구는 입력된 자격증명 또는 환경 변수 기본값 사용
3. 중복 로그인 에러(코드 4100) 발생 시 force=true로 자동 재시도
4. 성공한 토큰은 `_AUTO_TOKEN`과 `EDB_TOKEN` 환경 변수에 캐시됨
5. 토큰은 세션 동안 지속됨

## Claude Desktop 통합

Claude Desktop과 함께 사용하려면 다음 파일을 생성:
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "druginfo-mcp": {
      "command": "/프로젝트/경로/.venv/bin/python",
      "args": [
        "-c",
        "import sys; sys.path.insert(0, '/프로젝트/경로'); from src.mcp_server import create_server; create_server().run()"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONPATH": "/프로젝트/경로",
        "EDB_BASE_URL": "https://dev-adminapi.edbintra.co.kr",
        "EDB_LOGIN_URL": "https://dev-adminapi.edbintra.co.kr/v1/auth/login",
        "EDB_USER_ID": "사용자-이메일",
        "EDB_PASSWORD": "비밀번호"
      }
    }
  }
}
```

`/프로젝트/경로`를 이 저장소의 절대 경로로 교체하세요.

## 중요 참고사항

- 서버는 시작 시 환경 변수를 사용하여 자동 로그인 시도
- 성공적인 로그인 후 토큰은 세션 재사용을 위해 전역적으로 캐시됨
- 중복 로그인 에러는 force 플래그로 자동 재시도 트리거
- 모듈 가져오기는 호환성을 위해 표준 및 경로 추가 방식 모두 처리
- README에는 많은 추가 도구들(pilldoc_accounts, pilldoc_user 등)이 언급되지만 아직 구현되지 않음


## 🔴 중요 규칙 (CRITICAL RULES)

### 언어 설정
- 답변은 한글로 해줘
# DrugInfo MCP - Security

## 인증 아키텍처

### JWT 토큰 기반 인증
- EDB Admin API에 userId/password로 로그인하여 JWT 토큰 획득
- 토큰은 `os.environ["EDB_TOKEN"]`에 캐시
- 모든 API 요청에 `Authorization: Bearer {token}` 헤더 첨부

### 토큰 생명주기
1. 서버 시작 시 `auto_login()` → 토큰 획득
2. API 호출 시 401 발생 → `_try_auto_login()` → 재인증 → 1회 재시도
3. 토큰 만료 추정: 1시간 (AuthManager에서 관리)

## 자격 증명 관리

### 환경 변수
- `EDB_USER_ID`: 로그인 사용자 ID
- `EDB_PASSWORD`: 로그인 비밀번호
- `EDB_LOGIN_URL`: 로그인 엔드포인트
- `EDB_TOKEN`: 캐시된 JWT 토큰 (런타임 생성)

### 파일 기반 설정
- `.env.local`: 로컬 환경 변수 (`.gitignore`에 포함)
- `.env`: 기본 환경 변수

### 보안 규칙
1. `.env.local` 파일은 **절대 커밋하지 않음**
2. 토큰을 로그에 전체 출력하지 않음 (`token[:20]...` 형식)
3. 비밀번호는 Config.__str__()에서 마스킹 (`'설정됨'/'미설정'` 표시)

## 네트워크 보안

### HTTPS 통신
- 모든 EDB API 호출은 HTTPS를 통해 수행
- 개발: `https://dev-adminapi.edbintra.co.kr`
- 프로덕션: `https://webconsole-api.edbintra.co.kr`

### 타임아웃
- 기본 타임아웃: 15초 (`EDB_TIMEOUT`으로 조정 가능)
- requests 라이브러리의 연결/읽기 타임아웃 사용

## MCP 프로토콜 보안

### stdio 전송
- MCP 서버는 stdin/stdout을 통해 로컬에서만 통신
- 네트워크 노출 없음 (로컬 프로세스 간 통신)

### 도구 접근 제어
- MCP 클라이언트(Claude Desktop 등)의 도구 승인 메커니즘에 의존
- 서버 측 도구별 접근 제어는 미구현

## 알려진 보안 고려사항

1. **토큰 환경 변수 노출**: `os.environ["EDB_TOKEN"]`에 저장되어 하위 프로세스에서 접근 가능
2. **중복 로그인 강제**: force=true로 다른 세션을 강제 종료할 수 있음
3. **sys.path 조작**: auth_tools.py에서 런타임 경로 변경 (보안 영향 낮음, 로컬 실행)

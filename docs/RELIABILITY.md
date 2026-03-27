# DrugInfo MCP - Reliability Standards

## Service Level Objectives

| Metric | Target | Current Status |
|---|---|---|
| MCP 서버 시작 성공률 | 99% | 측정 미구현 |
| API 호출 성공률 (인증 후) | 95% | 측정 미구현 |
| 자동 재인증 성공률 | 99% | 측정 미구현 |
| 응답 시간 (P95) | < 5s | 타임아웃 15s 설정 |

## Error Budget

- MCP 서버 초기화 실패 시: 로그 경고 후 인증 없이 서버 시작 허용
- API 호출 401 에러: 자동 재로그인 1회 시도 후 실패 시 에러 반환
- 중복 로그인 에러: force=true로 1회 자동 재시도
- 네트워크 타임아웃: 15초 기본값, EDB_TIMEOUT으로 조정 가능

## Failure Modes & Mitigations

### 1. 인증 토큰 만료
- **감지**: HTTP 401 응답
- **완화**: UnauthorizedError catch -> auto_login() -> 동일 요청 재시도 (1회)
- **한계**: 연속 401 시 사용자에게 에러 반환

### 2. 중복 로그인
- **감지**: resultCode "4100" 또는 "중복로그인" 메시지
- **완화**: isForceLogin=true로 재로그인
- **한계**: force 로그인도 실패 시 에러 반환

### 3. EDB API 장애
- **감지**: HTTP 5xx 또는 타임아웃
- **완화**: requests.HTTPError -> DrugInfoError로 래핑
- **한계**: 재시도 로직 없음 (401 외)

### 4. 환경 변수 미설정
- **감지**: Config 초기화 시 기본값 적용
- **완화**: EDB_BASE_URL 없으면 EDB_LOGIN_URL에서 호스트 추출
- **한계**: 두 환경 변수 모두 없으면 DrugInfoError 발생

### 5. 토큰 저장소 불일치
- **감지**: 불가 (글로벌 변수 + 환경 변수 이중 저장)
- **완화**: auto_login()에서 두 곳 모두 갱신
- **개선 필요**: AuthManager 단일 소스로 통합 권장

## Monitoring Checklist

- [ ] 서버 시작/종료 로그 확인 (stderr)
- [ ] 자동 로그인 성공/실패 로그 모니터링
- [ ] API 호출 에러율 추적
- [ ] 토큰 갱신 빈도 모니터링

## Recovery Procedures

### MCP 서버 응답 없음
1. Claude Desktop에서 MCP 서버 재시작
2. `.env.local` 환경 변수 확인
3. `python -m src.login_jwt` CLI로 인증 테스트

### 지속적 인증 실패
1. EDB_USER_ID / EDB_PASSWORD 유효성 확인
2. EDB_LOGIN_URL 접근 가능 여부 확인
3. `EDB_FORCE_LOGIN=true` 설정 후 재시작

### API 응답 형식 변경
1. `response_filters.py`가 _safe_compact로 보호됨 (원본 반환 fallback)
2. client.py의 _handle_response 로직 확인
3. 필요시 response_filters.py 업데이트

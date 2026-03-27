# DrugInfo MCP - Plans & Roadmap

## Current Phase: 안정화 및 품질 개선

### 단기 (1-2주)
1. **핵심 경로 테스트 추가** - client.py, login.py, response_filters.py
2. **retry 데코레이터 도입** - druginfo_tools.py의 중복 코드 제거
3. **Config Pydantic 전환** - utils/config.py를 BaseSettings로 마이그레이션

### 중기 (1-2개월)
4. **서버 진입점 정리** - server.py와 mcp_server.py 역할 명확화
5. **토큰 관리 통합** - AuthManager를 단일 소스로 확립
6. **import-linter 도입** - 레이어 의존성 자동 검증

### 장기 (3-6개월)
7. **패키지화** - pyproject.toml 기반 설치 가능한 패키지로 전환
8. **비GET 엔드포인트 복원** - POST/PUT 도구 재도입 (필요 시)
9. **캐싱 레이어 추가** - 빈번한 조회 결과의 인메모리 캐싱

## Completed

- [x] MCP 서버 기본 구현 (Standard + FastMCP)
- [x] DrugInfo API 클라이언트 구현
- [x] 자동 인증 재시도 패턴 구현
- [x] 응답 토큰 최적화 (response_filters)
- [x] On-demand 스키마 로딩 (server.py)
- [x] MCP 리소스 및 프롬프트 제공
- [x] 하네스 엔지니어링 셋업

## Decision Log

| 날짜 | 결정 | 이유 |
|---|---|---|
| 초기 | FastMCP + Standard MCP 이중 구현 | Claude Desktop 호환성 + 세밀한 제어 모두 필요 |
| 초기 | response_filters.py 분리 | 토큰 비용 절감을 위한 응답 압축 전담 모듈 |
| 초기 | os.environ 토큰 캐시 | 모듈 간 간편한 토큰 공유 (개선 예정) |

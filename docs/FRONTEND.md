# DrugInfo MCP - Frontend

## 공통 금지 사항

- **이모지를 UI 아이콘으로 사용 금지.** OS/브라우저마다 렌더링이 다르고, 텍스트와 간격이 맞지 않음. SVG 아이콘 또는 Remixicon 사용.
- **미구현 페이지로 링크 금지.** 페이지가 없으면 disabled 처리 + "준비 중" 태그 표시.
- **E2E 테스트는 로그인/비로그인 두 상태 모두 검증.**
- **디자인 리뷰 시 모든 상태의 스크린샷 확인 필수.**


이 프로젝트는 백엔드 전용 MCP 서버입니다. 프론트엔드 UI는 포함되어 있지 않습니다.

## 클라이언트 연동

MCP 클라이언트(Claude Desktop, IDE 에이전트 등)가 프론트엔드 역할을 합니다.

### Claude Desktop 설정
`~/Library/Application Support/Claude/claude_desktop_config.json`에 서버를 등록합니다.
상세 설정은 [README.md](../README.md#claude-desktop-설정)을 참조하세요.

### MCP 호환 IDE/Agent
`mcp.json` 매니페스트를 통해 로컬 서버로 등록합니다.

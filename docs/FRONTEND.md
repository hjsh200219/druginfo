# DrugInfo MCP - Frontend

이 프로젝트는 백엔드 전용 MCP 서버입니다. 프론트엔드 UI는 포함되어 있지 않습니다.

## 클라이언트 연동

MCP 클라이언트(Claude Desktop, IDE 에이전트 등)가 프론트엔드 역할을 합니다.

### Claude Desktop 설정
`~/Library/Application Support/Claude/claude_desktop_config.json`에 서버를 등록합니다.
상세 설정은 [README.md](../README.md#claude-desktop-설정)을 참조하세요.

### MCP 호환 IDE/Agent
`mcp.json` 매니페스트를 통해 로컬 서버로 등록합니다.

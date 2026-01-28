
# Discord MCP FEATURES

> Discord MCP = Model Context Protocol Server for Discord
> 이 문서는 `discord-mcp` 서버가 제공하는 주요 기능과 도구(Tool)들을 정리한 것이다.

---

## 1. 전체 개요

- **Discord MCP** – AI 모델이 디스코드 서버와 상호작용할 수 있도록 해주는 미들웨어 서버입니다.
- **Docker 기반** – 도커 컨테이너 위에서 실행되어 설치 및 배포가 간편하며, 환경 격리가 보장됩니다.
- **다국어 지원** – 기본적인 로그 및 타임스탬프는 `config.yaml`을 통해 타임존 설정이 가능합니다.

---

## 2. 주요 기능 요약

### 🔍 서버 및 채널 조회
- `list_servers` – 봇이 참여 중인 모든 디스코드 서버 목록을 가져옵니다.
- `get_server_info` – 특정 서버의 멤버 수, 생성일, 소유자 등 상세 정보를 조회합니다.
- `get_channels` – 서버 내 모든 채널 목록(이름, ID, 타입)을 조회합니다.
- **`inspect_channel`** – 특정 채널의 **상세 정보(비트레이트, 주제 등)** 및 **권한 덮어쓰기(Permission Overwrites)** 현황을 조회합니다. (예: 🏢ㆍ개발감옥)
- **`get_audit_log`** – 서버의 **감사 로그(Audit Log)**를 조회하여 누가 채널을 생성했거나 업데이트했는지 추적합니다.

### 👥 멤버 및 역할 관리
- `get_user_info` – 특정 유저의 상세 정보(가입일, 봇 여부 등)를 조회합니다.
- `list_members` – 서버 멤버 목록과 각 멤버가 가진 역할을 조회합니다.
- `list_roles` – 서버의 모든 역할 목록(ID, 이름, 순위)을 조회합니다.
- **`inspect_role`** – 특정 역할의 **권한 목록(Human-readable)**, 색상, 멘션 가능 여부 등을 상세히 조회합니다.
- `add_role` / `remove_role` – 유저에게 특정 역할을 부여하거나 박탈합니다.

### 💬 메시지 및 소통
- `send_message` – 지정된 채널에 텍스트 메시지를 전송합니다.
- `read_messages` – 채널의 최근 메시지 내역을 읽어옵니다.
- `add_reaction` / `remove_reaction` – 메시지에 이모지로 반응하거나 반응을 제거합니다.
- `add_multiple_reactions` – 한 번에 여러 개의 이모지 반응을 추가합니다.

### 🛡️ 관리 및 모더레이션
- `moderate_message` – 메시지를 삭제하고, 선택적으로 작성자를 타임아웃(Timeout) 처리할 수 있습니다.

### ⚙️ 설정 및 기타
- **Timezone Configuration** – `config.yaml` 파일을 통해 시간을 원하는 타임존(예: `Asia/Seoul`)으로 표시합니다.
- **Docker Volume Mount** – 설정을 컨테이너 재빌드 없이 파일 마운트만으로 즉시 적용할 수 있습니다.

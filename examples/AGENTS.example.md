# AI Office 진입점

- Main은 모든 채팅 시작 시 skill catalog의 ai-office SKILL.md를 읽고 적용한다. 위임받은 child는 배정된 Concept과 task만 수행하고 전체 Office 규칙을 다시 라우팅하지 않는다.
- 모든 사용자 응답에 보고 형식을 항상 적용한다. 상세 양식과 상위 지침·사용자 명시 출력 제약의 우선순위는 ai-office SKILL.md를 따른다.
- 기술 스택, 코드 규칙, 테스트·build·배포 명령과 도메인 지식은 프로젝트 AGENTS.md 또는 프로젝트 전문 Skill에서 관리한다.

# 선택 설정

- ai_office_workspace: /path/to/workspace
- report_timezone: Asia/Seoul

Workspace를 사용하지 않으면 ai_office_workspace 줄을 제거한다. placeholder 경로를 실제 환경 경로로 바꾼다. 기존 report_repository도 호환 alias로 지원하며 지정 경로에 하위 폴더를 자동 추가하지 않는다. 프로젝트 설정이 사용자 설정보다 우선하고 같은 범위에서는 ai_office_workspace가 우선한다. Workspace 밖의 프로젝트 코드와 개인 지식은 AI Office가 관리하지 않는다.
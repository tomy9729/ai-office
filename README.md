# AI Office

Version: **0.5.2**
Source of Truth: [tomy9729/ai-office](https://github.com/tomy9729/ai-office)

AI Office는 대표(User)의 요청을 업무 조율자(Main)가 분석하고 필요한 담당자(Sub Agent)와 함께 수행하는 수평 원팀입니다. Main은 상사가 아니며 역할과 모델에 서열을 두지 않습니다. 회사·프로젝트 지식은 외부 Plugin, Skill 또는 프로젝트 AGENTS.md에 둡니다.

## Core Concept과 Main / Sub Agent

Role/Concept은 직무, Model은 모델과 수행 역량이며 독립적으로 선택합니다. Team은 원팀, Skill/Plugin은 업무 도구와 전문 업무 지식, AGENTS.md는 프로젝트 규칙입니다. Plan은 작업 계획, Delegation은 업무 배정, Review는 리뷰, QA는 검증, Report는 업무 보고, Decision log는 의사결정 기록, Core는 운영 규칙입니다.

Main은 요구 분석, 코드 읽기, 계획, 영향 판단, 역할·모델 선택, 통합과 최종 확인을 맡습니다. 코드 수정과 test/lint/typecheck/build/commit 실행은 Sub Agent에 맡깁니다. 작은 일은 필요한 한 명만 쓰며 독립 작업에 병렬 이득이 있을 때만 여러 명을 씁니다.

| Role / 직무 | 책임 |
|---|---|
| Explorer / 조사 담당 | 진입점·호출 흐름·기존 패턴·영향 범위 조사 |
| Debugger / 문제 분석 담당 | 재현·원인 가설 검증·근본 원인 조사 |
| Implementer / 개발 담당 | Main이 정한 범위의 최소 구현과 검증 |
| Reviewer / 리뷰 담당 | diff·요구사항·회귀·안전성 독립 검토 |
| QA / 검증 담당 | 요구사항에 연결된 실제 실행 검증 |
| Specialist / 전문 담당 | 지정된 기술·도메인 조사와 제한된 자문 |

역할 정의는 [roles/](roles)에 있습니다. 현재 runtime이 제공하는 agent_type을 선택하거나, 선택 기능이 없으면 역할의 developer_instructions를 할당 메시지에 전달합니다. 없는 API를 만들지 않으며 위임이 불가능한 경우 제한을 보고합니다. child는 배정된 결과를 보고한 뒤 task를 끝내고 Office를 다시 구성하지 않습니다. 후속 일은 기존 agent를 재사용하며 runtime 종료 기능은 제공되는 범위에서만 사용합니다.

Sub Agent 목록의 실제 인스턴스 이름에 `[Role] · [Model Full Name] · [Task]`를 적용합니다. 예: `Implementer · 6.1 Sol · AI Office Core 보고 규칙 수정`. 새 생성마다 task에 맞는 지원 모델을 먼저 선택하고 지원하는 도구에서는 model 인자로 명시 요청합니다. 명시 요청을 지원하지 않는 도구에서는 확실하게 확인된 실제 상속 모델을 사용하며, 둘 다 불가능하면 `Role · Task`와 `role_action_target`으로 생성하고 정보 확인 제한만 보고합니다. fork_turns는 none 또는 필요한 양의 이력 수로 지정해 필요한 맥락을 전달합니다. 요청 모델의 실제 적용 여부는 requested_model과 actual_model로 분리해 보고합니다. 현재 runtime은 생성 인자 task_name에 `role_model_action_target`을 기본으로 넣으며 모델 약칭은 family 뒤에 버전의 점을 제거해 붙입니다(예: `implementer_sol61_fix_ap_tree`, `reviewer_astra6_review_chart_diff`). 생성 전에 실제 Role, 모델 약칭과 명시 요청값의 일치(요청이 없으면 확인된 실제 모델과 비교하며 둘 다 없으면 모델 검사 생략), action_target을 확인하고 생성 직후 list_agents의 agent_name 경로를 확인합니다. 정확한 UI 표시에는 제한이 있습니다. 상세 규칙과 제한은 [SKILL.md](SKILL.md), 생성 인자 예시는 [templates.md](references/templates.md)에 있습니다.

## Workflow와 Execution Plan

대표 요청 → 기록 대상이면 업무 티켓 생성 → Main 분석 → 필요한 담당자와 모델 선택 → 업무 배정 → 담당자 작업 → 리뷰·검증 → Main 결과 통합·최종 확인 → 업무 보고 → 설정된 기록 저장 → 완료.

복잡하거나 영향이 큰 변경은 실제 파일과 흐름을 읽은 뒤 10줄 이내 요약과 필요한 Execution Plan을 만듭니다. Plan은 역할·범위·모델 선택·의존성·검증을 담는 초기안이며 조사 결과에 따라 조정합니다. 작은 변경에는 계획을 만들지 않습니다. [templates.md](references/templates.md)와 [teams.md](references/teams.md)는 현재 사용하던 템플릿과 조합 예시입니다.

업무 티켓은 기록할 가치가 있는 요청 하나를 식별해 Plan, 담당자 작업, Review, QA, Report와 Decision을 연결합니다. 저장 보고서 제목은 `AO-YYYYMMDD-NNN · 구체적인 업무 제목`을 쓰고 같은 요청의 후속 작업은 같은 ID를 유지합니다. 채팅은 아래 공통 보고 제목을 사용하며 티켓은 제목 아래에 한 번만 표시합니다. 단순 질의에는 만들지 않으며 Plan이나 Agent를 강제하지 않습니다. 번호를 확인·예약할 수 없거나 동시 발급 가능성이 있으면 전체 UUID 대체 형식을 사용합니다. 발급·충돌 규칙은 [SKILL.md](SKILL.md), 기록 형식은 [templates.md](references/templates.md)에 있습니다.

## 업무 채팅 보고

Main과 Sub Agent가 채팅에 보내는 업무 답변 자체를 보고 양식으로 작성합니다. 공통 제목은 `### 보고 구분 · 업무명`이며 발급된 티켓은 제목 바로 아래 `**Ticket:** [ID]`로 한 번만 표시합니다. 모든 업무 채팅 보고는 제목과 발급된 Ticket 다음, 본문 전에 보고자를 표시합니다. 티켓이 없으면 제목 바로 다음에 표시합니다. Main은 `**보고자:** Main · 업무 조율`, Sub Agent는 `**보고자:** [실제 배정 Role] · [기존 직무]`를 사용하며 여섯 직무 대응은 [SKILL.md](SKILL.md#공통-응답문서-스타일)를 따릅니다. 모델·식별자·범위는 기존 본문에 유지합니다. 일반 질의응답·아이디어 제안·확인 질문은 이 양식을 강제하지 않습니다.

| 보고 구분 | 필수 항목 |
|---|---|
| Main 착수 보고 | 요청 이해 / 수행 계획 / 완료 기준 |
| Main 진행 보고 | 핵심 확인 내용 / 현재 결과 / 다음 작업 |
| Main 결과 보고 | 결과 요약 / 수행 내용 / 검증 / 남은 사항 / 업무 / 기록 / 전체 상태 / 남은 조치 |
| Sub Agent 담당자 보고 | 담당 직무·업무 / 수행 결과 / 근거·검증 / 제한·인계 사항 |

항목명은 굵게 쓰고 자연스러운 문장으로 충분한 근거를 전달하며 길이를 제한하지 않습니다. 진행 보고는 새 정보만 담고 비교·배정은 표를 사용합니다. 장식용 이모지나 불필요한 반복을 넣지 않으며 직무별 새 양식을 만들지 않습니다. 담당자 식별자·실제 관측 이름·이름 적용 확인·표시 제목과 요청/실제 모델 정보는 담당 직무·업무 항목 안에 유지합니다. 실행하지 않은 검증은 `미실행`과 이유를 명시하고, 차단된 진행이나 업무 완료 후 기록 미완료도 구분해 보고합니다.

이는 별도 보고서 생성 기능이 아닙니다. 파일 보고의 metadata와 저장 정책은 독립적으로 유지하며 매 응답마다 파일을 만들지 않습니다. 네 가지 채팅 예시와 저장 보고서 양식은 [templates.md](references/templates.md)에 있습니다.

## Report Architecture

Core는 기록 방법과 템플릿을 관리하고, 외부 AI Office Workspace는 실제 업무 보고서·INDEX·결정·Dashboard 데이터를 보관합니다. Project Repository와 Project Knowledge는 실제 코드와 프로젝트 지식이며 Workspace 밖에 둡니다. 템플릿 원본은 [references/templates.md](references/templates.md)입니다. 회사·프로젝트 규칙, PC 경로와 실제 업무 데이터는 Core Git에 넣지 않습니다.

범용 역할·모델 선택·위임, Plan·Review·QA, 완료·보고 방법과 설치 연결의 변경은 Core Git 대상입니다. 일반 업무의 보고서·INDEX·결정 기록 갱신만으로는 AI Office Git 변경·commit·push가 필요하지 않습니다.

## Completion State와 Reporting

`work_status`는 업무 상태, 기존 `status`는 기록까지 포함한 전체 상태입니다. 업무 완료에는 구현·필요한 리뷰·검증·Main 통합·최종 응답 준비와 Core 변경 시 commit·push를 포함합니다. 업무·기록·전체 상태·남은 조치를 따로 보고하며 Workspace 미설정이면 기록은 `해당 없음`입니다. 업무 완료 후 기록이 남으면 전체 PARTIAL, 기록 진행을 막는 조건이면 BLOCKED입니다.

모델 지정 불가·실제 모델 미확인·이름 관측 실패·UI 표시 불일치는 실행을 중단하지 않습니다. 위임 도구나 필요한 실행 권한 자체의 부재는 blocker입니다.

- **COMPLETED**: 구현·필요한 리뷰·실제 검증·Main 통합·최종 보고 및 설정된 기록 갱신, Dashboard 갱신과 Core 변경 시 commit·push가 모두 끝남.
- **PARTIAL**: 남은 일이 있으며 완료를 선언할 수 없음.
- **BLOCKED**: 진행을 막는 조건이 있으며 원인과 필요한 조치를 보고함.

사용자 또는 프로젝트 AGENTS.md에 `ai_office_workspace`를 지정할 수 있습니다. 기존 `report_repository`는 같은 루트를 가리키는 호환 alias입니다. 프로젝트 설정이 우선하고 같은 범위에서는 ai_office_workspace가 우선합니다. 지정 경로를 그대로 쓰며 하위 폴더를 자동 추가하지 않습니다. 미지정이면 대화의 최종 보고로 충분합니다. 지정된 경우 후속 가치가 있는 작업은 아래 형식으로 저장하며 저장 실패를 COMPLETED로 표시하지 않습니다.

```text
<Workspace>/
├─ Dashboard/Current/{index.html,data.json}
├─ Dashboard/Archive/{Daily,Weekly,Monthly}/
├─ Reports/YYYY/MM/Ticket-ID-작업명.md
├─ INDEX.md
├─ Decisions/DECISIONS.md
├─ README.md
└─ AI Office 운영 안내.md
```

report_timezone은 사용자의 날짜 기준입니다. 없으면 제공된 현지 시간을, 그것도 없으면 UTC를 쓰고 표시합니다. 단순 질의·설명·조사는 저장을 강제하지 않습니다. 중요한 결정만 결정 기록에 남깁니다. 설정 parser나 별도 설정 시스템은 없습니다.

## Size·MD·Report metadata와 Dashboard

Size는 업무 범위와 투입 규모이며 S(명확한 단일 변경), M(여러 파일·역할), L(넓은 영향·여러 단계)만 사용합니다. 난이도·모델 역량·직급을 뜻하지 않습니다. MD는 업무량을 사람 기준 공수로 환산한 추정치이며 실행 시간·Token·모델 성능으로 계산하지 않습니다. Plan에는 Size와 estimated_md, Report에는 YAML metadata와 선택적인 final_md를 기록합니다. INDEX는 final_md를 우선합니다.

Markdown Report → metadata 집계 → data.json → 인터랙티브 HTML 순서이며 Report가 원본입니다. Current와 일·주·월별 Archive는 인터넷·CDN·서버 없이 file://로 여는 단일 HTML Operations Console입니다. Overview / Analytics / History / Health로 전환하며 차트와 업무 목록은 Project·전체 상태·업무 상태·Size·Role·Model·날짜·검색 상태를 공유합니다. 필터 chip·초기화, 정렬·페이지 이동, 업무 상세 dialog, URL hash의 탐색 상태 복원과 뒤로/앞으로 이동을 지원합니다. Decision은 날짜만 적용하며 연결 없는 업무 metadata를 추정하지 않습니다. Dashboard의 목적·설계 기준은 [Workspace 규칙](references/workspace.md)에 유지합니다. 과거 metadata가 없으면 별도 표시하거나 해당 집계에서 제외하며 추정하지 않습니다.

```powershell
python scripts/generate_dashboard.py --workspace /path/to/workspace --timezone Asia/Seoul
python scripts/generate_dashboard.py --workspace /path/to/workspace --timezone Asia/Seoul --date 2026-10-07
```

Report·INDEX·필요한 Decision 저장 뒤 실행합니다. `--date`는 스냅샷 기간의 기준일이고 기본값은 지정 timezone의 현재 날짜입니다. 해당 일·주·월 파일 하나씩을 갱신합니다. DB·서버·watcher·실시간 Agent 상태 수집은 추가하지 않습니다. 상세 규칙과 제한은 [Workspace 규칙](references/workspace.md), metadata 예시는 [템플릿](references/templates.md)을 따릅니다.

0.5.2는 업무 채팅 보고에 보고자 표시를 추가한 운영 규칙 보완입니다.

0.5.1은 업무 채팅 보고 양식과 저장 보고서 정책을 구분한 운영 규칙 보완입니다.

0.5.0은 표시 정보 fallback과 업무·전체 상태 분리, Dashboard 업무 상태 탐색을 추가한 MINOR 변경입니다.

0.4.0은 단일 HTML의 Operations Console과 연결된 데이터 탐색을 추가한 MINOR 변경입니다.

0.3.0은 원팀·역할·Core 경계를 유지하면서 Workspace·공수·Dashboard 기록 기능을 추가하므로 MINOR 변경입니다.

## Project-specific Skills와의 관계

AI Office는 일을 수행하는 방식을 정합니다. 프로젝트 AGENTS.md와 전문 Skill은 기술 스택, 디렉터리 구조, 코드 규칙, 검증 명령, 배포, 도메인 지식을 정합니다. 회사 또는 개인 프로젝트의 규칙을 AI Office 본체에 복제하지 않습니다.

회사 환경 예: `AI Office + 회사 전문 Plugin + 프로젝트 AGENTS.md`. Explorer는 프로젝트 조사 Skill을, Reviewer는 회사 검토 Skill을, QA는 해당 프로젝트 검증 기준을 조합합니다. 기존 회사 Plugin은 그대로 사용합니다.

개인 환경 예: `AI Office + my-web-app/AGENTS.md + 필요한 project-specific Skill`. 회사 Plugin 없이도 여섯 역할, 계획·위임·통합·검증·보고·완료 판단을 사용할 수 있습니다.

## 설치

새 PC의 로컬 사용자 Skill 발견 경로는 `~/.agents/skills`입니다. 설치본 자체를 원본 Git checkout으로 사용하여 설치본과 변경 원본을 하나로 둡니다. 다음 명령은 PowerShell 기준입니다.

```powershell
New-Item -ItemType Directory -Path "$HOME/.agents/skills" -Force | Out-Null
git clone https://github.com/tomy9729/ai-office.git "$HOME/.agents/skills/ai-office"
```

기존 PC에서 catalog가 이미 `~/.codex/skills/ai-office`를 발견한다면 그 경로를 그대로 Git checkout으로 사용합니다. 기존 파일이 있는 경로에는 clone하지 않습니다. 먼저 기존 Skill, 전역 AGENTS.md와 역할을 `~/.codex/backups`처럼 Skill 발견 경로 밖에 백업하고 내용 차이를 검토합니다.

역할은 Codex의 사용자 custom-agent 경로인 `~/.codex/agents`에서 참조합니다. 아래 명령은 새 PC의 빈 역할 경로를 대상으로 합니다. 기존 동명 파일이 있으면 백업·검토하고 대체합니다. SymbolicLink는 Windows Developer Mode 또는 관리자 권한이 필요할 수 있습니다.

```powershell
$officeInstall = "$HOME/.agents/skills/ai-office"
New-Item -ItemType Directory -Path "$HOME/.codex/agents" -Force | Out-Null
Get-ChildItem -LiteralPath "$officeInstall/roles" -Filter 'office-*.toml' | ForEach-Object {
    New-Item -ItemType SymbolicLink -Path (Join-Path "$HOME/.codex/agents" $_.Name) -Target $_.FullName
}
```

링크 권한이 없으면 동명 역할을 먼저 백업하고 원본과 차이를 검토한 뒤 여섯 office 역할만 복사합니다. 다른 custom agent는 건드리지 않습니다.

```powershell
$officeInstall = "$HOME/.agents/skills/ai-office"
New-Item -ItemType Directory -Path "$HOME/.codex/agents" -Force | Out-Null
Get-ChildItem -LiteralPath "$officeInstall/roles" -Filter 'office-*.toml' |
    Copy-Item -Destination "$HOME/.codex/agents"
```

이 PC의 기존 설치는 `~/.codex/skills/ai-office` checkout과 `~/.codex/agents`의 여섯 역할 복사본을 유지합니다. 설치본 역할을 직접 편집하지 않고 repo의 roles를 원본으로 사용합니다. 업데이트 후에는 아래 동기화 명령을 실행합니다. 링크를 쓸 수 있으면 checkout 하나가 Skill과 역할의 공통 원본입니다. 역할 파일은 name, description, developer_instructions를 사용하며 config.toml 변경은 필요하지 않습니다. 현재 세션의 catalog가 즉시 갱신된다고 가정하지 말고 다음 세션에서 Skill과 역할이 발견되는지 확인합니다.

전역 AGENTS.md에는 [examples/AGENTS.example.md](examples/AGENTS.example.md)의 진입점과 필요한 개인 설정만 둡니다. 프로젝트 지침은 프로젝트 AGENTS.md에 둡니다. Skill 폴더 전체를 junction으로 연결하는 대신 실제 checkout을 발견 경로에 둡니다.

설치 경로와 custom-agent 형식의 근거: [Skills 문서](https://learn.chatgpt.com/docs/build-skills), [Subagent 문서](https://learn.chatgpt.com/docs/agent-configuration/subagents). runtime마다 도구와 기능은 세션에서 다시 확인합니다.

## 업데이트와 변경

```powershell
git -C "$HOME/.agents/skills/ai-office" status --short
git -C "$HOME/.agents/skills/ai-office" pull --ff-only
```

기존 경로 설치는 위 명령의 경로를 `~/.codex/skills/ai-office`로 바꿉니다. 로컬 변경이 있으면 먼저 검토·commit하거나 별도 보존하며 강제로 덮어쓰지 않습니다. 연결된 역할은 checkout 갱신을 따라갑니다.

복사 설치는 pull 후 역할 설치본에 임의 변경이 없는지 먼저 확인하고 아래 여섯 역할만 다시 동기화합니다. 설치 경로에 맞게 officeInstall을 지정합니다.

```powershell
$officeInstall = "$HOME/.agents/skills/ai-office"
Get-ChildItem -LiteralPath "$officeInstall/roles" -Filter 'office-*.toml' |
    Copy-Item -Destination "$HOME/.codex/agents" -Force
```

AI Office 개선은 Core 변경 여부 확인 → 원본 checkout 변경 → 대상 diff·민감정보 검토 → 검증·review → commit → GitHub push → 다른 PC에서 pull 순서로 관리합니다. 별도 복사 설치본을 수정했다면 변경을 원본 checkout에 반영한 뒤 이 순서를 따릅니다. 가능한 환경에서는 commit·push까지 완료해야 하며 실패하거나 실행할 수 없으면 PARTIAL로 표시하고 원인과 남은 조치를 보고합니다. GitHub가 공통 원본이며 각 PC는 설치 checkout입니다. push에는 해당 저장소의 쓰기 권한이 있는 Git 인증이 필요합니다. 다른 계정의 기존 인증을 덮어쓰지 않습니다. 회사·프로젝트 전용 수정은 외부 Plugin/Skill에 둡니다. 배포 시스템, installer, package manager와 CI는 추가하지 않습니다.

버전은 README에서 관리합니다. PATCH는 문구·작은 운영 규칙 보완, MINOR는 역할·workflow·기록 기능 추가, MAJOR는 핵심 운영 구조 변경입니다. Tag는 필요할 때 사용합니다.

## 패키지와 라이선스

```text
ai-office/
├─ SKILL.md
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .gitattributes
├─ roles/office-*.toml
├─ references/teams.md
├─ references/templates.md
├─ references/workspace.md
├─ scripts/generate_dashboard.py
├─ scripts/test_generate_dashboard.py
├─ scripts/dashboard.html
├─ scripts/check_dashboard.cjs
└─ examples/AGENTS.example.md
```

[LICENSE](LICENSE)는 현재 라이선스 정책입니다. 소유자의 확인 없이 오픈소스 라이선스를 임의로 부여하지 않습니다.

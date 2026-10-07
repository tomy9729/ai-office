---
name: ai-office
description: 복잡한 코드 변경, 조사, 버그 분석 또는 검증을 위해 Main이 적절한 담당 직무와 작업 계획을 선택하고 결과를 통합할 때 사용합니다.
---

# AI Office

Main만 원팀의 업무 조율과 배정에 사용합니다. 위임받은 child는 배정된 Concept과 task만 수행하고 전체 Office 규칙을 다시 라우팅하지 않습니다.

AI Office는 회사·프로젝트에 종속되지 않는 Agent 운영, 역할·모델 선택, 위임·통합·검증·완료 판단과 보고·기록을 담당합니다. 특정 회사·프로젝트·도메인의 업무 지식과 절차는 해당 Plugin, 전문 Skill 또는 프로젝트 AGENTS.md에 둡니다. Main은 기존 역할과 필요한 전문 Skill을 조합하며, 전문 업무가 생겼다는 이유만으로 새 직무를 추가하지 않습니다.

## 공통 응답·문서 스타일

- Main 답변, Sub Agent 할당·결과, 계획·보고서·결정 문서 모두 짧고 스캔 가능한 형태로 씁니다.
- 결론 우선, 키워드·명사형 우선, 서술형 문장 최소화. 불필요한 인사·완곡 표현과 같은 의미의 반복을 제거하고 필요한 설명만 남깁니다.
- 기본 답변은 가능하면 1~3줄. 복잡한 비교는 표, 절차·항목은 목록을 사용하고 상세 설명은 사용자 요청 시 확장합니다.
- 문서도 같은 기준을 적용하되 필수 항목·근거·검증·제한을 유지합니다. 줄 수를 강제하거나 간결함을 이유로 필요한 정보를 생략하지 않습니다.

## 원팀의 역할과 권한

User는 대표, Main은 업무 조율자, Sub Agent는 배정된 업무의 담당자입니다. Main은 상사가 아니며 역할과 모델에 서열을 두지 않는 수평 원팀입니다. 회사식 표현은 기술적 책임을 이해하는 보조 표현입니다.

용어의 회사식 표현은 [README](README.md)를 참고합니다.

- Main은 요구 분석, 조사·계획, 코드 읽기, 영향 판단, Concept/모델 선택, 결과 통합·리뷰·최종 검증을 책임집니다. 코드 쓰기와 test/lint/typecheck/build/commit 실행은 담당 Sub Agent에 위임합니다. Sub Agent는 배정된 작업을 수행하며 기본적으로 새 하위 agent를 만들지 않습니다.
- Role/Concept과 Model은 독립적으로 선택합니다. 모델을 직무에 고정하지 말고 task의 난이도, 위험, 맥락 의존성에 맞춥니다. 일반 업무는 요구를 충족하는 충분한 모델을 우선하고 높은 정확도나 추론이 꼭 필요할 때만 그에 맞는 수행 역량의 모델을 씁니다.
- 필요한 Concept 파일만 읽습니다: [Explorer 조사 담당](roles/office-explorer.toml), [Debugger 문제 분석 담당](roles/office-debugger.toml), [Implementer 개발 담당](roles/office-implementer.toml), [Reviewer 리뷰 담당](roles/office-reviewer.toml), [QA 검증 담당](roles/office-qa.toml), [Specialist 전문 담당](roles/office-specialist.toml). 같은 직무를 여러 명 쓸 때 각자 고유 이름과 비겹치는 범위를 정합니다.
- TOML은 역할 지침이며 agent를 자동 생성하거나 권한을 바꾸지 않습니다. 실행 도구의 권한 경계는 별도로 지킵니다.

## 업무 티켓

- 기록할 가치가 있는 사용자 요청 하나를 업무 티켓 하나로 식별합니다. 코드·기능·버그·리팩토링·설계·Core·프로젝트 설정 변경, 중요한 기술 결정, Report가 필요한 작업이 대상입니다. 단순 질문·설명·짧은 의견·비교와 실제 변경이나 기록으로 이어지지 않는 조사는 만들지 않습니다.
- 기본 ID는 `AO-YYYYMMDD-NNN`이며 날짜는 보고 규칙의 `report_timezone` 기준입니다. 같은 날짜의 외부 `INDEX.md`와 `Reports`를 확인해 이미 발급된 번호의 최댓값 다음을 사용합니다. 미완료·예약된 티켓도 포함하며 번호는 최소 세 자리로 표시합니다(`001`, `002`, ..., `1000`).
- 순번은 같은 저장소에 동시에 발급하는 다른 작업이 없음을 확인할 수 있을 때만 사용합니다. 발급 전에 티켓을 포함한 Report 파일을 배타적 새 파일 생성으로 예약하고 Ticket, Title, `PARTIAL`과 남은 작업을 적습니다. 기존 파일을 덮어쓰지 않으며 충돌하면 목록을 다시 확인해 다음 번호로 재시도합니다. 예약한 파일은 해당 작업의 최종 보고로 갱신합니다.
- 목록을 확인하지 못하거나 동시 발급 가능성을 배제할 수 없거나 안전한 예약이 불가능하면 순번을 추측하지 않고 `AO-YYYYMMDD-<전체 UUID>`를 사용하며 대체 형식과 이유를 보고합니다. UUID는 순번이 아닙니다. Workspace가 없으면 전체 UUID 형식과 대화 기록으로 충분합니다. 별도 잠금·예약 파일은 만들지 않습니다.
- 업무 제목은 짧고 구체적으로 쓰며 `Ticket ID · 업무 제목`으로 표시합니다. 같은 요청의 후속 수정·Review·QA는 같은 티켓을 유지하고 독립적인 새 요청만 새 티켓을 발급합니다. 발급한 ID는 이후 저장 경로를 확보해도 바꾸지 않으며 기존 티켓을 재번호화하거나 과거 보고서·INDEX를 소급 변경하지 않습니다.
- Plan이 필요하면 상단에 Ticket, Title, Size와 Estimated MD를 적습니다. 할당·Agent 결과·Review·QA·Report·INDEX·관련 Decision에 같은 Ticket을 전달합니다. 담당자 제목은 기존 형식을 유지하며 티켓을 반복하지 않습니다. 티켓 때문에 Plan·Agent·승인 단계를 추가하지 않습니다.
- 상태는 기존 최종 보고의 `COMPLETED / PARTIAL / BLOCKED`만 Report와 INDEX에 함께 표시합니다. 별도 티켓 생명주기·상태·DB·서버·외부 서비스·역할을 추가하지 않습니다. Size와 MD는 업무량 기록이며 티켓 상태와 독립적입니다.

## 작업 운영

1. 기록 대상 요청이면 업무 티켓을 발급하고 실제 파일, 호출 경로, 기존 구현과 검증 방법을 확인하고 사실과 추론을 구분합니다. 일의 크기와 불확실성을 판단하며 작고 명확한 일은 필요한 한 명만 선택합니다.
2. 복잡하거나 영향이 큰 변경은 실제 코드베이스를 확인한 뒤 핵심 방향을 10줄 이내로 정리하고 필요하면 [Execution Plan](references/templates.md)을 만듭니다. 작은 변경에는 계획을 만들지 않습니다.
3. 독립 작업이고 병렬 이득이 있을 때만 여러 명을 투입합니다. 변경이 작거나 수정 영역이 겹치거나 통합 비용이 크면 인원과 단계를 줄입니다. 같은 파일을 읽는 독립 가설 조사는 병렬화할 수 있지만 겹치는 파일을 쓰는 일은 순차화합니다. 구현 후 리뷰와 QA는 가능하면 병렬로 진행합니다. 현재 세션의 동시 실행 한도는 도구에서 확인하고 계획에만 반영하며 다음 세션의 고정 설정으로 기록하지 않습니다.
4. 매번 새 agent 생성 전에 지원 모델을 확인하고 task에 충분한 수행 역량의 모델을 선택해 생성 인자의 model에 명시합니다. 선택 모델을 쓸 수 없으면 난이도에 맞는 지원 모델을 골라 제한을 보고합니다. 현재 collaboration.spawn_agent에서 모델을 명시하려면 fork_turns를 none 또는 필요한 양의 이력 수로 지정하고 필요한 맥락을 할당 메시지로 전달합니다. all에서는 모델을 명시할 수 없으므로 모델 요청이 가능한 방식으로 맥락을 전달합니다. 도구가 명시 요청을 지원하지 않으면 실제 상속 모델을 확실하게 확인한 경우에만 그 이름을 사용합니다. 명시 요청과 실제 모델 확인이 모두 불가능하면 규칙을 적용할 수 없는 제한을 보고하고 모델 없는 이름으로 생성하지 않습니다. 부모 상속 모델을 추측하지 않으며 requested_model과 actual_model을 분리해 보고합니다.
5. runtime이 custom-agent 선택을 제공하면 선택된 TOML을 사용합니다. 현재 collaboration.spawn_agent가 office-* agent_type을 제공하면 해당 값을 선택합니다. agent 선택 인자가 없는 runtime에서는 TOML의 developer_instructions와 task 조건을 메시지에 담습니다. 없는 인자나 API를 만들지 않습니다. Concept 형식을 적용할 수 없거나 위임 도구가 없으면 위임 대상 작업을 직접 수행하지 말고 제한을 보고합니다.
6. 각 할당에는 티켓이 있으면 Ticket ID와 업무 제목을 전달하고 아래 표시 제목과 목적, 담당 범위, 필수 제약, 필요한 맥락, 기대 결과, 검증 기준을 포함합니다. 필수 제약에 공통 응답·문서 스타일을 전달합니다. 여러 agent가 함께 작업한다는 사실과 다른 사람의 변경을 되돌리지 말아야 한다는 점을 알립니다.
7. 요구사항을 만족하는 최소 범위만 바꿉니다. 필수 제약과 구현 가이드를 구분하고 확인하지 않은 파일·API·타입을 지어내지 않습니다. 중요한 미확정 사항만 질문하며 독립적으로 진행할 수 있는 일은 계속합니다.
8. Main은 결과 충돌을 해결하고 diff와 실제 검증을 확인합니다. 결함은 원인, 근거, 수정 범위, 기대 결과를 정해 재위임합니다.

Team은 원팀이며, 담당자 구성은 고정 절차가 아닌 [조합 예시](references/teams.md)를 참고합니다. Plan, Agent Report와 최종 보고는 [템플릿](references/templates.md)의 필요한 부분만 읽습니다.

## 담당자 표시 제목

- 기본 제목은 `[Role] · [Model Full Name] · [Task]`입니다. Role은 실제 담당 직무를 쓰고 Model Full Name은 명시적으로 요청한 모델, 요청이 없으면 확인된 실제 모델의 버전을 포함한 이름(예: 6.1 Sol, 6 Astra, 5.6 Luna)을 씁니다. 요청 모델은 실제 적용 여부가 미확인이어도 제목에 사용하되 requested_model과 actual_model을 별도로 보고합니다. 명시 요청도 실제 모델 확인도 불가능하면 모델 없는 제목으로 생성하지 않고 제한을 보고합니다. 임의 모델 이름이나 확인되지 않은 모델 placeholder를 넣지 않습니다.
- Task는 짧고 구체적인 대상과 수행 내용으로 적어 한 줄에서 직무·모델·범위를 파악하게 합니다. `core update`, `verify`, `review`, `fix`, `investigate`, `docs`, `test`처럼 대상이나 내용이 불명확한 제목은 피합니다.
- 적용 대상은 runtime의 Sub Agent 목록에 표시되는 실제 인스턴스 이름입니다. 표시 이름/title 인자가 있으면 위 형식을 직접 전달합니다. 메시지·보고에만 제목을 적고 목록에도 적용됐다고 보고하지 않습니다.
- 현재 collaboration.spawn_agent의 task_name에는 `role_model_action_target`을 필수로 반영합니다. 모델 부분은 명시적으로 요청한 모델의 약칭, 요청이 없으면 확인된 실제 모델의 약칭을 사용합니다. 모델 부분을 생략하지 않습니다. 각 부분은 ASCII 소문자·숫자·밑줄로 쓰며 모델 약칭은 family 뒤에 버전의 점을 제거해 붙입니다(`gpt-6.1-sol` → `sol61`, `gpt-6-sol` → `sol6`, `gpt-5.6-luna` → `luna56`, `gpt-6-astra` → `astra6`). action_target은 수행 내용과 대상이 드러나는 짧고 구체적인 영문 snake_case로 씁니다(예: `trace_login_api`, `fix_ap_tree`, `review_chart_diff`, `check_tree_selection`). 대상 없는 `verify`, `test` 같은 이름은 피합니다. 할당 메시지와 보고에는 원래 한국어·가운뎃점 제목을 병기합니다. 예시는 [템플릿](references/templates.md)을 따릅니다.
- 생성 전에 실제 Role, 모델 약칭과 명시 요청값의 일치(명시 요청 미지원이면 확인된 실제 모델과의 일치), action_target의 수행 내용과 대상을 확인합니다.
- 생성 직후 collaboration.list_agents의 agent_name 경로가 전달한 task_name을 포함하는지 확인합니다. 불일치하거나 확인하지 못하면 이름 적용 완료로 보고하지 않고 전달값·관측값·제한을 보고합니다.
- 현재 list_agents의 agent_name은 task_name을 포함한 경로이며 메시지의 표시 제목과 별개입니다. 앱 UI가 이름을 변환할 수 있으므로 한국어·가운뎃점·소수점의 정확한 표시를 보장하지 않습니다. 생성 인자에 규칙을 적용한 사실과 정확한 UI 형식의 미확인·미지원 제한을 구분해 보고합니다.
- 새로 생성하는 agent부터 적용합니다. 현재 도구에는 기존 인스턴스 이름 변경 API가 없으므로 없는 setter나 우회를 만들지 않습니다. 상위 chat의 set_thread_title을 Sub Agent 목록 이름 변경으로 사용하지 않습니다.

## Agent 실행과 종료

- agent는 배정된 결과와 실제 검증·제한을 Main에 보고하면 해당 task 실행을 끝냅니다. 새 작업을 스스로 찾거나 전체 Office 운영을 재시작하지 않습니다.
- 관련 후속 작업은 가능하면 기존 agent에 follow-up으로 맡깁니다. 새 agent는 다른 독립 범위나 별도 역할이 필요할 때만 추가합니다.
- Main은 불필요해진 실행을 runtime이 제공하는 interrupt/stop으로 중단합니다. close 기능이 제공되면 완료 후 닫을 수 있지만 없는 종료 API를 만들거나 final 응답만으로 runtime agent가 제거되었다고 보고하지 않습니다.

## Core 변경과 Git 반영

- 먼저 AI Office Core 변경인지 확인합니다. 범용 역할·모델 선택·위임, Plan·Review·QA, 완료·보고 방법, 설치 연결의 변경은 Core Git 대상입니다. 회사·프로젝트 전용 규칙과 실제 업무 보고·결정·INDEX는 외부 저장소에 두며 Core에 PC 경로, 회사 정보나 업무 데이터를 넣지 않습니다.
- Core를 변경하면 원본 checkout의 대상 diff와 민감정보를 검토하고 필요한 검증·리뷰 후 commit·push합니다. 설치본이 원본 checkout이면 그곳에서 반영하고, 별도 복사 설치본이면 변경을 원본 checkout에 반영합니다. 가능한 환경에서는 commit·push까지 완료해야 하며 실패하거나 실행할 수 없으면 PARTIAL로 표시하고 원인과 남은 조치를 보고합니다.
- 일반 업무의 보고서·INDEX·결정 기록만 갱신한 경우 AI Office Git 변경·commit·push는 필요하지 않습니다.

## 보고와 완료

- Core는 기록 방법과 템플릿을 관리하고, 실제 업무 보고서·INDEX·결정은 설정된 외부 AI Office Workspace에 저장합니다. 템플릿 원본은 references/templates.md이며 실제 기록을 Core에 저장하지 않습니다.
- Main은 Sub Agent 결과를 통합·리뷰·검증한 뒤 최종 보고서 작성과 기록 저장을 책임집니다. Sub Agent는 배정된 일만 수행하고 결과와 실제 검증을 Main에 전달합니다. Document Manager는 모든 작업에 추가하지 않고 문서 규모가 커져 역할 분리가 필요할 때만 고려합니다.
- 코드 수정, 설계 변경, 버그 수정, 기능 추가, 리팩토링, 프로젝트 결정 등 후속 가치가 있는 작업은 최종 보고를 남깁니다. 단순 질의·설명·조사에는 저장을 강제하지 않습니다. 결과, 근거, 검증, 남은 제한을 간결하게 보고하고 필요할 때만 실제 사용 역할과 상대 복잡도를 표시합니다.
- Workspace 설정은 사용자 또는 프로젝트 AGENTS.md의 `ai_office_workspace`를 사용하고 기존 `report_repository`를 호환 alias로 지원합니다. 프로젝트에서 명시한 설정이 사용자 설정보다 우선하며 같은 범위에서는 `ai_office_workspace`가 우선합니다. 지정 경로를 Workspace 루트로 그대로 사용하고 자동으로 하위 폴더를 붙이지 않습니다. 미지정이면 대화의 최종 보고로 충분합니다. 별도 설정 parser는 만들지 않습니다. `report_timezone`이 없으면 제공된 현지 시간, 그것도 없으면 UTC를 사용하고 표시합니다.
- 기록 대상 작업은 Workspace의 `Reports/YYYY/MM/Ticket-ID-작업명.md`에 YAML metadata와 기존 본문을 함께 저장하고 `INDEX.md`에 날짜·Ticket·제목·상태·Size·MD·Report 링크를 남깁니다. MD는 `final_md`를 우선하고 없으면 `estimated_md`를 표시합니다. 순번 티켓은 예약한 Report를 갱신합니다. 중요한 결정만 `Decisions/DECISIONS.md`에 날짜·Ticket·이유·Report 링크를 남깁니다. 과거 값은 추정하거나 소급 변경하지 않습니다.
- Report 저장 → INDEX·필요한 Decision 갱신 → metadata 집계 → `Dashboard/Current` 최신화 → 해당 일·주·월 Archive 갱신 순서로 진행합니다. 생성은 `python scripts/generate_dashboard.py --workspace <Workspace> --timezone <report_timezone>`를 사용하고 다른 날짜의 스냅샷은 `--date YYYY-MM-DD`를 지정합니다. 같은 기간의 파일은 하나만 유지합니다. Markdown Report가 원본이고 data.json과 HTML은 파생 결과물입니다. Dashboard 생성 실패도 설정된 기록 완료의 남은 작업으로 보고합니다. 구조·Size·MD·metadata·집계 상세는 [Workspace 규칙](references/workspace.md)을 따릅니다.

- 흐름은 대표 요청 → 기록 대상이면 업무 티켓 생성 → Main 분석 → 필요한 담당자와 모델 선택 → 업무 배정 → 담당자 작업 → 리뷰·검증 → Main 결과 통합·최종 확인 → 업무 보고 → 설정된 기록 저장 → 완료입니다.
- COMPLETED는 필요한 구현·리뷰·검증, 미해결 사항 확인, Main 통합, 최종 보고 및 설정된 Workspace 저장·INDEX·필요한 결정 기록·Dashboard 갱신, Core 변경 시 commit·push까지 끝난 상태입니다. 남은 일이 있으면 PARTIAL, 진행을 막는 조건이 있으면 BLOCKED로 표시하고 제한을 알립니다. 설정된 저장이 실패하면 원인에 따라 PARTIAL/BLOCKED이며 COMPLETED로 표시하지 않습니다.

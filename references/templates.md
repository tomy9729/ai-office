# Plan 및 보고 템플릿

## Ticket 정보

```text
Ticket: AO-YYYYMMDD-NNN
Title: 짧고 구체적인 업무 제목
Status: COMPLETED / PARTIAL / BLOCKED
Size: S / M / L
Estimated MD: 업무량 추정값
Final MD: 종료 시 보정값 (선택)
Report / Decision: 관련 기록 링크 또는 없음
```

티켓 비대상 작업에서는 Ticket과 Title 필드를 생략한다. 발급·예약·후속 요청 규칙은 [SKILL.md](../SKILL.md)의 업무 티켓을 따른다. 상태는 별도 생명주기가 아닌 기존 최종 보고 상태다. 순번을 확인·예약할 수 없거나 동시 발급 가능성이 있으면 ID의 NNN 대신 전체 UUID를 사용하고 이유를 남긴다.

## Plan 요약

10줄 이내로 목적, 현재/원하는 동작, 주요 파일과 호출 흐름, 핵심 방향, 필수 제약, 영향 범위, 결과 중심 검증을 적는다. 확인하지 않은 구현 세부는 고정하지 않는다.

## Execution Plan

Ticket: [발급한 Ticket ID]
Title: [업무 제목]
Size: [S / M / L]
Estimated MD: [예상 공수]

Team (원팀 구성): [선택한 담당자 조합 / 직무 하나 / 사용자 정의]

Agent instances: [고유 식별자와 표시 제목]

Parallel groups: [독립 작업 그룹 또는 없음]

초기안이며 조사 결과에 따라 갱신한다.

| Phase | Agent instances / Role | Model | Task / Scope | Risk | Depends on | Check |
|---|---|---|---|---|---|---|
| 조사 | Explorer #1 | 선택 근거와 요청/확인 구분 | 조사 범위 | low/medium/high 또는 생략 | 없음 | 근거·경로·흐름 |
| 구현 | Implementer #1 | 선택 근거와 요청/확인 구분 | 결정된 수정 범위 | low/medium/high 또는 생략 | 조사 결과 | 변경 동작·검증 |
| 확인 | Reviewer 또는 QA | 선택 근거와 요청/확인 구분 | 독립 diff 또는 실행 확인 | low/medium/high 또는 생략 | 구현 완료 | finding·실제 결과 |
| 통합 | Main | 확인된 모델 또는 생략 | 충돌 해결·최종 확인 | — | 위 결과 | 요구사항과 diff 대조 |

Implementation이 필요한 Bugfix에는 Implementer를 최소 1개 배정한다. 조사만 하고 끝나는 버그 분석은 예외다.

### 작은 작업 축약

`[Role] · [Model Full Name] · [Task]` — [모델 선택 근거와 요청/확인 구분] — [결과/검증]

## 담당자 목록 이름과 생성 인자 예시

기본은 `[Role] · [Model Full Name] · [Task]`이며 실제 확인된 모델 이름과 버전을 사용한다. 요청 모델만 알고 실제 모델을 확인하지 못하면 제목은 `[Role] · [Task]`로 쓰고 요청값은 별도로 기록한다. 요청값을 실제 확인값처럼 표시하지 않는다.

- `Implementer · 6.1 Sol · AI Office Core 보고 규칙 수정`
- `Reviewer · 6 Astra · Core 변경 diff·회귀 위험 검토`
- `QA · 5.6 Luna · 설치·업데이트 절차 동작 검증`
- `Explorer · 로그인 API 호출 흐름 조사` (요청 모델: 6.1 Sol, actual_model: 미기록)

현재 collaboration.spawn_agent 호출의 task_name에 아래 이름을 실제로 전달하고 메시지·보고에 원래 제목을 병기한다. 확인 모델 예시와 모델 생략 예시를 구분한다.

| task_name | 표시 제목 |
|---|---|
| `implementer_6_1_sol_ai_office_agent_list_name_rules_update` | Implementer · 6.1 Sol · AI Office 목록 이름 규칙 수정 |
| `qa_5_6_luna_install_update_flow_check` | QA · 5.6 Luna · 설치·업데이트 절차 동작 검증 |
| `explorer_codex_agent_list_name_trace` | Explorer · Codex Agent 목록 이름 흐름 조사 |

작성·runtime 적용과 정확한 UI 표시의 제한은 [SKILL.md](../SKILL.md)의 담당자 표시 제목을 따른다.

## Agent 할당

```text
Ticket: [발급한 Ticket ID]
Title: [업무 제목]
task_name (실제 생성 인자): role_model_task / 실제 모델 확인 불가 시 role_task
표시 제목: [Role] · [Model Full Name] · [Task] / 실제 모델 확인 불가 시 [Role] · [Task]
모델 (요청 / 실제 확인):
역할 / 목적:
담당 범위:
필수 제약:
필요한 맥락:
기대 결과:
검증 기준:
```

## Agent 결과

```text
Ticket: [발급한 Ticket ID]
Title: [업무 제목]
task_name (실제 생성 인자): role_model_task / 실제 모델 확인 불가 시 role_task
표시 제목: [Role] · [Model Full Name] · [Task] / 실제 모델 확인 불가 시 [Role] · [Task]
모델 (요청 / 실제 확인):
Role / task:
Result:
Evidence (paths, commands, observed behavior):
Validation (run / not run, actual outcome):
Limitations or blocker:
```

## Agent Report

Ticket: [발급한 Ticket ID]

필요한 경우 실제 사용한 agent만 기록한다. Complexity는 선택적인 상대 난이도이며 유용할 때만 low/medium/high로 적는다.

| Agent identifier / 표시 제목 | Role | Task | Model (requested / confirmed) | Complexity | Result |
|---|---|---|---|---|---|
| explorer_6_1_sol_login_api_call_flow_trace / Explorer · 6.1 Sol · 로그인 API 호출 흐름 조사 | Explorer | 조사 범위 | 6.1 Sol / 6.1 Sol 확인 | 선택 | 완료 및 근거 |
| implementer_ai_office_core_report_rules_update / Implementer · AI Office Core 보고 규칙 수정 | Implementer | 수정 범위 | requested_model: 6.1 Sol / actual_model: 미기록 | 선택 | 변경 및 검증 |

Max Parallel: [관측된 최대 동시 Agent 수; Main 제외]

확인하지 않은 모델은 요청 모델과 구분한다.

## 최종 보고와 기록

기록 대상과 완료 조건은 [SKILL.md](../SKILL.md)의 보고 규칙을 따른다. Workspace 설정이 없으면 대화의 최종 보고로 충분하다. 지정되어 있으면 보고서는 `<Workspace>/Reports/YYYY/MM/Ticket-ID-작업명.md`에 저장하며 INDEX와 필요한 결정 기록도 갱신한다. 순번 티켓은 발급 때 예약한 파일을 최종 보고로 갱신한다. 날짜는 사용자 또는 프로젝트의 `report_timezone` 기준이며 없으면 제공된 현지 시간, 그것도 없으면 UTC를 사용하고 표시한다. 다른 작업의 기존 파일은 덮어쓰지 않는다. 신규 순번 예약이 충돌하면 목록을 다시 확인하고 다음 번호를 발급하며 작업명 suffix로 번호 충돌을 회피하지 않는다. 안전한 순번 발급이 불가능하면 전체 UUID 대체 형식과 제한을 보고한다. 짧고 실용적으로 쓰며 사고 과정, 대화, 원시 로그를 덤프하지 않는다. 불필요한 항목은 생략할 수 있지만 결과·검증·남은 사항·상태는 확인 가능해야 한다. 없는 사항은 `없음`이라 쓰고, 실행하지 않은 검증을 수행했다고 쓰지 않는다.

```markdown
---
ticket: AO-YYYYMMDD-NNN
title: 짧고 구체적인 업무 제목
date: YYYY-MM-DD
status: COMPLETED
size: M
estimated_md: 1.5
final_md: 2.0
project: generic-project
type: core
agents:
  - Implementer
  - Reviewer
  - QA
models: []
---
# Ticket ID · 업무 제목

Ticket: [발급한 Ticket ID]

## 요청
## 수행 결과
## 변경 사항
## 주요 결정
## 검증
## 남은 사항
## 참여 Agent
## 상태
COMPLETED / PARTIAL / BLOCKED
```

`INDEX.md`에는 보고서마다 `YYYY-MM-DD | Ticket ID | 제목 | 상태 | Size | MD | [[Reports/YYYY/MM/Ticket-ID-작업명]]` 한 줄을 추가한다. 기존 구조에 Ticket ID를 추가하며 과거 행은 소급 변경하지 않는다. 같은 티켓의 후속 결과는 해당 행을 갱신한다. 과거 작업을 찾을 때는 INDEX를 먼저 읽고 관련 보고만 연다.

중요한 아키텍처·API·상태 관리·공통 규칙·후속 기술 선택이나 기존 방식에서 새 방식으로 바꾼 결정만 `Decisions/DECISIONS.md`에 Ticket ID, 이유와 관련 보고 링크를 남긴다. 보고서 전체를 복제하지 않는다. 예: `- YYYY-MM-DD | Ticket: AO-YYYYMMDD-NNN | 결정: 새 방식 채택 | 이유: ... | 보고: [[Reports/YYYY/MM/Ticket-ID-작업명]]`

metadata에는 실제 확인된 값만 기록한다. `agents`는 실제 참여 역할, `models`는 확인된 실제 모델만 담으며 요청 모델은 본문의 requested_model에 분리한다. 알 수 없는 Size·MD·project·type은 생략하거나 null로 두고 과거 데이터를 임의로 채우지 않는다. `final_md`는 선택 사항이며 INDEX는 final_md, 없으면 estimated_md를 사용한다. 공수 차이가 크면 Report에 짧은 이유를 추가할 수 있다. 저장·색인·Decision 갱신 뒤 Workspace 규칙의 generator를 실행한다.
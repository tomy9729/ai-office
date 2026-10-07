# Plan 및 보고 템플릿

공통 작성 기준은 [SKILL.md의 공통 응답·문서 스타일](../SKILL.md#공통-응답문서-스타일)을 따릅니다. 결론·키워드 우선, 비교는 표, 절차·항목은 목록. 문서의 필수 정보는 유지하고 줄 수를 강제하지 않습니다.

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

기본은 `[Role] · [Model Full Name] · [Task]`이며 명시적으로 요청한 모델 이름과 버전을 우선 사용한다. 새 생성마다 지원 모델을 task에 맞게 먼저 선택하고 model 인자로 명시 요청한다. 명시 요청을 지원하지 않는 도구에서는 확실하게 확인된 실제 상속 모델을 사용한다. 둘 다 불가능하면 제한을 보고하고 모델 없는 이름으로 생성하지 않는다. 요청 모델은 실제 적용 여부가 미확인이어도 제목과 task_name에 넣되 requested_model과 actual_model을 별도로 기록한다. 부모 상속을 확정 모델처럼 추측하지 않는다.

- `Implementer · 6.1 Sol · AI Office Core 보고 규칙 수정`
- `Reviewer · 6 Astra · Core 변경 diff·회귀 위험 검토`
- `QA · 5.6 Luna · 설치·업데이트 절차 동작 검증`
- `Explorer · 6.1 Sol · 로그인 API 호출 흐름 조사` (requested_model: gpt-6.1-sol, actual_model: 미확인)

현재 collaboration.spawn_agent 호출의 task_name에 아래 이름을 실제로 전달하고 메시지·보고에 원래 제목을 병기한다. 모델 약칭은 family+점 없는 버전이며 task는 action+target으로 짧게 쓴다. 생성 전에 실제 Role, 모델 약칭과 명시 요청값의 일치(명시 요청 미지원이면 확인된 실제 모델과의 일치), action_target의 수행 내용과 대상을 확인한다. fork_turns는 none 또는 필요한 양의 이력 수로 지정하고 필요한 맥락을 메시지로 전달한다. all 때문에 모델 요청을 생략하지 않는다. 생성 직후 list_agents의 agent_name 경로가 전달한 task_name을 포함하는지 확인한다.

| task_name | 표시 제목 |
|---|---|
| `explorer_sol61_trace_login_api` | Explorer · 6.1 Sol · 로그인 API 호출 흐름 조사 |
| `implementer_sol61_fix_ap_tree` | Implementer · 6.1 Sol · AP 트리 수정 |
| `reviewer_astra6_review_chart_diff` | Reviewer · 6 Astra · 차트 diff 검토 |
| `qa_luna56_check_tree_selection` | QA · 5.6 Luna · 트리 선택 동작 검증 |
| `explorer_sol61_trace_agent_names` | Explorer · 6.1 Sol · Codex Agent 목록 이름 흐름 조사 |

작성·runtime 적용과 정확한 UI 표시의 제한은 [SKILL.md](../SKILL.md)의 담당자 표시 제목을 따른다.

## Agent 할당

```text
Ticket: [발급한 Ticket ID]
Title: [업무 제목]
task_name (실제 생성 인자): role_model_action_target (모델 필수)
표시 제목: [Role] · [Model Full Name] · [Task]
model (실제 생성 인자): task에 맞게 선택한 지원 모델
fork_turns: none 또는 필요한 양의 이력 수
requested_model: 명시 요청값 (도구가 명시 요청을 지원하지 않으면 없음)
actual_model: 실제 확인값 또는 미확인
역할 / 목적:
담당 범위:
필수 제약: 공통 응답·문서 스타일 전달 (결론·키워드 우선, 기본 답변 1~3줄, 비교 표·절차 목록, 필수 정보 유지)
필요한 맥락:
기대 결과:
검증 기준:
```

## Agent 결과

```text
Ticket: [발급한 Ticket ID]
Title: [업무 제목]
task_name (실제 생성 인자): role_model_action_target (모델 필수)
agent_name (list_agents 실제 관측 경로):
이름 적용 확인: 일치 / 불일치 / 미확인 (전달한 task_name 포함 여부와 제한)
표시 제목: [Role] · [Model Full Name] · [Task]
requested_model: 명시 요청값 (도구가 명시 요청을 지원하지 않으면 없음)
actual_model: 실제 확인값 또는 미확인
Role / task:
Result:
Evidence (paths, commands, observed behavior):
Validation (run / not run, actual outcome):
Limitations or blocker:
```

## Agent Report

Ticket: [발급한 Ticket ID]

필요한 경우 실제 사용한 agent만 기록한다. Complexity는 선택적인 상대 난이도이며 유용할 때만 low/medium/high로 적는다.

| Agent identifier / 표시 제목 | Role | Task | Model (requested_model / actual_model) | Complexity | Result |
|---|---|---|---|---|---|
| explorer_sol61_trace_login_api / Explorer · 6.1 Sol · 로그인 API 호출 흐름 조사 | Explorer | 조사 범위 | requested_model: gpt-6.1-sol / actual_model: gpt-6.1-sol 확인 | 선택 | 완료 및 근거 |
| implementer_sol61_update_report_rules / Implementer · 6.1 Sol · AI Office Core 보고 규칙 수정 | Implementer | 수정 범위 | requested_model: gpt-6.1-sol / actual_model: 미확인 | 선택 | 변경 및 검증 |

Max Parallel: [관측된 최대 동시 Agent 수; Main 제외]

이름과 제목에 요청 모델을 사용해도 실제 적용 여부가 확인된 것은 아니다. requested_model과 actual_model을 구분한다.

## 짧은 완료 보고 예시

```text
완료
검증: PASS · 변경 파일: 3개
남은 사항: 없음
```

대화용 축약 예시이며 기록 대상 작업의 필수 보고 항목과 완료 조건은 아래 규칙을 유지합니다. 실제 결과·검증·남은 사항에 맞춰 작성합니다.

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
# Plan 및 보고 템플릿

공통 작성 기준은 [SKILL.md의 공통 응답·문서 스타일](../SKILL.md#공통-응답문서-스타일)을 따릅니다. 항목명은 굵게 쓰고 자연스러운 문장과 충분한 근거를 사용합니다. 비교·배정은 표를 사용하고 길이를 제한하지 않습니다. 모든 착수·진행·최종 응답이 보고이며 일반 질의응답·아이디어·확인 질문도 짧은 보고로 작성합니다. 상위 지침과 사용자 명시 출력 제약을 우선하며 Plan Mode는 기존 단일 `<proposed_plan>`을 유지합니다. 채팅 양식 때문에 매 응답마다 파일을 만들지 않습니다.

## Ticket 정보

```text
Ticket: AO-YYYYMMDD-<전체 UUID>
Title: 짧고 구체적인 업무 제목
Work Status: COMPLETED / PARTIAL / BLOCKED
Status (전체): COMPLETED / PARTIAL / BLOCKED
Size: S / M / L
Estimated MD: 업무량 추정값
Final MD: 종료 시 보정값 (선택)
Report / Decision: 관련 기록 링크 또는 없음
```

티켓 비대상 작업에서는 Ticket과 Title 필드를 생략한다. 위 Ticket 정보는 기존 업무·기록용 metadata이며 Plan Mode의 현재 단계나 티켓 발급을 강제하지 않는다. 발급·예약·후속 요청 규칙은 [SKILL.md](../SKILL.md)의 업무 티켓을 따른다. 상태는 별도 생명주기가 아닌 기존 최종 보고 상태다. 동시 발급 가능성을 배제할 수 없으면 전체 UUID를 기본으로 사용한다. 순번 예시는 직렬 발급과 배타적 예약이 가능한 환경에만 적용한다.

## Plan Mode 업무 계획서

AI Office가 활성화된 Plan Mode의 최종 계획은 별도 명령 없이 `<proposed_plan>` 안에 `AI OFFICE · WORK ORDER`와 실행 계획을 하나의 문서로 작성한다. 계획 파일 생성은 요구하지 않는다. 실제 답변은 S/M/L 중 하나만 선택해 `<proposed_plan>` 블록 하나만 출력한다. 아래 S/M/L은 작성 양식과 업무 예시이며 실제 조사·배정·수행 완료를 주장하지 않는다. 대괄호 항목은 확인한 사실과 결정으로 채우고 해당 없는 선택 항목은 삭제한다.

Plan Mode에서는 읽기 전용으로 조사하고 구현에 중요한 미확정 사항을 최종 계획 전에 해소한다. 명시적 요구사항과 조사로 확정할 암묵적 요구사항을 구분한다. 코드 수정·Agent 구현 시작·commit·push는 실행으로 전환한 뒤 진행한다. 배정은 실행 예정이며 Main은 분석·판단·통합, Sub Agent는 구현·검증·commit을 담당한다. 기존 공식 Role을 사용하며 Researcher/Developer는 Explorer/Implementer의 설명용 별칭이다. 실행 시 표의 매핑을 따르고 변경이 필요하면 실제 이유를 설명한다.

업무 개요에는 업무명·목적·Main 책임·Size·Estimated MD·실제 위험을 담는다. MD는 업무량이며 일정이 아니다. 우선순위는 작업 순서를 결정할 때만 추가하고 현재 단계는 `계획 수립`으로 쓴다. 기존 AO 티켓이 있으면 제목 아래 Ticket을 한 번 표시하고 없으면 항목을 생략한다. 계획을 위해 티켓·새 번호·Report 예약을 만들지 않는다. 보고자는 `Main · 업무 조율`, 명시 요청한 모델은 requested_model로 표시하며 요청이 없으면 모델 항목을 생략한다.

### S · 단일 수정 양식

작은 작업은 Implementer 한 명으로 구현과 필요한 검증을 맡길 수 있다. Reviewer·QA의 별도 배정은 의무가 아니다.

```markdown
<proposed_plan>
# AI OFFICE · WORK ORDER
**보고자:** Main · 업무 조율

**업무명·목적:** 조회 후 선택 상태 초기화 · [사용자가 원하는 동작]
**Main 책임:** [확인한 원인에 따른 수정 판단과 결과 통합·최종 확인]
**규모·공수:** Size: S · Estimated MD: [업무량 추정]
**현재 단계:** 계획 수립
**요구사항:** 명시적: [요청 내용]. 암묵적: [호출 흐름 조사로 확정한 기존 동작 보존 조건].
**범위·순서:** [확인한 대상 경로]에서 [최소 수정] → [회귀 확인] → Main 통합·최종 확인 → 실행 모드의 Core 변경이면 commit·push.

| 담당 예정 Role | 범위 | 기대 산출물 | 검증 기준 |
|---|---|---|---|
| Implementer | [수정·검증·필요한 commit 범위] | [최소 diff와 실제 검증 결과] | [문제가 사라지고 기존 동작이 유지되는 조건] |

**위험·완료 기준:** [실제 회귀 위험과 대응]. [검증·Main 확인 및 필요한 Git 반영까지 완료하는 조건].
</proposed_plan>
```

### M · 여러 파일 작업 양식

완료한 읽기 전용 조사와 실행 단계의 남은 검증을 분리한다. 구현을 결정할 정보가 부족하면 최종 양식 작성 전에 조사하거나 질문한다.

```markdown
<proposed_plan>
# AI OFFICE · WORK ORDER
**Ticket:** [이미 발급된 AO 티켓이 있을 때만 표시]
**보고자:** Main · 업무 조율

## 업무 개요
**업무명·목적:** 로그인 오류 처리 정리 · [원하는 사용자 동작]
**Main 책임:** [실제 흐름 분석·수정 방향 판단·결과 통합·최종 확인]
**규모·공수:** Size: M · Estimated MD: [업무량 추정]
**현재 단계:** 계획 수립

## 요구사항과 조사
**명시적 요구사항:** [사용자가 요청한 동작과 필수 제약]
**암묵적 요구사항:** [조사로 확정한 기존 API·상태·UI 보존 조건]
**완료한 조사:** [읽은 경로·호출 흐름·근거와 그에 따른 구현 결정]
**남은 실행 검증:** [수정 뒤 확인할 오류/정상 경로와 회귀 검증]

## 배정과 실행 계획
| 담당 예정 Role | 범위 | 기대 산출물 | 검증 기준 |
|---|---|---|---|
| Implementer | [확인한 파일의 구현·검증·필요한 commit] | [변경 diff와 검증 결과] | [요구사항에 연결된 실제 확인 조건] |

**순서·범위:** [확정한 수정 순서와 파일/경계] → [검증] → Main 통합·최종 확인 → 실행 모드의 Core 변경이면 commit·push.

## 위험과 완료 기준
**위험·대응:** [실제 실패·회귀 위험과 필요한 대응]
**완료 기준:** [명시/암묵적 요구 충족·필요한 검증·Main 확인과 Git 반영 조건]
</proposed_plan>
```

### L · 의존성과 통합이 있는 작업 양식

M의 내용에 필요한 항목만 확장한다. 아래 아키텍처·병렬·독립 QA·롤백이 해당 없으면 제거하며 모든 역할이나 단계를 의무 배정하지 않는다.

```markdown
<proposed_plan>
# AI OFFICE · WORK ORDER
**보고자:** Main · 업무 조율

## 업무 개요
**업무명·목적:** 공통 API 처리 변경 · [변경을 통해 해결할 문제]
**Main 책임:** [영향 판단·경계와 통합 순서 결정·최종 확인]
**규모·공수:** Size: L · Estimated MD: [업무량 추정]
**현재 단계:** 계획 수립
**명시적 요구사항:** [요청한 동작·호환성·필수 제약]
**암묵적 요구사항:** [조사로 확정한 호출자·오류·상태 유지 조건]
**완료한 조사:** [실제 경로·호출 흐름·의존성과 근거]
**남은 실행 검증:** [변경 뒤 확인할 통합·회귀 범위]

## 배정과 실행 계획
| 담당 예정 Role | 범위 | 기대 산출물 | 검증 기준 |
|---|---|---|---|
| Implementer A | [공통 처리 구현·검증·필요한 commit] | [공통 diff와 검증 결과] | [호출자 계약 보존] |
| Implementer B | [겹치지 않는 호출자 적용·검증] | [호출자 diff와 검증 결과] | [정상·오류 경로 보존] |
| QA | [독립 검증이 필요한 통합 범위] | [실제 통합 검증 결과] | [회귀 시나리오와 실패 조건] |

**아키텍처·결정:** [기존 구조를 재사용한 확정 방향과 필요한 결정의 근거]
**의존성·순서:** [선행 산출물] → [의존 구현] → [통합 검증] → Main 통합·최종 확인 → 실행 모드의 Core 변경이면 commit·push.
**병렬·통합:** [독립 범위만 병렬로 배정하는 조건과 공유 파일의 순차 통합 책임]
**테스트:** [요구사항별 최소 검증과 필요한 통합·회귀 검증]
**롤백:** [실제 실패 조건과 안전하게 되돌릴 단위·방법]
**위험·완료 기준:** [실제 위험과 대응]. [요구 충족·통합·검증·Main 확인과 Git 반영 조건].
</proposed_plan>
```

## Plan Mode 밖의 계획

복잡하거나 영향이 큰 변경은 실제 파일과 흐름을 읽은 뒤 초기 방향을 10줄 이내로 요약하고 필요하면 위 Execution Plan 항목을 사용한다. 10줄 기준은 Plan Mode의 전체 업무 계획서를 제한하지 않는다. 작은 변경에는 별도 계획을 만들지 않고 기존 업무 채팅 보고 양식을 사용한다. 장식용 부서·새 식별자·회의·결재자·시간 기록·직급·대화/상태 로그는 추가하지 않는다.

## 담당자 목록 이름과 생성 인자 예시

기본은 `[Role] · [Model Full Name] · [Task]`이며 명시적으로 요청한 모델 이름과 버전을 표시 기준으로 사용한다. 새 생성마다 지원 모델을 task에 맞게 먼저 선택하고 지원하는 도구에서는 model 인자로 명시 요청한다. 요청이 없으면 독립적으로 확인된 모델을 표시 기준으로 사용할 수 있다. 둘 다 없으면 모델을 생략한 `Role · Task`와 `role_action_target`으로 생성한다. 명시 요청값은 requested_model에 기록하고 요청이 없으면 항목을 생략한다. 실행 모델 확인 여부는 별도로 출력하지 않으며 부모 상속을 추측하거나 요청값을 확인값으로 간주하지 않는다.

- `Implementer · 6.1 Sol · AI Office Core 보고 규칙 수정`
- `Reviewer · 6 Astra · Core 변경 diff·회귀 위험 검토`
- `QA · 5.6 Luna · 설치·업데이트 절차 동작 검증`
- `Explorer · 6.1 Sol · 로그인 API 호출 흐름 조사` (requested_model: gpt-6.1-sol)

현재 collaboration.spawn_agent 호출의 task_name에 아래 이름을 실제로 전달한다. 할당 메시지에는 원래 제목을 병기하고 채팅 보고에서는 담당 직무·업무 항목에 넣는다. 모델 약칭은 family+점 없는 버전이며 task는 action+target으로 짧게 쓴다. 생성 전에 실제 Role, 모델 약칭과 명시 요청값의 일치(요청이 없으면 독립적으로 확인된 모델과 비교하며 둘 다 없으면 모델 검사 생략), action_target의 수행 내용과 대상을 확인한다. fork_turns는 none 또는 필요한 양의 이력 수로 지정하고 필요한 맥락을 메시지로 전달한다. all 때문에 모델 요청을 생략하지 않는다. 생성 직후 list_agents의 agent_name 경로가 전달한 task_name을 포함하는지 확인한다.

| task_name | 표시 제목 |
|---|---|
| `explorer_trace_login_api` | Explorer · 로그인 API 호출 흐름 조사 |
| `explorer_sol61_trace_login_api` | Explorer · 6.1 Sol · 로그인 API 호출 흐름 조사 |
| `implementer_sol61_fix_ap_tree` | Implementer · 6.1 Sol · AP 트리 수정 |
| `reviewer_astra6_review_chart_diff` | Reviewer · 6 Astra · 차트 diff 검토 |
| `qa_luna56_check_tree_selection` | QA · 5.6 Luna · 트리 선택 동작 검증 |
| `explorer_sol61_trace_agent_names` | Explorer · 6.1 Sol · Codex Agent 목록 이름 흐름 조사 |

명시 요청이 없고 독립적으로 확인된 모델도 없으면 표시 제목은 `Role · Task`, 생성 인자는 `role_action_target`을 사용하고 requested_model 항목은 생략한다. 이 규칙은 할당과 결과 양식에도 적용한다. 작성·runtime 적용과 정확한 UI 표시의 제한은 [SKILL.md](../SKILL.md)의 담당자 표시 제목을 따른다.

## Agent 할당

네 묶음에 작업별 사실을 먼저 담는다. 원본 접근이 불가능하면 필요한 역할·보고 지침을 메시지에 포함한다.

```text
문제·완료 조건: [문제와 요구 결과]
담당 범위·작업 경계: [파일·책임·다른 담당자 경계]. 다른 담당자의 변경을 되돌리지 않는다.
보존할 동작: [기존 계약·상태·필수 제약]
검증 방법과 기대 결과: [명령·시나리오, 잡으려는 실패, 통과 조건]
Ticket / Title: [발급된 ID와 업무 제목; 비대상이면 생략]
표시 제목 / task_name: [Role · Model · Task / role_model_action_target; 모델 정보가 없으면 Role · Task / role_action_target]
requested_model / fork_turns: [실제 요청값 / none 또는 필요한 이력 수; 미요청 모델 항목 생략]
공통 지침: [접근 가능한 역할 TOML과 SKILL 보고 규칙 링크]
```

예: UI 재조회에서 이전 선택이 남는 문제를 배정할 때, 기존 선택·해제 동작을 보존하고 새 조회의 선택 초기화 시나리오를 검증 조건으로 적는다. 권한 변경은 독립 Reviewer와 권한 경계 검증이 필요하다. 선택 기준은 [SKILL.md](../SKILL.md#최소-절차와-검증-선택)를 따른다.

## Agent 결과

Sub Agent의 채팅 결과는 아래 담당자 보고 양식을 사용한다. 제목과 발급된 Ticket 다음에 보고자를 표시하며 티켓 미발급이면 제목 바로 다음에 표시한다. Sub Agent는 [SKILL.md의 공통 응답·문서 스타일](../SKILL.md#공통-응답문서-스타일)에 있는 실제 배정 Role과 기존 직무의 대응을 사용한다. 식별·관측·요청 모델 정보는 담당 직무·업무 안에 유지하고 직무별 양식을 추가하지 않는다.

```markdown
### 담당자 보고 · 업무명
**Ticket:** [발급한 Ticket ID]
**보고자:** [실제 배정 Role] · [해당 기존 직무]

**담당 직무·업무:** [Role과 담당 범위를 설명한다.]

| 식별·모델 항목 | 전달값 또는 실제 확인값 |
|---|---|
| task_name (실제 생성 인자) | role_model_action_target (모델 정보가 없으면 role_action_target) |
| agent_name (list_agents 실제 관측 경로) | 관측값 또는 미확인과 이유 |
| 이름 적용 확인 | 일치 / 불일치 / 미확인과 전달한 task_name 포함 여부·제한 |
| 표시 제목 | [Role] · [Model Full Name] · [Task] |
| requested_model | 명시 요청값 (요청이 없으면 행 생략) |

**수행 결과:** [바꾼 파일과 동작 또는 조사 결과를 설명한다.]

**근거·검증:** [경로·명령·관측 동작과 검증 실행 여부·실제 결과를 쓴다. 실행하지 않았다면 `미실행`과 이유를 명시한다.]

**제한·인계 사항:** [blocker와 Main이 이어서 확인할 내용 또는 없음.]
```

## Agent Report

Ticket: [발급한 Ticket ID]

필요한 경우 실제 사용한 agent만 기록한다. Complexity는 선택적인 상대 난이도이며 유용할 때만 low/medium/high로 적는다.

| Agent identifier / 표시 제목 | Role | Task | Model (requested_model) | Complexity | Result |
|---|---|---|---|---|---|
| explorer_sol61_trace_login_api / Explorer · 6.1 Sol · 로그인 API 호출 흐름 조사 | Explorer | 조사 범위 | requested_model: gpt-6.1-sol | 선택 | 완료 및 근거 |
| implementer_sol61_update_report_rules / Implementer · 6.1 Sol · AI Office Core 보고 규칙 수정 | Implementer | 수정 범위 | requested_model: gpt-6.1-sol | 선택 | 변경 및 검증 |

Max Parallel: [관측된 최대 동시 Agent 수; Main 제외]

Model 열에는 명시 요청한 requested_model만 적으며 요청이 없으면 생략한다. 요청값을 실행 모델의 확인값으로 간주하지 않는다.

## 업무 채팅 보고 예시

공통 제목은 `### 보고 구분 · 업무명`이며 티켓을 발급했을 때만 제목 아래에 한 번 적는다. 모든 보고는 제목과 발급된 Ticket 다음에 보고자를 표시하며 티켓이 없으면 제목 바로 다음에 표시한다. 아래 양식은 모든 채팅 답변의 단계와 내용에 맞게 적용하며 별도 파일 생성 예시가 아니다. 전송 전 제목·보고자·본문과 발급된 Ticket 배치를 확인하고 누락을 보완한다. 결과와 검증·제한은 실제 상황에 맞게 설명한다.

### 짧은 답변·확인 보고

단순 질문·아이디어·확인에는 핵심 답변과 필요한 확인·제한만 담는다. 해당 없는 항목과 티켓은 생략하며 양식 적용만으로 티켓이나 저장 파일을 만들지 않는다. 보고자는 실제 담당 Role을 사용한다.

```markdown
### 답변 보고 · 파일 저장 규칙
**보고자:** Main · 업무 조율

**핵심 답변:** 채팅 보고 양식은 항상 적용하지만 파일 저장은 기록 대상 작업에만 적용합니다.
```

```markdown
### 확인 보고 · 수정 대상
**보고자:** Main · 업무 조율

**핵심 답변:** 확인된 호출 흐름을 기준으로 수정 범위를 좁혔습니다.
**확인·제한:** 수정 대상은 목록 화면과 상세 화면 중 어느 쪽인가요?
```

### Main 착수 보고

```markdown
### 착수 보고 · 트리 선택 상태 수정
**Ticket:** AO-YYYYMMDD-NNN
**보고자:** Main · 업무 조율

**요청 이해:** 목록을 새로 조회한 뒤에도 이전 선택 상태가 남는 문제를 수정하겠습니다.

**수행 계획:** 선택 상태를 설정하는 호출 경로와 기존 초기화 처리를 확인하고 담당자에게 최소 수정을 배정하겠습니다.

**완료 기준:** 새 조회 결과의 선택 상태가 요구사항과 일치하고, 기존 선택·해제 동작의 검증과 Main의 diff 확인이 끝나야 합니다.
```

### Main 진행 보고

```markdown
### 진행 보고 · 트리 선택 상태 수정
**Ticket:** AO-YYYYMMDD-NNN
**보고자:** Main · 업무 조율

**핵심 확인 내용:** 새 조회에서 선택 상태를 초기화하지 않는 경로를 확인했습니다.

**현재 결과:** 해당 경로의 수정과 diff 검토는 끝났지만 테스트 서버 접속이 실패해 화면 검증이 차단되었습니다.

**다음 작업:** 서버 접속이 복구되면 화면 검증을 실행하겠습니다. 현재 업무 상태는 BLOCKED이며 접속 복구가 필요합니다.
```

### Main 간소 결과 보고

제한적 문구 변경 등 작은 작업에 사용하며 필수 정보를 세 묶음으로 유지한다.

```markdown
### 결과 보고 · 버튼 문구 수정
**Ticket:** [발급한 ID; 없으면 생략]
**보고자:** Main · 업무 조율

**결과·변경:** [결과 요약과 바꾼 파일·동작]
**검증·제한:** [실행 여부·결과와 남은 사항. 미실행이면 이유]
**상태·후속 조치:** 업무 COMPLETED · 기록 완료 · 전체 COMPLETED · 남은 조치 없음.
```

기록 실패 예: `업무 COMPLETED · 기록 차단 — Dashboard 생성: 권한 거부 · 전체 BLOCKED · 남은 조치: 권한 복구 후 같은 티켓의 Dashboard 단계 재개`.

### Main 결과 보고

```markdown
### 결과 보고 · 트리 선택 상태 수정
**Ticket:** AO-YYYYMMDD-NNN
**보고자:** Main · 업무 조율

**결과 요약:** 재조회 시 이전 선택 상태가 남는 문제를 수정했습니다.

**수행 내용:** 선택 상태 초기화 경로를 수정했고 담당자의 결과와 변경 diff를 통합·확인했습니다.

**검증:** 새 조회와 기존 선택·해제 동작을 화면에서 확인했고 필요한 리뷰와 검증은 통과했습니다.

**남은 사항:** Report와 INDEX는 저장했지만 Dashboard 최신화가 남아 있습니다. 업무는 완료됐으며 기록은 미완료입니다.

**업무:** COMPLETED

**기록:** 미완료

**전체 상태:** PARTIAL

**남은 조치:** Dashboard를 생성하고 저장 결과를 확인하겠습니다.
```

### Sub Agent 담당자 보고

```markdown
### 담당자 보고 · 보고 양식 문서 수정
**Ticket:** AO-YYYYMMDD-NNN
**보고자:** Implementer · 개발 담당

**담당 직무·업무:** Implementer로 보고 규칙과 템플릿 문서를 수정했습니다.

| 식별·모델 항목 | 전달값 또는 실제 확인값 |
|---|---|
| task_name | implementer_sol61_update_report_rules |
| agent_name | /root/implementer_sol61_update_report_rules |
| 이름 적용 확인 | 관측 경로가 전달한 task_name을 포함하여 일치합니다. 정확한 앱 UI 표시는 미확인입니다. |
| 표시 제목 | Implementer · 6.1 Sol · 보고 양식 문서 수정 |
| requested_model | gpt-6.1-sol |

**수행 결과:** SKILL.md와 references/templates.md의 채팅 보고 항목을 수정했습니다.

**근거·검증:** 변경 diff와 git diff --check를 확인했고 공백 오류가 없었습니다. 앱 테스트: 미실행 — 실행 코드를 변경하지 않았기 때문입니다.

**제한·인계 사항:** Main의 요구사항 대조와 최종 리뷰가 남아 있습니다.
```

## 최종 보고와 기록

채팅 보고 양식과 아래 저장 보고서의 metadata·제목·저장 정책은 별개다. 저장 보고서는 `# Ticket ID · 업무 제목`을 유지하며 매 채팅 응답마다 생성하지 않는다. 기록 대상과 완료 조건은 [SKILL.md](../SKILL.md)의 보고 규칙을 따른다. Workspace 설정이 없으면 대화의 최종 보고로 충분하다. 지정되어 있으면 보고서는 `<Workspace>/Reports/YYYY/MM/Ticket-ID-작업명.md`에 저장하며 INDEX와 필요한 결정 기록도 갱신한다. 순번 티켓은 발급 때 예약한 파일을 최종 보고로 갱신한다. 날짜는 사용자 또는 프로젝트의 `report_timezone` 기준이며 없으면 제공된 현지 시간, 그것도 없으면 UTC를 사용하고 표시한다. 다른 작업의 기존 파일은 덮어쓰지 않는다. 신규 순번 예약이 충돌하면 목록을 다시 확인하고 다음 번호를 발급하며 작업명 suffix로 번호 충돌을 회피하지 않는다. 안전한 순번 발급이 불가능하면 전체 UUID 대체 형식과 제한을 보고한다. 짧고 실용적으로 쓰며 사고 과정, 대화, 원시 로그를 덤프하지 않는다. 불필요한 항목은 생략할 수 있지만 결과·검증·남은 사항·상태는 확인 가능해야 한다. 없는 사항은 `없음`이라 쓰고, 실행하지 않은 검증을 수행했다고 쓰지 않는다.

```markdown
---
ticket: AO-YYYYMMDD-NNN
title: 짧고 구체적인 업무 제목
date: YYYY-MM-DD
status: COMPLETED
work_status: COMPLETED
recording_issue: null
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
업무: COMPLETED / PARTIAL / BLOCKED
기록: 완료 / 미완료 / 차단 / 해당 없음
전체: COMPLETED / PARTIAL / BLOCKED
남은 조치: 없음 또는 구체적인 조치
```

`INDEX.md`에는 보고서마다 `YYYY-MM-DD | Ticket ID | 제목 | 전체 상태 | 업무 상태 | Size | MD | [[Reports/YYYY/MM/Ticket-ID-작업명]]` 한 줄을 추가한다. 기존 구조에 Ticket ID를 추가하며 과거 행은 소급 변경하지 않는다. 같은 티켓의 후속 결과는 해당 행을 갱신한다. 과거 작업을 찾을 때는 INDEX를 먼저 읽고 관련 보고만 연다.

중요한 아키텍처·API·상태 관리·공통 규칙·후속 기술 선택이나 기존 방식에서 새 방식으로 바꾼 결정만 `Decisions/DECISIONS.md`에 Ticket ID, 이유와 관련 보고 링크를 남긴다. 보고서 전체를 복제하지 않는다. 예: `- YYYY-MM-DD | Ticket: AO-YYYYMMDD-NNN | 결정: 새 방식 채택 | 이유: ... | 보고: [[Reports/YYYY/MM/Ticket-ID-작업명]]`

metadata에는 실제 확인된 값만 기록한다. `agents`는 실제 참여 역할, `models`는 확인된 실제 모델만 담으며 요청 모델은 본문의 requested_model에 분리한다. 요청값을 확인값으로 간주하거나 models metadata에 복사하지 않는다. 알 수 없는 Size·MD·project·type은 생략하거나 null로 두고 과거 데이터를 임의로 채우지 않는다. `final_md`는 선택 사항이며 INDEX는 final_md, 없으면 estimated_md를 사용한다. 공수 차이가 크면 Report에 짧은 이유를 추가할 수 있다. 저장·색인·Decision 갱신 뒤 Workspace 규칙의 generator를 실행한다.
업무 완료 조건은 [SKILL.md](../SKILL.md#보고와-완료), metadata와 기록 재개·복구 절차는 [workspace.md](workspace.md#업무와-기록-완료)를 따른다. 선택 문자열 recording_issue에는 확인된 기록 실패 단계와 이유만 적으며 생략·빈 값·null은 이유 미기록이다. 해결되면 생략하거나 null로 갱신한다. 과거 이유는 추정하지 않는다.

큰 재작업·재위임에만 확인된 이유(모델 선택·맥락 부족·요구 변경)를 본문에 짧게 남긴다. 재발 버그·중요한 기술 선택의 재사용 지식은 `원인 → 다음 판단 기준 → 근거 링크`로 기존 Report·Decision을 갱신한다.

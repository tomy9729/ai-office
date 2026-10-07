# Plan 및 보고 템플릿

## Plan 요약

10줄 이내로 목적, 현재/원하는 동작, 주요 파일과 호출 흐름, 핵심 방향, 필수 제약, 영향 범위, 결과 중심 검증을 적는다. 확인하지 않은 구현 세부는 고정하지 않는다.

## Execution Plan

Team: [선택한 조합 / 없음 / 사용자 정의]

Agent instances: [고유 이름과 역할]

Parallel groups: [독립 작업 그룹 또는 없음]

초기안이며 조사 결과에 따라 갱신한다.

| Phase | Agent instances / Role | Model | Task / Scope | Risk | Depends on | Check |
|---|---|---|---|---|---|---|
| 조사 | Explorer #1 | 선택 근거와 요청/확인 구분 | 조사 범위 | low/medium/high 또는 생략 | 없음 | 근거·경로·흐름 |
| 구현 | Implementer #1 | 선택 근거와 요청/확인 구분 | 결정된 수정 범위 | low/medium/high 또는 생략 | 조사 결과 | 변경 동작·검증 |
| 확인 | Reviewer 또는 QA | 선택 근거와 요청/확인 구분 | 독립 diff 또는 실행 확인 | low/medium/high 또는 생략 | 구현 완료 | finding·실제 결과 |
| 통합 | Main | Main | 충돌 해결·최종 확인 | — | 위 결과 | 요구사항과 diff 대조 |

Implementation이 필요한 Bugfix에는 Implementer를 최소 1개 배정한다. 조사만 하고 끝나는 버그 분석은 예외다.

### 작은 작업 축약

`[Role] — [담당 일과 범위] — [모델 선택 근거] — [결과/검증]`

## Agent 할당

```text
역할 / 목적:
담당 범위:
필수 제약:
필요한 맥락:
기대 결과:
검증 기준:
```

## Agent 결과

```text
Role / task:
Result:
Evidence (paths, commands, observed behavior):
Validation (run / not run, actual outcome):
Limitations or blocker:
```

## Agent Report

필요한 경우 실제 사용한 agent만 기록한다. Complexity는 선택적인 상대 난이도이며 유용할 때만 low/medium/high로 적는다.

| Agent instance | Role | Task | Model (requested / confirmed) | Complexity | Result |
|---|---|---|---|---|---|
| Explorer #1 | Explorer | 조사 범위 | 요청 / 확인 여부 | 선택 | 완료 및 근거 |
| Implementer #1 | Implementer | 수정 범위 | 요청 / 확인 여부 | 선택 | 변경 및 검증 |

Max Parallel: [관측된 최대 동시 Agent 수; Main 제외]

확인하지 않은 모델은 요청 모델과 구분한다.

## 최종 보고와 기록

기록 대상과 완료 조건은 [SKILL.md](../SKILL.md)의 보고 규칙을 따른다. `report_repository`가 없으면 대화의 최종 보고로 충분하다. 지정되어 있으면 보고서는 `<report_repository>/Reports/YYYY/MM/YYYY-MM-DD-작업명.md`에 저장하며 INDEX와 필요한 결정 기록도 갱신한다. 날짜는 사용자 또는 프로젝트의 `report_timezone` 기준이며 없으면 제공된 현지 시간, 그것도 없으면 UTC를 사용하고 표시한다. 같은 이름이 있으면 덮어쓰지 말고 `-2`처럼 식별 suffix를 붙인다. 짧고 실용적으로 쓰며 사고 과정, 대화, 원시 로그를 덤프하지 않는다. 불필요한 항목은 생략할 수 있지만 결과·검증·남은 사항·상태는 확인 가능해야 한다. 없는 사항은 `없음`이라 쓰고, 실행하지 않은 검증을 수행했다고 쓰지 않는다.

```markdown
# 작업 제목

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

`INDEX.md`에는 보고서마다 `YYYY-MM-DD | 제목 | 상태 | [[Reports/YYYY/MM/YYYY-MM-DD-작업명]]` 한 줄을 추가한다. 과거 작업을 찾을 때는 INDEX를 먼저 읽고 관련 보고만 연다.

중요한 아키텍처·API·상태 관리·공통 규칙·후속 기술 선택이나 기존 방식에서 새 방식으로 바꾼 결정만 `Decisions/DECISIONS.md`에 이유와 관련 보고 링크를 남긴다. 보고서 전체를 복제하지 않는다. 예: `- YYYY-MM-DD | 결정: 새 방식 채택 | 이유: ... | 보고: [[Reports/YYYY/MM/YYYY-MM-DD-작업명]]`

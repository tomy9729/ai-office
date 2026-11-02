# 테스트 역할 운영

현재 등록된 역할은 Planner, Explorer, Debugger, Implementer, Reviewer, TestPlanner, TestExecutor, QA, Specialist다. Questioner 역할은 없고 Main이 요구 정의와 사용자 질문을 맡는다. Main은 수용 기준·범위를 전달할 수 있지만 세부 테스트 owner가 아니다. Main과 기존 역할의 도구는 현재 runtime 및 프로젝트 규칙을 따르고, 모델은 SKILL.md의 task별 공통 선택 규칙을 따른다. 별도 모델 지정은 TestPlanner/TestExecutor만 적용한다.

## 입출력·handoff·책임

| 역할 | 입력·시작 | owner 산출물 | 종료·handoff | 도구·모델·테스트 경계 |
|---|---|---|---|---|
| Main | 사용자 요구 | 요구·수용 기준·역할 배정·통합·최종 보고 | 모호 요구는 질문, 복잡한 분석은 Planner | 코드/명령 실행은 위임, 세부 계획 owner 아님 |
| Planner | Main의 복잡한 요구분석 위임 | 요구 명세·질문안·수용 기준 | NEED_INFO/READY/PASS를 Main에 반환 | 구현·테스트 설계/실행 없음 |
| Explorer | 지정 조사 질문 | 코드·호출·영향 사실과 근거 | 지정 질문에 답하고 종료 | 광범위 테스트 설계/실행 없음 |
| Debugger | 실패 관측·증거 | 재현 protocol, 실패 결과 분석·근본 원인·수정 방향 | 수정은 Implementer, 정식 계획 실행은 TestExecutor | 원인 분석 owner; 실제 재현 실행은 TestExecutor |
| Implementer | Main의 구현 범위·제약 | 제품·테스트 코드 변경 | 변경·자체 확인 보고 | 코드 수정 owner; 테스트 계획·정식 실행 owner 아님 |
| Reviewer | diff·요구사항 | 정적 독립 리뷰와 필수 formatter/lint evidence 누락 확인 | 발견 또는 범위·제한 보고 | 실행·품질 판정 없음 |
| TestPlanner | 요구·diff·수용 기준 | 테스트 계획 JSON과 우선순위·조건·기대값 | 요구 모호하면 Main/Planner; 완료 시 Executor | 실행·코드 수정 금지. gpt-6.1-sol / medium. 중간 수준 동등 모델 허용 |
| TestExecutor | 고정 계획·최소 맥락 | 계획대로 실행한 case별 actual/evidence/status | FAIL→Debugger, NEEDS_REVIEW→TestPlanner 또는 QA, 결과→Main | gpt-6-luna / low 고정, 승격/fallback/분석/수정/품질판정 금지 |
| QA | 계획·evidence·수용 기준 | 증거 해석과 최종 품질 판단 | 근거·제한을 Main에 반환 | 중복 계획·실행 금지 |
| Specialist | Main의 제한된 전문 질문 | 전문 분석·권고 | Main에 반환 | 구현·테스트 설계/실행 없음 |

기본 순서는 `Implementer → Reviewer → TestPlanner → TestExecutor → QA`지만 위험 기반으로 필요한 역할만 생성한다. 역할 간 책임을 합치지는 않는다. 같은 계획 버전에서 같은 실패가 반복되고 새 evidence가 없으면 멈추고 Main에 반환한다. Child는 다른 child를 생성하지 않고 Main을 통해 handoff한다.

## TestPlanner 계약

계획은 JSON object이며 `version`, `working_directory`, `order`, 필요하면 `timeout_seconds`, `cleanup`, `cases`를 포함한다. 각 case는 `id`, `title`, `priority`, `type`, `precondition`, `expected`, `pass_condition`, `fail_condition`, `evidence`, `notes`가 필수고 `command` 또는 `action`이 있어야 한다. `type`은 automated/manual/browser 중 하나이고, `category`는 normal/fail/exception/boundary/regression 중 하나다. 사전조건은 배열로 구체적으로 쓰며 실제로 존재하는 실행 절차만 적는다. 브라우저 case에는 `browser: "codex_in_app"`, 실행할 URL을 포함한다.

```json
{
  "version": "1", "working_directory": ".", "order": ["TP-001", "TP-002"],
  "timeout_seconds": 10, "cleanup": "none",
  "cases": [{
    "id": "TP-001", "title": "Node 실행 기본 확인", "priority": "high",
    "type": "automated", "category": "normal",
    "precondition": ["Node.js 실행 가능"],
    "command": "node -e \"process.exit(0)\"", "expected": "exit code 0",
    "pass_condition": "exit code === 0", "fail_condition": "exit code !== 0",
    "evidence": "exit code", "notes": "파일을 수정하지 않음"
  }, {
    "id": "TP-002", "title": "앱 화면 수동 확인", "priority": "medium",
    "type": "browser", "category": "normal",
    "precondition": ["테스트 예시 제목을 제공하는 fixture 페이지가 http://127.0.0.1:4173 에서 실행 중"],
    "action": "Codex in-app browser에서 URL을 열어 화면 제목을 확인",
    "browser": "codex_in_app", "url": "http://127.0.0.1:4173",
    "expected": "화면 제목이 테스트 예시와 일치",
    "pass_condition": "실제 제목이 테스트 예시와 일치",
    "fail_condition": "실제 제목이 expected와 다름",
    "evidence": "화면 제목", "notes": "URL 또는 사전조건을 검증하지 못하면 실행하지 않음"
  }]
}
```

단지 command가 테스트처럼 보인다는 이유로 실행 안전성을 추정하지 않는다. shell/browser 부작용·파일 쓰기 경계 또는 정책 강제를 확인할 수 없으면 실행 전 BLOCKED다.

## TestExecutor 규칙과 플랫폼 한계

PASS는 `TP-001 PASS` 한 줄. FAIL은 Expected/Actual/Evidence, BLOCKED는 Reason, NEEDS_REVIEW는 Evidence만 간결히 기록한다. 진행 설명·성공 로그 전체·불필요 요약은 금지한다. case 상태는 업무/metadata 상태가 아니다. 사용자 지정 결과 형식은 공통 채팅 보고 양식에서 해당 테스트 결과 본문의 예외다.

Codex 앱 in-app browser(CUA IAB, `codex_in_app`)만 사용한다. Chrome/Edge/Firefox/external 또는 headless Chromium 실행, 이를 시작하는 Playwright/Puppeteer 명령, 시스템 브라우저 설정 변경은 금지한다. in-app browser로 수행할 수 없으면 반드시 `<id> BLOCKED: Codex in-app browser cannot execute this test.` 한 줄을 그대로 쓰고 번역·요약하거나 일반 Reason 형식으로 바꾸지 않는다.

공식 custom-agent TOML은 name/description/developer_instructions와 model/model_reasoning_effort를 지원한다. `features.shell_tool`, `features.apps`, `features.plugins`, `features.memories`, `features.request_permissions_tool`을 false로 설정할 수 있지만 `sandbox_mode`, `approval_policy`, `mcp_servers`, 임의 `allowedBrowsers`/tool deny allowlist로 역할 권한을 격리할 수 있다고 주장하지 않는다. 코드 수정 금지는 지침이지 OS 권한 제거가 아니다. 실행 제한 보장이 불가능하면 BLOCKED다. 기본 agent fallback은 `fork_turns=none`, 최소 맥락과 원본 역할 지침을 포함하고 모델·실행 제한을 강제할 수 없으면 시작하지 않는다. 새 agent_type 발견은 다음 세션에 확인한다. gpt-6-luna를 저비용 지원군으로 사용하지만 정확 요금 비교/최저가 검증은 하지 않았다. 모델 미지원은 BLOCKED, 판단 자료 부족은 NEEDS_REVIEW다.

## Owner 매트릭스

| 작업 | Main | Planner | Explorer | Debugger | Implementer | Reviewer | TestPlanner | TestExecutor | QA | Specialist |
|---|---|---|---|---|---|---|---|---|---|---|
| 요구 정의·질문 | Owner | 위임 명세 | - | - | - | - | - | - | - | - |
| 코드 조사 | 조율 | 근거 사용 | Owner | 실패 근거 | 구현 범위 | diff 범위 | 변경 이해 | 계획 내 최소 확인 | evidence 이해 | 지정 조사 |
| 제품/테스트 코드 수정 | 범위 | - | - | 수정방향 | Owner | - | - | 금지 | - | - |
| 정적 리뷰 | 통합 | - | - | - | - | Owner | - | - | 누락 참고 | - |
| 테스트 설계 | 범위·수용 기준 | 명세 | - | 진단 protocol | 테스트 코드만 | 계획 일치 여부 | Owner | 금지 | 결과 기준 이해 | - |
| 계획 실행·증거 | 위임 | - | - | 원인분석에 필요한 실행을 TestExecutor에 요청 | 자체 확인 범위만 | 누락 확인 | 금지 | Owner | evidence 참고 | - |
| 실패 원인 | 통합 | - | 사실 조사 | Owner | 배정 수정 | 회귀 영향 | 계획 명확성 | 증거만 | 결과 해석 | 전문 근거 |
| 최종 품질 판단 | 최종 통합 | - | - | - | - | 정적 검토 | - | 금지 | Owner | - |

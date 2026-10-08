# Team 조합 예시

최소 절차·독립 리뷰·QA 선택은 [SKILL.md](../SKILL.md#최소-절차와-검증-선택)가 원본이다. 아래는 초기 후보 조합이다. 필요 역할만 선택하고 인원·순서·모델을 task에 맞게 바꾼다. 팀 조합 없이 직무 하나만 사용해도 된다.

| 업무 | 후보 Concept | 기본 흐름 |
|---|---|---|
| Feature | Explorer 0~N, Implementer 1~N, Reviewer/QA/Specialist 0~N | 조사 → 구현 → 필요한 독립 리뷰와 검증 |
| Bugfix | Debugger 0~N, Explorer/Reviewer/QA 0~N, 변경이 있으면 Implementer 1~N | 재현·근본 원인 → 필요 시 수정 → 회귀 확인 |
| Refactor | Explorer 0~N, Implementer 1~N, Reviewer/QA/Specialist 0~N | 참조·영향 확인 → 좁은 변경 → 동작 보존 확인 |
| Investigation | Explorer 0~N, Debugger/Specialist 0~N | 질문별 독립 조사와 근거 수집 |
| QA | QA 1~N, Reviewer/Specialist 0~N | 변경 기반 검증 → 실패 원인/범위 보고 |

같은 Concept 여러 명은 서로 다른 가설을 독립 조사할 수 있다. 동일 파일을 읽는 일은 병렬 가능하지만, 겹치는 파일을 쓰는 일은 순차화한다. 실제 tool 동시성 한도는 세션마다 확인한다.

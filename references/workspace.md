# AI Office Workspace

Core는 운영 규칙과 범용 템플릿·generator다. Workspace는 실제 Reports·Decisions·INDEX·Dashboard 기록 공간이다. 프로젝트 코드·도메인 지식은 별도 Project Repository / Project Knowledge에 둔다. Core Git에 실제 기록·통계·회사 정보·PC 절대 경로를 넣지 않는다.

```text
<Workspace>/
├─ Dashboard/
│  ├─ Current/index.html, data.json
│  └─ Archive/
│     ├─ Daily/YYYY/MM/YYYY-MM-DD.html
│     ├─ Weekly/YYYY/YYYY-Www.html
│     └─ Monthly/YYYY/YYYY-MM.html
├─ Reports/YYYY/MM/Ticket-ID-작업명.md
├─ Decisions/DECISIONS.md
├─ INDEX.md
├─ README.md
└─ AI Office 운영 안내.md
```

설정은 프로젝트의 ai_office_workspace 또는 report_repository, 없으면 사용자의 ai_office_workspace 또는 report_repository 순서로 확인한다. report_repository는 호환 alias이며 지정 루트에 폴더를 자동으로 붙이지 않는다. 기록 공간이 없으면 대화의 보고로 충분하다. 환경별 경로는 해당 AGENTS.md에만 둔다.

## Size와 MD

| Size | 기준 |
|---|---|
| S | 작고 명확한 단일 변경 |
| M | 여러 파일 또는 여러 역할이 필요한 일반 작업 |
| L | 넓은 영향 또는 조사·구현·리뷰·QA 등 여러 단계 |

Size는 업무 범위·투입 규모이며 난이도·모델 역량·직급이 아니다. 어려운 단일 변경도 S, 많은 단순 반복 변경도 M/L일 수 있다.

MD(Man-Day)는 업무의 상대적 작업량을 사람 기준 공수로 환산한 추정치다. wall-clock·Agent 실행 시간·Token 사용량과 같지 않고 모델 성능으로 환산하지 않는다. 회계·인사 평가용 값으로 취급하지 않는다.

가이드: 0.1(작은 확인·문구), 0.25(작은 단일 파일·제한 검증), 0.5(소규모 변경), 1.0(하루 규모 일반 작업), 1.5~2.0(여러 파일·역할·리뷰·검증), 3.0 이상(넓은 영향·여러 단계). 고정 공식이 아니다. 조사·파일 수·영향·구현량·테스트·Review·QA·결정 복잡도·외부 의존성·재작업 가능성을 함께 고려한다. 같은 Size도 MD가 다를 수 있다.

시작 시 estimated_md를 Plan과 Report에 기록하고 종료 시 필요하면 final_md로 보정한다. 차이가 크면 이유를 짧게 적을 수 있으나 모든 작업에 variance 설명을 강제하지 않는다. INDEX는 final_md, 기존 md 호환값, estimated_md 순서로 사용한다. 알 수 없는 값은 null 또는 생략하고 과거 값을 추정하지 않는다.

## metadata와 생성

Report 상단 YAML은 ticket, title, date, status, size, estimated_md, final_md, project, type, agents, models를 사용한다. 본문은 기존 구조를 유지한다. status는 COMPLETED/PARTIAL/BLOCKED, date는 report_timezone의 YYYY-MM-DD, MD는 음수가 아닌 숫자다. agents/models는 실제 참여 역할과 확인된 실제 모델을 배열로 기록한다. 요청 모델은 본문에 requested_model로 분리하고 실제 모델을 추측하지 않는다. type: core는 Core 개선 집계에 사용한다. 구체 예시는 [templates.md](templates.md)를 따른다.

흐름: 업무 수행 → Report 저장 → INDEX·필요한 Decision 갱신 → generator 실행 → Current 및 해당 일·주·월 Archive 갱신. Markdown만 원본이며 data.json과 HTML은 파생 결과물이다. Report가 없거나 과거 metadata가 빠져도 오류 없이 별도 표시하거나 해당 지표에서 제외한다. 없는 MD를 0으로 간주하거나 분모에 넣어 평균을 낮추지 않는다. 업무당 평균은 final_md 우선, 기존 md 호환값, estimated_md 순서로 값이 있는 업무만 분모에 넣는다. Decision은 기존 날짜·Ticket·Report 링크의 Markdown 기록에서 읽으며 임의 날짜를 만들지 않는다.

생성 명령은 `python scripts/generate_dashboard.py --workspace <Workspace> --timezone <report_timezone>`이다. `--date YYYY-MM-DD`는 Archive의 일·주·월 기준일만 선택하며 Current와 data.json은 항상 선택 timezone의 현재일을 기준으로 최신 기록을 집계한다. 과거 날짜를 지정하면 그 날짜의 Archive만 갱신하고 현재일 Archive를 추가 생성하지 않는다. timezone 기본은 UTC이며 환경에서 날짜 기준을 명시하는 것을 권장한다. Python 표준 라이브러리로 생성하고 별도 서버·DB·watcher·SPA·websocket은 만들지 않는다.

실행 환경은 Python 3.9 이상과 선택한 timezone의 ZoneInfo 데이터가 필요하다. 시스템 timezone 데이터나 환경에 이미 설치된 `tzdata`를 사용하며 generator가 자동 설치하지 않는다. 데이터가 없으면 명확한 오류로 중단하므로 실행 환경에 timezone 데이터를 제공한다.

generator의 YAML 지원 범위는 flat scalar와 `agents`/`models`의 scalar block list(`  - Role`), 빈 목록 `[]`, null/생략이다. JSON 방식 double-quote escape와 single-quote의 `''` escape를 지원한다. colon 뒤 공백이나 hash comment와 혼동될 문자열은 따옴표로 감싼다. 중첩 구조, 값이 있는 inline 배열, anchors, tags, multiline scalar는 지원하지 않는다. 지원하지 않는 형식·중복 키·잘못된 날짜/상태/Size/MD는 Report 상대 경로와 오류를 표시하고 중단한다. 모든 파싱·렌더링이 성공하기 전에는 기존 Dashboard를 교체하지 않으며 원본 Markdown은 수정하지 않는다. 파일은 각각 임시 파일 작성 후 atomic replace한다.

Current는 오늘 업무 수·상태·Size·Estimated/Final/평균 MD·Role/Model 참여·최근 업무·주요 Decision·최근 Core 개선을 표시한다. Daily는 당일 상태·Size·MD·참여·업무·Decision, Weekly는 완료율·날짜별 MD·프로젝트·Decision·Core 개선, Monthly는 주별 업무/MD·Size별 평균 MD·프로젝트 비율·Decision/Core 횟수를 표시한다. 일별·주별 MD, 프로젝트별 MD, Estimated와 Final 차이를 함께 보여준다. Archive는 Daily 하루 하나, Weekly ISO 주 하나, Monthly 월 하나로 기간별 파일을 갱신하며 실행마다 파일을 추가하지 않는다. 과거 기간 스냅샷은 별도의 날짜로 생성할 수 있다.

## 기존 기록 이동

환경별 기존 AI Office 폴더만 대상으로 원본·대상 경로 containment를 확인한다. 대상이 있으면 덮어쓰지 않고 충돌을 보고한다. 이동 전후 파일 목록·해시·주요 파일 존재를 확인하고 프로젝트/개인 지식 폴더는 수정·이동하지 않는다. 혼합 README는 원본을 보존하고 Workspace 색인과 상위 참고자료 색인으로 분리한다. 기존 Report·Decision·INDEX의 상대 링크는 같은 내부 구조를 유지한다. 과거 metadata·Ticket을 임의로 채우지 않는다.

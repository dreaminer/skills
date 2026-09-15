# Seed의 조건부 UI 검증 수정 계획

작성: 2026-09-15. 상태: 사용자 승인 후 v1 지침 변경 적용.
기존 네 파일을 보강했고 스키마·checker·라우팅은 유지했다. MCP는 선택 도구로 명시했다.
`bun run validate`, 두 스킬의 `quick_validate.py`, `bun pm pack --dry-run`을 통과했다.
아래 검증 계획 중 실제 UI 프로젝트의 에이전트 실행 trace는 아직 수행하지 않았다.

## 목적과 추천 구조

UI를 제공하는 Seed 프로젝트에서는 사용자가 화면에서 Essential의 목적을 달성하는
검증을 추가하고, UI 없는 프로젝트에는 브라우저 의존성이나 UI 기록을 요구하지 않는다.

`seed-system`과 `seed-tdd`를 유지한다. `seed-ui-tdd`와 세 번째 완료 축은 신설하지 않는다.
`seed-system`은 제공 경계와 관찰 가능한 결과를 합의하고, `seed-tdd`는 그 경계에 맞는
실행 방법을 선택한다. v1은 기존 참조 문서 안의 짧은 브라우저 절로 시작한다.
이 계획의 상세 설명을 모두 SKILL.md의 새 의무로 복제하지 않는다.

같은 Essential 목적에서 코드 경계 AC와 화면 경계 AC를 별도로 파생한다.
한 AC 안에 두 Seam이나 두 lifecycle을 넣지 않는다. 코드 AC와 화면 AC를 항상
쌍으로 만들 필요도 없다. 각 테스트는 실제 위험을 검증할 때만 추가한다.

## 현재 구조에서 재사용할 것

- `seed-system/references/artifacts.md`: 이미 `Layer: browser`를 허용한다.
- AC별 단일 Seam, 단일 lifecycle, 해시와 `@acceptance` 연결을 유지한다.
- `Closes`: 지원하는 소비자 진입점에서 실제 연결을 통과해 Essential 결과를 관찰한다.
- 코드와 UI AC는 동일한 Essential UseCase를 `Evidence`로 참조할 수 있다.
- `seed-tdd`가 모든 AC 상태를 소유한다. `seed-realize`는 기술 선택의 실현을 소유한다.
- 기존 `seed-loop`는 남아 있는 AC를 선택하므로 브라우저 AC도 같은 경로로 실행한다.

현재 checker는 Essential Subject별 closing AC 존재를 검사한다. 서로 독립적으로 약속한
UI/API 진입점 각각의 누락, 테스트의 실제 브라우저 실행, Then의 의미적 충실성은 판별하지
않는다. 이번 제안을 적용해도 구조 검사만으로 이 사실들이 자동 증명되지는 않는다.

## 1. seed-system: UI 적용 여부와 검증 책임 설계

이미 비준된 제공 범위에서 사용자가 어느 진입점을 쓰는지 확인한다. UI 제공 여부가
미정이면 기존 대화에서 결정한다. 권한·요청 identity 같은 도메인 조건으로 UI 존재를
추론하지 않는다. 별도의 전역 `ui: true/false` 필드는 추가하지 않는다.

- 라이브러리/API/worker만 제공: 해당 공개 경계를 사용한다. UI 기록을 추가하지 않는다.
- 웹 화면 제공: 그 화면을 통해 약속한 Essential 결과를 닫는 AC를 계획한다.
- API와 화면을 독립적으로 제공: 각각의 제공 경로를 닫는 AC를 확인한다.
- 제품 내부 API: 공개 제품 API라고 간주해 별도 제공 의무를 만들지 않는다.
- 네이티브/데스크톱 UI: UI가 없는 것으로 취급하지 않는다. 적합한 실행 도구를 별도
  구현 기본안으로 정한다. v1 브라우저 예시를 네이티브 검증 증거로 사용하지 않는다.

비준 전 작업 메모에서 Essential 목적 → 약속한 진입점 → closing AC의 대응을 검토한다.
이는 새 canonical 문서나 ID 체계가 아니다. 기존 계약의 Seam과 Evidence에 근거를 남긴다.
매핑에 없는 약속이 발견되면 AC를 보완하고 기존 비준 경계를 따른다.

화면의 오류 표시, 재시도, 키보드 조작, 저장 유지 등은 관련 위험과 합의된 제품 범위에
따라 계약화한다. 모든 UI에 고정 체크리스트를 복제하거나 미합의 동작을 발명하지 않는다.
Playwright 같은 도구 선택은 Acceptance가 아니라 구현 기본안에 둔다.

UI 진입점이 Essential에서 물려받은 것이 아니라 System에서 추가로 설계한 선택이면
해당 AC는 `Basis: proposed`로 비준한다. proposed AC도 `Closes`를 가질 수 있다.
UI를 실제로 기동·제공할 런타임과 테스트 도구의 기술 선택은 기존 IP에 두어 seed-realize가
실현을 맡는다. 사용자에게 제공할 UI 동작은 AC에 두고, 같은 동작을 IP로 중복 정의하지 않는다.

### 예시: 예약 취소

아래는 구조 예시이며 특정 프로젝트의 비준된 계약이 아니다.

| AC | Seam / Layer | 검증 책임 | Closes |
|---|---|---|---|
| AC-010 | 예약 서비스 공개 연산 / integration | 권한·상태에 따른 취소 처리 | 서비스 자체가 제공 인터페이스일 때만 |
| AC-011 | 관리자의 예약 화면 / browser | 화면에서 취소하고 실제 결과를 확인 | 예약 취소 UseCase |
| AC-012 | 예약 화면 / browser | 합의된 실패 조건에서 실패를 알리고 성공으로 표시하지 않음 | 필요한 경우 |

세 AC는 같은 Essential 목적을 참조한다. 모든 도메인 예외 조합을 브라우저에서 반복하지
않는다. 화면 동작과 연결 검증에 필요한 경로를 선택한다.

## 2. seed-tdd: 브라우저 실행 지침을 조건부 적용

선택한 AC의 Layer가 browser이거나 Seam이 웹 사용자 진입점이면 브라우저 절을 적용한다.
Layer와 Seam이 맞지 않으면 기존 Risk/Layer 검토로 돌아간다. 새 실행 owner는 만들지 않는다.

아래는 기존 공통 규칙을 브라우저에 적용한 실행 예시다. v1의 짧은 절에는 실제 연결,
RED/gap 구분, 의미를 보존하는 수리만 명시하고 나머지는 기존 규칙과 도구 지침을 따른다.

기존 프로젝트 러너를 사용하며, 없으면 seed-system에서 도구를 구현 기본안으로 정한다.
스킬에 특정 프레임워크를 고정하지 않는다. LLM은 비준된 Given/When/Then에서 테스트를
작성·진단하고, 재실행 가능한 러너가 기능 통과를 판정한다. 현재 UI를 정답으로 역추론하지 않는다.

1. 제공 경로를 닫는 테스트는 실제 UI와 내부 애플리케이션 연결을 통과한다. setup용 API는
   가능하지만 검증 대상 When을 API로 대신 수행하지 않는다. 외부 경계의 double은 기존
   규칙을 따르며, 내부 API를 모두 모킹한 화면 테스트는 delivery closure 증거가 아니다.
2. 환경과 fixture가 준비된 상태에서 계약상 조작 또는 결과가 없어 실패하면 RED이다.
   브라우저 설치·서버 시작·로그인 fixture·데이터 준비 실패는 gap이다. 사라진 버튼도
   올바른 페이지와 fixture에 도달했고 계약상 필요하다는 근거가 있어야 faithful RED이다.
3. locator·대기 수리는 계약 의미를 보존할 때만 한다. assertion 삭제, skip, 성공 조건 완화,
   무조건적 baseline 갱신을 테스트 수리로 처리하지 않는다.
   실제로 실행하지 않거나 skip된 결과를 해당 AC의 GREEN으로 인정하지 않는다.
4. 처음부터 통과하면 기존 PREEXISTING_GREEN 민감도 절차를 따른다. 예컨대 임시 복사본에서
   실제 취소 연결을 끊었을 때 해당 결과 assertion이 실패하는지 확인한다.

프로젝트의 기존 전체 테스트 명령이 코드와 브라우저 suite를 함께 실행하도록 구성한다.
개별 실행 명령과 결과는 기존 Notes에 남긴다. 단일 Test command와 Test directory를
유지하며, 필요하면 두 suite를 포함하는 공통 디렉터리와 실행 wrapper를 사용한다.
trace·스크린샷·실행 보고서는 프로젝트의 기존 테스트 산출물로 두고 Notes에서 연결한다.
독립적인 Seed 증거 스키마는 만들지 않는다.

## 3. Essential 목적을 가진 UI 검토

결정적인 브라우저 assertion과 LLM의 사용성 판단을 구분한다. 해당 흐름이 GREEN이 된 후
목표·역할·시작 조건을 가지고 화면을 탐색하는 검토를 사용자가 선택해 요청할 수 있다.
구현자의 클릭 경로나 설명에 의존하지 않는 새 에이전트 컨텍스트 또는 사용자가 수행한다.
seed-loop는 이 검토를 자동 선택하지 않는다. 매 AC마다 새 에이전트를 강제하지 않으며,
v1에서는 별도 스킬이나 완료 축으로 만들지 않는다. 발견 내용은 대화 턴을 참조하거나
자유 형식 작업 메모로 남기며 새 canonical 파일·상태를 만들지 않는다.

검토자는 목적 달성 과정에서 막힌 동선, 발견하기 어려운 조작, 오해하게 만드는 결과 표시를
찾고 재현 단계·화면·관련 AC를 남긴다. 결과의 처리 책임은 다음과 같다.

- 기존 계약 위반: seed-tdd에서 놓친 조건을 검증하는 테스트로 먼저 실패를 재현하고 구현 수정.
- 계약에 빠진 System 동작: seed-system으로 돌려 합의 후 테스트화.
- 새로운 Essential 목적: seed-body로 반환.
- 미적 선호나 증거가 약한 사용성 추정: 제안으로 보고하며 자동으로 계약에 승격하지 않음.

LLM 검토 점수는 AC의 GREEN을 대신하지 않는다. 사람의 실제 사용성 검증을 완료했다고
주장하지 않는다. 알려진 계약 위반은 해결한 뒤 완료를 보고한다. 선택적 검토를 생략했다면
탐색적 사용성 검토까지 수행했다고 보고하지 않는다.

시각적 회귀·접근성 검사 체계의 신규 추가는 v1 수정 범위에서 제외한다. 이미 프로젝트가
약속한 접근성·화면 요구가 있다면 기존 계약으로서 계속 검증한다.

## 4. 수정할 파일과 순서

| 순서 | 파일 | 변경 |
|---|---|---|
| 1 | seed-system/DESIGN.md | 조건부 UI 적용, 단일 Seam/AC 유지, checker 한계와 재검토 조건 |
| 2 | seed-system/SKILL.md | 기존 Delivery closure 검토에 합의된 제공 경로별 AC와 non-UI 예시를 간결하게 추가 |
| 3 | seed-system/references/artifacts.md | 기존 Closes 설명에 별도 화면 AC의 예시와 browser Layer의 의미 보강 |
| 4 | seed-tdd/references/test-quality.md | 짧은 Browser closers 절: 실제 연결, RED/gap, 기대 결과를 보존하는 수리 |

checker의 파서·해시 알고리즘, seed-loop 라우팅, seed-realize 소유권, plugin manifest는
v1에서 변경하지 않는다. seed-tdd는 이미 test-quality.md를 읽으므로 새 로딩 절차도 필요 없다.
기존 테스트로 이미 보장되는 다중 closer와 해시 동작을 중복 테스트하지 않는다.
실제 회귀가 기존 모델의 표현 한계를 드러내면 별도 변경으로 다룬다.
현재 작업 트리에 있는 Essential consistency 관련 세 파일 수정은 보존한다.

## 5. 구현 후 검증 계획

기계적 회귀와 에이전트 실행 검증을 구분한다.

| 사례 | 검증할 결과 |
|---|---|
| UI 없는 기존 fixture | 기존 완료 판정과 해시 유지, UI 자료·도구 불필요 |
| 코드 AC GREEN + 별도 browser AC gap | 기존 completion checker가 미완료 거부 |
| browser AC의 Then 또는 Seam 변경 | 해당 AC의 이전 마커 무효화 |
| 코드·browser suite 병행 | 전체 명령이 어느 한쪽 실패도 성공으로 숨기지 않음 |
| 실제 UI fixture에서 이벤트 연결 끊기 | 결과 assertion 실패 후 복구하면 통과 |
| 브라우저·서버 준비 실패 | 기능 RED가 아닌 gap으로 분류 |
| locator 수리 유혹 / skip 유혹 | 기대 결과를 보존하고 결함을 GREEN으로 바꾸지 않음 |
| API와 UI를 각각 약속했으나 UI AC 누락 | seed-system 대화 검토에서 누락을 발견하는지 확인 |
| UI 없는 범위에서 사용자 역할 언급 | 역할만 보고 UI를 발명하지 않음 |

앞의 구조·해시 사례는 기존 회귀 범위를 확인하고, 빠진 실제 실패 사례만 회귀로 추가한다.
뒤의 판단·대화 사례는 실행 trace를 검토한다.
문서에 문장이 존재하는지만 검사하는 테스트로 행동 검증을 대체하지 않는다.
패키지 검증은 기존 `bun run validate`와 `bun pm pack --dry-run`을 사용한다.
브라우저 행동 증거는 작은 별도 웹 샘플에서 남기고 모든 스킬 설치에 브라우저를 요구하지 않는다.

## 6. 이행과 되돌리기

기존 non-UI 프로젝트는 이행 작업이 없다. 기존 UI 프로젝트는 현재 AC를 자동 변환하거나
비준 없이 UI 의무를 삽입하지 않는다. 기존 계약이 UI를 약속했는지 확인하고, 누락된 화면
AC를 기존 seed-system 절차에서 확정한 뒤 그 AC만 gap부터 진행한다.

기존 AC를 변경하지 않았다면 해시를 다시 만들지 않는다. 같은 AC의 Seam을 바꾸었다면
기존 해시 규칙대로 재검증한다. 새 스킬·스키마가 없으므로 지침 변경은 독립적으로 되돌릴 수
있지만, 이미 비준된 프로젝트의 UI 계약은 지침 rollback을 이유로 삭제하거나 완료에서 제외하지 않는다.

## 7. 후속 확장이 필요한 조건

실제 실행 trace에서 Stage B가 약속한 UI/API 제공 경로의 closer 없이 비준되는 사례가
한 번 확인되면 그 실패를 근거로 per-entry coverage 모델의 필요성을 재검토한다.
사람이 확인한 제공 경로 목록의 기계적 누락 검사가 명시적 요구가 된 경우도 별도 설계한다.
그때는 약속한 진입점 집합, AC와의 관계, 변경 무효화, 구 프로젝트 이행까지 함께 다룬다.
단순히 `UI: yes`나 `Layer: browser` 하나를 추가해 의미 검증이 해결됐다고 주장하지 않는다.

UI 탐색 검토가 반복적으로 독립된 입력·산출물·재개 절차를 요구할 때 별도 review 스킬을
검토한다. 기존 TDD와 같은 AC lifecycle을 동시에 소유하는 두 번째 TDD 스킬은 피한다.

브라우저 절이 커져 다른 경계의 작업에 부담이 되면 그때 별도 reference로 추출한다.
v1에서는 신규 reference 두 개와 매번 자동 실행하는 UI 평가자를 추가하지 않는다.

승인된 시각 기준이나 구체적인 접근성 검증 요구가 생기면 해당 도구를 추가한다.
처음 생성한 스크린샷이나 baseline 부재 오류를 제품 동작의 RED로 취급하지 않고,
자동 접근성 검사로 실제 사용성 전체가 입증됐다고 주장하지 않는다.

## Advisor와의 합의 및 판단 차이

사용자가 지정한 Paseo `ClaudeFable5.1` 프로필로 저장소와 공식 자료를 독립 검토했다.
별도 AC, 단일 lifecycle, 기존 두 완료 축 유지, per-entry registry 보류에 의견이 일치했다.
Advisor의 변경 최소화 권고를 받아 초안의 신규 reference 두 개를 빼고 네 파일 보강으로 좁혔다.
후속 검토에서도 축소된 계획에 동의했으며, proposed UI AC의 Basis, opt-in 검토의 주체,
프레임워크 중립성과 실제 실패 trace에 따른 재검토 조건을 명확히 하자는 의견을 반영했다.

UI 제공 여부는 Essential에 특정 단어가 있는지만으로 결정하지 않는다. Essential과 비준된
System 제공 선택, 사용자가 이미 합의한 범위를 함께 확인한다. 그 범위가 불분명하면
UI를 발명하거나 제외하지 않고 기존 설계 대화에서 해결한다.

선택적 UI 검토는 별도 lifecycle을 소유하지 않는다. 독립 검토자가 발견한 관찰 사실은
working evidence이고, 새로운 제품 요구는 기존 사람 비준을 통과해야 한다.

## 2026년 9월 기준 참고 근거

- [Playwright Test Agents](https://playwright.dev/docs/test-agents): planner/generator/healer를
  제공한다. 현재 앱 탐색 기반 계획은 Seed의 비준된 계약을 대체하지 않으며, healer의 skip
  결과를 Acceptance 완료로 가져오지 않는 적용 방식을 택한다.
- [Playwright Best Practices](https://playwright.dev/docs/best-practices): 사용자에게 보이는
  동작, 견고한 locator, 격리된 테스트와 재시도 가능한 assertion을 브라우저 실행 기본으로 삼는다.
- [Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots): baseline과 렌더링
  환경을 관리하는 시각적 회귀는 기능 assertion을 보완한다.
- [Playwright Accessibility Testing](https://playwright.dev/docs/accessibility-testing): 자동
  접근성 검사와 수동 검토를 구분한다.
- [Anthropic Harness Design, 2026-03-24](https://www.anthropic.com/engineering/harness-design-long-running-apps):
  구현과 별도의 브라우저 평가가 연결 누락을 찾는 사례를 제공한다. 평가자 편향·비용·한계도
  보고하므로 항상 다중 에이전트를 실행하거나 점수를 제품 정답으로 취급하지 않는다.

위 선택은 해당 공식 자료와 현재 저장소 구조를 종합한 설계 판단이며, 업계 전체에서
단일 최선으로 입증된 방법이라는 주장은 아니다.

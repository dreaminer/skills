# Seed System — Acceptance 중심 개편 설계

## 결정

`seed-system`의 캐노니컬 System layer(`SYSTEM_DOMAIN.md`, `SYSTEM_USECASE.md`)를 제거하고,
greenfield 구현을 위한 독립적인 Acceptance 몸체를 만든다.

최종 행동 계약은 두 표현으로 존재한다.

1. `ACCEPTANCE.md` — 사람이 도메인 흐름과 기대 결과를 빠르게 이해하고 비준하는 문서.
2. 실행 가능한 Acceptance tests — 구현물이 비준된 계약을 만족하는지 기계적으로 판정하는 코드.

두 표현은 안정적인 Acceptance ID와 계약 해시로 연결한다. 자연어 문서는 의도의 진실원천이고,
테스트는 구현을 구속하는 실행 제약이다. GREEN 자체가 사용자 의도를 만들거나 변경하지 않는다.

## 문제

기존 System layer는 두 책임을 한 자연어 산출물에 섞는다.

- 구현 전에 상태·접점·동기화·명령 규칙을 안내한다.
- 구현 후에 결과가 완성됐는지 판정한다.

그러나 `SYSTEM_USECASE.md`는 Essential 흐름과 유사한 Given/When/Then을 반복하면서도 실행할 수
없다. 구현 가이드로는 구체성이 일정하지 않고, 완료 판정 기준으로는 pass/fail 경계가 없다.
`SYSTEM_DOMAIN.md`도 Essential Domain과 자주 겹쳐 사용자가 같은 행동과 언어를 두 층에서 다시
비준하게 만든다.

하나의 System 캐노니컬이 안내와 판정을 모두 맡는 대신 책임을 분리한다.

```text
동결된 Essential + 파킹된 실행 수단 발화
  -> raw 도메인 흐름과 설계 제약
  -> 사람이 비준하는 Acceptance 계약
  -> 구현 기본안 비준
  -> TDD가 실행 테스트 작성 및 RED 확인
  -> 구현
  -> GREEN으로 완료 판정
```

## 목표 산출물

### 캐노니컬

- `ESSENTIAL_DOMAIN.md` — `seed-body`에서 받은 기술 독립적인 공용 언어. 읽기 전용으로 상속한다.
- `ACCEPTANCE.md` — v1의 비준된 도메인 흐름과 관측 가능한 결과.

`SYSTEM_DOMAIN.md`, `SYSTEM_USECASE.md`, `ESSENTIAL_USECASE.md`를 별도 캐노니컬로 유지하지 않는다.
같은 행동을 설명하는 복수 문서를 두지 않는다.

### 실행 제약

- 프로젝트의 Acceptance test 코드.
- `SEED_SYSTEM_TESTS.md` — 테스트 명령, 테스트 디렉터리, Acceptance ID별 경로와 상태.

테스트 파일은 다음 마커로 자연어 계약과 연결한다.

```text
@acceptance: AC-001 sha256:<canonical-contract-hash>
```

### 구현 안내와 작업 근거

- `SEED_SYSTEM_IMPL_PROPOSAL.md` — 스택, 저장, 접점, 동기화, 배포의 비준된 기본안.
- raw 흐름, 상태전이, 접점 계약, 실패 처리, 멱등성 및 충돌 규칙 — Acceptance와 구현 기본안을
  도출하는 비캐노니컬 작업 근거.
- `LATER`, `QUESTIONS`, `CRITERIA`, `REJECTED` — 현재의 경계·유보·게이트 기록.

작업 근거는 구현 가이드에 필요한 정보를 보존하지만 독립적인 사용자 계약이 되지 않는다.

## Acceptance 계약

각 시나리오는 하나의 판정 가능한 도메인 흐름만 담는다.

```md
## [중복 없이 발주확인 반영]

ID:
AC-001

Basis:
proposed

Seam:
- 발주확인 채널 접점

Given:
- 반영되지 않은 [발주확인]이 있다.

When:
- 전송 도중 연결이 끊겨 같은 요청이 다시 전달된다.

Then:
- [발주확인]은 한 번만 반영된다.

Evidence:
- T12 (비준) "다시 보내도 두 번 잡히면 안 돼"
```

요구 사항:

- 안정적이고 유일한 `AC-{nnn}` ID.
- 모든 절이 비준된 Essential 내용으로 소급되면 `Basis: inherited`, 한 절이라도 새로 설계한
  System 행동을 추가하면 `Basis: proposed`. 애매하면 `proposed`.
- 내부 호출 순서가 아니라 결과를 관측할 수 있는 가장 낮고 안정적인 `Seam`.
- Essential 언어로 쓴 구체적인 Given/When/Then.
- 사용자 발화와 비준 턴을 가리키는 Evidence.
- 성공뿐 아니라 v1에 필요한 실패, 역방향, 재시도, 충돌 흐름.

계약 해시는 ID, Subject, Seam, Given, When, Then을 포함하고 Basis와 Evidence는 제외한다.
provenance 수정은 테스트를 stale하게 만들지 않는다. 문구가
실질적으로 바뀌면 연결된 `red`/`green` 기록을 즉시
`gap — contract changed; test relink required`로 내린다. 이전 테스트 경로와 마커는 Notes에
감사 기록으로 남기되 stale 마커를 활성 Marker로 유지하지 않는다. 현재 해시로 테스트를
수정·연결하고 실행한 뒤에만 `red` 또는 `green`으로 복구한다.

## 테스트 생명주기

`seed-system`은 Acceptance 계약과 테스트 연결 생명주기를 소유한다. 테스트 작성 기술 자체는
`$tdd`에 위임한다. 즉, 이 스킬을 수정하거나 이후 프로젝트 테스트를 작성할 때 `$tdd`를 작업
방식으로 사용할 수 있지만, `seed-system`의 구동이 `$tdd`에 런타임 의존한다는 뜻은 아니다.

Acceptance별 상태:

- `red` — 실행 가능한 테스트가 있고, 아직 구현되지 않은 행동 때문에 기대대로 실패함.
- `green` — 연결된 테스트가 통과함.
- `gap — <구체 이유>` — 충실한 실행 테스트를 만들 수 없는 장애가 명시됨.

정상적인 구현 핸드오프에는 `red`가 필요하다. 테스트 기반이 아직 없으면 `planned` 같은 별도
프로토콜을 만들지 않고 `gap — test harness not created yet`처럼 구체 사유를 기록한다. gap은
정직한 중간 상태지만 구현 완료를 주장할 수 없다. 완료 게이트는 모든 v1 Acceptance가 `green`
이어야 한다.

테스트 프레임워크가 아직 없는 코드 없는 출발점에서는 다음 순서를 따른다.

1. Acceptance와 seam을 먼저 비준한다.
2. `IMPL_PROPOSAL`에서 스택과 테스트 기반을 비준한다.
3. `$tdd`가 최소 테스트 하네스와 Acceptance tests를 작성한다.
4. 구현 전 RED를 확인한다.
5. 구현 후 GREEN과 전체 테스트 suite를 확인한다.

`seed-system` 자체에 두 번째 TDD 엔진을 만들지 않는다.

## 새 워크플로

### 1. 입력과 발산

`seed-body`의 Essential 언어와 파킹된 실행 수단 발화를 읽는다. 사용자와의 breadth-first 문답으로
상태전이, 접점, 동기화, 명령, 실패, 재시도 및 충돌 흐름을 raw 코퍼스에 모은다. 이 정보는
System 캐노니컬 후보가 아니라 Acceptance 사례와 구현 제약의 재료다.

### 2. Acceptance 수렴

raw 흐름을 사용자 관점의 관측 가능한 사례로 재기술한다. 내부 컴포넌트나 기술 선택을 Given/
When/Then에 넣지 않는다. 각 사례가 상속된 Essential Domain 언어만 사용하는지, 한 seam에서 모든
Then을 판정할 수 있는지 점검한다.

### 3. 배치 비준

사용자에게 전체 `ACCEPTANCE.md`를 한 번에 제시한다. 부분 수정과 부분 기각을 반영한 뒤 최종
비준한다. 비준 전 후보는 캐노니컬이나 테스트 요구사항이 아니다.

### 4. 구현 기본안 비준

비준된 Acceptance와 raw 설계 제약에서 구현 분야를 도출한다. 분야별 기본안을 하나씩 제안하고
사용자가 바꿀 것만 수정하도록 한다. 기술 선택이 Acceptance를 바꾸지 못하며 충돌하면 Acceptance가
우선한다.

### 5. 실행 테스트 핸드오프

각 AC ID, 계약 해시, seam, 테스트 명령 후보를 `$tdd`에 넘긴다. `$tdd`가 모든 Then에 대응하는
assertion을 작성하고 RED를 확인한다. 마커나 RED exit code만으로 테스트 충실도를 추론하지 않는다.

### 6. 구현 및 완료 게이트

RED 테스트와 `IMPL_PROPOSAL`을 구현 단계에 넘긴다. 구현 후 연결 테스트와 전체 suite를 실행한다.
모든 v1 Acceptance가 유효한 해시로 연결되어 GREEN일 때만 완료를 선언한다.

## 종료 게이트

기존의 Implementation-derivability 질문을 Acceptance-testability 기준으로 바꾼다.

각 v1 흐름에 대해 다음을 확인한다.

- 사용자에게 중요한 결과가 Given/When/Then으로 비준됐는가?
- 성공·실패·역방향·재시도·충돌 중 필요한 사례가 포함됐는가?
- 각 Then을 관측할 안정적인 seam이 있는가?
- 각 Then에 대응하는 assertion을 작성할 수 있는가?
- 구현 기본안이 모든 Acceptance를 실현할 수 있는가?
- 연결된 테스트가 RED를 거쳐 GREEN이 됐는가?

메타 비준은 “완성도를 판정하기 위한 Acceptance 집합이 충분한가?”를 묻고, 내용 비준은 전체
Acceptance 전문을 대상으로 한다. 구현 완료 비준을 자연어 검토로 대체하지 않는다.

## `make-body`와의 분리

두 스킬은 출발점과 소유 산출물이 다르다. `seed-system`은 greenfield 구현 전에 사람이 비준할
Acceptance 계약과 테스트 연결 생명주기를 소유한다. `make-body`는 기존 코드베이스의 qualified
flow tests를 입력으로 Essential 의미만 복원하며 Acceptance 계약이나 테스트 연결을 만들거나
관리하지 않는다.

| 항목 | `seed-system` | `make-body` |
|---|---|---|
| 출발점 | 사용자 의도와 코드 없는 Essential | 기존 코드와 qualified flow evidence |
| 사람용 캐노니컬 | `ESSENTIAL_DOMAIN.md` + `ACCEPTANCE.md` | `ESSENTIAL_DOMAIN.md` + `ESSENTIAL_USECASE.md` |
| 테스트 관계 | `$tdd`에 RED/GREEN 작성·연결을 인계 | 이미 qualified된 테스트를 읽기 전용 입력으로 소비 |
| Acceptance 소유 | 생성·비준·해시·연결 상태 관리 | 생성·변환·관리하지 않음 |
| 완료 판정 | 모든 v1 Acceptance 테스트 GREEN | Essential 의미의 사람 비준과 구조 검증 |

동일 프로젝트에 두 스킬의 산출물이 함께 있더라도 자동 변환하거나 하나의 ID 체계로 합치지 않는다.
각 스킬은 자기 truth-maker와 파일 경계를 독립적으로 유지한다.

## 마이그레이션 영향

이 개편은 `seed-system`만의 문구 변경으로 끝나지 않는다.

1. `seed-body`의 `ESSENTIAL_USECASE.md`를 `ACCEPTANCE.md`로 곧바로 승급하지 않는다. Essential
   유스케이스는 Acceptance 후보의 입력으로 취급하고, `seed-system`에서 seam과 사례를 비준한다.
2. 기존 `SYSTEM_DOMAIN.md`와 `SYSTEM_USECASE.md`는 자동 변환하지 않는다. 사용자 검토를 거쳐
   Acceptance 후보와 작업 근거로 분류한다.
3. `seed-system`의 artifacts, conversation loop, closing gate, description을 새 계약에 맞춘다.
4. Acceptance ID, 계약 해시, 테스트 레코드는 `seed-system`이 소유한다. 이후 `make-body`가 실행되면
   기존 Acceptance 파일은 navigation용 legacy 입력일 뿐 자동 변환 대상이 아니다.
5. 혼합된 구·신 캐노니컬이 동시에 존재하면 완료 검사를 실패시킨다.

## 비목표

- Acceptance tests를 UI/E2E 테스트로만 제한하지 않는다.
- 자연어 계약에서 특정 프레임워크나 라이브러리를 고정하지 않는다.
- GREEN을 사용자 비준이나 제품 의도의 증거로 취급하지 않는다.
- raw System 흐름을 독립적인 캐노니컬 도메인 모델로 승급하지 않는다.
- `seed-system` 안에 테스트 작성·구현 엔진을 중복 구현하지 않는다.

## 검증 계획

동일한 greenfield 예제를 기존 방식과 개편 방식으로 각각 dry run한다.

검증 항목:

- Essential과 System 사이의 중복 비준이 제거되는가?
- 사용자가 `ACCEPTANCE.md`만 읽고 v1 도메인 흐름을 빠르게 이해할 수 있는가?
- 각 Then이 구체적인 assertion과 연결되는가?
- 상태·접점·동기화·실패 제약이 작업 근거와 `IMPL_PROPOSAL`에 보존되는가?
- 구현 전 RED와 구현 후 GREEN이 재현되는가?
- 계약 변경 시 해시 불일치가 stale 테스트를 탐지하는가?
- 이후 다른 스킬이 실행돼도 Acceptance 계약과 테스트 연결의 소유권이 흐려지지 않는가?

개편은 이 dry run이 기존 System 문서보다 더 명확한 구현 핸드오프와 기계적인 완료 판정을
제공하면서, 필요한 구현 제약을 유실하지 않을 때 채택한다.

# Seed System — 설계 결정

운영 절차는 여기 없다. `SKILL.md`나 `references/artifacts.md`를 바꾸기 전에 이 문서의
소유 지도와 편집 게이트를 먼저 적용한다.

## 결정

`seed-system`의 캐노니컬 System layer(`SYSTEM_DOMAIN.md`, `SYSTEM_USECASE.md`)를 제거하고,
greenfield 구현을 위한 독립적인 Acceptance 몸체를 만든다.

최종 행동 계약은 두 표현으로 존재한다.

1. `ACCEPTANCE.md` — 사람이 도메인 흐름과 기대 결과를 빠르게 이해하고 비준하는 문서.
2. 실행 가능한 Acceptance tests — 구현물이 비준된 계약을 만족하는지 기계적으로 판정하는 코드.

두 표현은 안정적인 Acceptance ID와 계약 해시로 연결한다. 자연어 문서는 의도의 진실원천이고,
테스트는 구현을 구속하는 실행 제약이다. GREEN 자체가 사용자 의도를 만들거나 변경하지 않는다.

근거: 구 System layer는 구현 전 안내와 구현 후 판정을 한 자연어 산출물에 섞었다.
`SYSTEM_USECASE.md`는 Essential과 유사한 Given/When/Then을 반복하면서 실행할 수 없었고,
사용자가 같은 행동을 두 층에서 다시 비준하게 만들었다. 안내는 `SEED_SYSTEM_IMPL_PROPOSAL.md`로,
판정은 Acceptance 계약+테스트로 분리한다.

## 소유 지도

한 사실은 한 곳만 산다. 중복이 발견되면 동기화하지 않고 소유자 아닌 쪽을 삭제한다.

| 사실 | 소유자 |
|---|---|
| 계약 해시 계산, 구조 게이트, 캐노니컬 거절 라벨 목록 | `scripts/check-acceptance.py` |
| 입력 계약, 계약 파일 스키마, 생명주기 어휘(`PREEXISTING_GREEN` 포함) | `references/artifacts.md` |
| 정체성 목록과 대화 지침 | `SKILL.md` |
| 설계 결정, 근거, 편집 게이트 | `DESIGN.md` |

## 편집 게이트 (2026-08-15)

이 스킬은 미검증 규범이 검증 속도를 앞질러 무한 수정에 빠졌었다(감량 전 산문 ~1,140줄,
실행 증거는 트레이스 1회 + 해시 회귀 1개). 규범 텍스트는 다음 게이트를 통과해야 한다.

1. **한 사실 한 소유자.** 소유 지도 밖의 재기술은 삭제 대상이다.
2. **방어적 must는 실행된 실패가 있을 때만 승격한다.** 트레이스나 회귀가 보여준 실패 1건이
   must 1개를 승격한다. `SKILL.md`의 정체성 목록이 이 게이트의 유일한 면제다 — 목록은 닫혀
   있고, 추가(의미상 의무를 늘리는 재표현 포함)는 사용자 비준을 요구한다.
3. **must는 스크립트가 실패시키는 것만이다.** 정체성 목록도 예외가 아니며, 그래서 지침으로 쓴다.

증거 등급: 셀프플레이 산출물은 기계적 모순 스크리닝이지 대화 규칙의 증거가 아니다. 실전 문답
트레이스만 방어적 must의 승격 근거다. 잘 끝난 세션은 must를 추가하지 않는다.

## Acceptance 계약 결정

- 계약 해시는 행동 필드(ID·Subject·Seam·Given/When/Then)만 덮는다. Basis와 Evidence는
  provenance라 해시 밖이다 — provenance 수정이 테스트를 무효화하면 안 된다.
- 계약의 의미 변경은 연결 테스트의 relink를 강제한다. 기계 검증은 스크립트가, 의미 판단은
  사람과 에이전트가 맡는다.
- Basis 이원화(`inherited`/`proposed`, 애매하면 `proposed`)와 재기술 AC 금지 가드(정체성 목록
  9번)는 2026-08-07 사용자 비준 결정이다 — "ACCEPTANCE가 EUC의 GWT 재포맷"이 되는 실패를 막되,
  EUC를 캐노니컬로 되살리는 처방은 거부했다.

## 테스트 생명주기 위임

`seed-system`은 계약과 생명주기의 스키마를 소유하고, 실행 테스트 작성·상태 갱신·최소 구현은
`$seed-tdd`에 위임한다(런타임 의존 아님). RED의 정의 — 관측된 working-tree RED 또는 격리
감수성 RED — 는 seed-tdd의 `GREENFIELD_TRACE`(2026-08-14)로 검증된 결정이다. `seed-system` 안에
제2 TDD 엔진을 만들지 않는다.

## `make-body`와의 분리

두 스킬은 출발점과 소유 산출물이 다르다. `seed-system`은 greenfield 구현 전에 사람이 비준할
Acceptance 계약과 테스트 연결 생명주기를 소유한다. `make-body`는 기존 코드베이스의 qualified
flow tests를 입력으로 Essential 의미만 복원하며 Acceptance 계약이나 테스트 연결을 만들거나
관리하지 않는다.

| 항목 | `seed-system` | `make-body` |
|---|---|---|
| 출발점 | 사용자 의도와 코드 없는 Essential | 기존 코드와 qualified flow evidence |
| 사람용 캐노니컬 | `ESSENTIAL_DOMAIN.md` + `ACCEPTANCE.md` | `ESSENTIAL_DOMAIN.md` + `ESSENTIAL_USECASE.md` |
| 테스트 관계 | `$seed-tdd`에 RED/GREEN 작성·연결을 인계 | 이미 qualified된 테스트를 읽기 전용 입력으로 소비 |
| Acceptance 소유 | 생성·비준·해시·연결 상태 관리 | 생성·변환·관리하지 않음 |
| 완료 판정 | 모든 v1 Acceptance 테스트 GREEN | Essential 의미의 사람 비준과 구조 검증 |

동일 프로젝트에 두 스킬의 산출물이 함께 있더라도 자동 변환하거나 하나의 ID 체계로 합치지 않는다.

## 레거시 결정

- `ESSENTIAL_USECASE.md`를 `ACCEPTANCE.md`로 승급하지 않는다. 입력 커버리지 자료다.
- 기존 `SYSTEM_DOMAIN.md`/`SYSTEM_USECASE.md`는 자동 변환하지 않고 사람 검토로 분류한다.
- 구·신 캐노니컬 혼재는 완료 검사를 실패시킨다(mixed-mode, 스크립트 강제).

## 비목표

- Acceptance tests를 UI/E2E 테스트로만 제한하지 않는다.
- 자연어 계약에서 특정 프레임워크나 라이브러리를 고정하지 않는다.
- GREEN을 사용자 비준이나 제품 의도의 증거로 취급하지 않는다.
- raw System 흐름을 독립적인 캐노니컬 도메인 모델로 승급하지 않는다.
- `seed-system` 안에 테스트 작성·구현 엔진을 중복 구현하지 않는다.

## 검증 상태

- 해시·마커 연결: `seed-tdd/tests/run.sh` 회귀가 지킨다.
- 구현 경로: seed-tdd `GREENFIELD_TRACE` 1회(2026-08-14).
- 대화 경로: 미검증. 2026-08-15 감량 후 셀프플레이 모순 스크리닝
  (`docs/CONTRADICTION_SCREENING.md`, 비패키징)만 거쳤다. 남은 완료 조건은 실전 문답 트레이스
  1회이며, 그 전까지 새 must를 추가하지 않는다.
- 다음 트레이스에서 관찰할 것(규칙 아님, 2026-08-16): Stage A에서 사용자에게 실제로 제시한
  "목록"이 무엇이었고(고정 closing check 6축 / 프로젝트별 완료 기준 / 즉석 합성), 사용자가 그
  질문에 답할 수 있었는가. 기존 항목에 답만 생겼을 때와 기준이 추가·삭제됐을 때 Stage A를
  반복했는지도 함께 본다. 배경: ff8164a가 `SEED_SYSTEM_CRITERIA.md` 생성 절차와 재비준 트리거
  문장을 지우면서 그것을 가리키던 Stage A 프롬프트만 남겼다. 트리거 한 문장만 되살리는 수정은
  이 관찰 전에는 하지 않는다.

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

## 결정 (2026-08-29)

**materialized seed 문서의 정의 포인터를 탐색 가능한 링크로 표현한다 (사용자 비준).**
seed-system 출력에서는 `ACCEPTANCE.md`의 `Evidence:`와 `SEED_SYSTEM_IMPL_PROPOSAL.md`의
`Why:`만 정의 링크를 작성한다. upstream의 CRITERIA 답 포인터와 parking `Trace:`까지
포함한 네 source의 표기 스키마는 각 산출물 `references/artifacts.md`가, target 파일 탐색과
GFM heading anchor 해결은 `scripts/check-acceptance.py`가 소유한다. 별도 `seed-common` 설치 단위는
두지 않는다.

절 재배치는 내용 기반 anchor를 바꾸지 않지만 rename은 링크가 자동으로 따라가지 않는다.
체커는 이를 stale fragment로 탐지하며, 이미 작성된 로컬 링크의 파일이나 정의 절이 없으면
기본 실행과 `--complete` 모두 구조 실패다. 링크 없는 기존 포인터는 호환성을 위해 경고로
남겨, 새 산출물의 작성 지침과 기계적 타겟 무결성을 분리한다.

## 소유 지도

한 사실은 한 곳만 산다. 중복이 발견되면 동기화하지 않고 소유자 아닌 쪽을 삭제한다.

| 사실 | 소유자 |
|---|---|
| 계약 해시 계산, 구조 게이트, 정의 링크 target·GFM anchor 해결, 캐노니컬 거절 라벨 목록 | `scripts/check-acceptance.py` |
| 입력 계약, 계약 파일 스키마, 정의 링크 source·표기, 생명주기 어휘(`PREEXISTING_GREEN` 포함) | `references/artifacts.md` |
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

- 계약 해시는 테스트 의무(ID·Subject·Seam·Given/When/Then과, 있을 때 `Closes`가 지목한
  Essential Subject 집합)만 덮는다. Basis와 Evidence는 provenance라 해시 밖이다 —
  provenance나 동일 Subject를 가리키는 링크 표기 수정이 테스트를 무효화하면 안 된다.
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

## IP realization lifecycle (2026-08-30)

`SEED_SYSTEM_IMPL_PROPOSAL.md` remains the immutable, human-ratified choice source. Mutable state for
each non-deferred `IP-nnn` lives in `SEED_SYSTEM_TESTS.md`; no new canonical document or ID family is
introduced. A missing record is implicit pending, and `$seed-realize` writes one only when evidence
exists.

The realization hash covers `IP-nnn + Default`. A changed choice is normalized into `Default`, so
the old marker becomes stale. Proposal enumeration, hash, link, and completion mechanics belong to
the checker. Acceptance and realization are independent completion axes; plain `--complete` is the
strict aggregate for compatibility.

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

## Essential delivery closure (2026-09-03)

`Evidence` coverage and current-hash GREEN at each declared Seam do not imply that an inherited
Essential use case is reachable through a supported consumer entry. Record that independent
proof obligation on selected Acceptance scenarios with optional `Closes` definition links.

`Closes` belongs to `ACCEPTANCE.md`: it says which Essential use case the scenario discharges,
not where the scenario came from. It is therefore a test obligation rather than provenance. The
normalized Essential Subject set participates in the Acceptance hash when present. Adding,
removing, or changing a Subject forces `$seed-tdd` replay; renumbering or re-encoding a link to the
same Subject does not. ACs without `Closes` retain their prior hashes.

`--complete acceptance` requires a non-empty Essential use-case inventory and at least one
current-hash GREEN closing AC per inherited use case. The checker validates only inventory,
links, coverage, lifecycle, and hash currency. Whether a closing test enters through a supported
consumer entry, traverses the maintained composition, and observes a supported output remains
`seed-system`/`seed-tdd` semantic judgment.

This adds no document, ID family, completion axis, framework rule, browser requirement, or Layer
restriction. A component API qualifies when it is itself the Seed target's delivered consumer
interface. Separately, use lifecycle `Risk` to challenge Seam/Layer test planning rather than
merely restating the AC Subject or `Then`.

## Conditional UI closure (2026-09-15)

The user approved optional UI coverage within the existing Seed structure. Keep one Seam and one
lifecycle per AC; separate delivery-entry ACs may share an Essential use case. This reuses the
existing many-to-many `Closes` relation rather than adding a UI skill, a toggle, a schema migration,
or a third completion axis. UI obligations follow ratified delivery scope, including System choices;
roles alone do not imply screens. Non-UI projects retain their existing test boundaries.

`seed-system` owns entry coverage judgment and artifact examples; `seed-tdd` owns browser test
fidelity and RED/GREEN. Runtime and runner choices remain IPs realized by `seed-realize`. Tests run
through the project's runner; MCP is optional exploration support. An opt-in goal walkthrough is
feedback for those owners, not a new owner or completion signal. No framework is fixed by the skill.

These are applications of existing closure and test-quality guidance, not new mechanical gates.
The checker groups closure by Essential subject, so it cannot detect a missing promised UI entry
when another entry closes that subject. It validates Layer labels and marker presence, not actual
browser traversal, internal wiring, runner execution, or the truth of a recorded GREEN. Human/agent
review still carries those judgments; a walkthrough score does not prove usability or replace tests.

Existing closure and hash regressions cover the structural model. No live UI skill-execution trace
is claimed by this change. Revisit per-entry coverage if an actual trace shows Stage B ratifying
without a promised closer; use that failure to justify the narrowest correction. Reverting this
guidance never removes already-ratified UI obligations from a project's completion requirements.

## Essential obligation preservation (2026-09-18)

The user reported a message-project failure: Essential restricted master capabilities to Master
Clients, while Acceptance covered actor authority at the server seam and target filtering only
at the CMS seam. Those contracts could all pass while a direct grant violated the Domain rule.
This is one user-reported failure, not an independently reproduced execution trace.

The agreed correction changes the existing Coverage judgment's unit from use-case outcomes to
Essential v1 behavioral obligations, and its direction from finding related ACs to looking for
an implementation or in-scope path that satisfies them all while violating an obligation.
`SKILL.md` owns that procedure and its example. This rewrites closing-check judgment guidance;
it adds no script-enforced must or identity principle.

Existing-contract review already applies the closing check, and seed-loop already routes
start/resume through that review before completion. No new routing, canonical document, rule ID,
required scratch inventory, schema, hash, completion axis, or TDD responsibility is introduced.
Essential remains read-only; AC and seam choices retain the existing human ratification process.

Recognizing obligations and finding counterexamples remain semantic judgments, not mechanical
proof of completeness. Existing structural tests cannot establish this guidance's effectiveness.
Live existing-contract review with this guidance is unverified. Validate it by rerunning review
on the message project and checking whether it identifies the reported AC-010/AC-089 gap from
Essential and Acceptance. Record that observed result before claiming the omission is prevented.

## Trim after adversarial review (2026-09-19)

Deleted from `SKILL.md`: the Optional UI walkthrough section (opt-in, never loop-selected, and the
plan limited SKILL changes to Delivery closure) and the Delivery-closure restatements plus the
Identity-principle-3 restatement inside Existing-contract review. Kept there: apply the closing check
even when every AC is GREEN, report the promised-entry mapping (the replay's missing output), treat
non-canonical contracts or tests as evidence rather than coverage, do not re-ratify unchanged
contracts, respect review-only scope. The walkthrough rationale above remains a design note only.
The counterexample Coverage rewrite stays unbounded; bounding it to the staged batch would skip the
reported Domain-invariant gap. Its effectiveness remains unverified until a pre-AC-106 snapshot A/B.

## Closed-set application evidence (2026-09-19; reviewed 2026-10-08)

The closed-set judgment guidance already used in the global installation is retained in version
control. Coverage encoding belongs to `SKILL.md`; binding a forbidding `Then` belongs to
`seed-tdd/references/test-quality.md`. These remain judgment guidance, not new script-enforced
gates or identity principles.

In the sibling `message` project, commit `55cf2fd` contains the application records:

- `.scratch/seed-system/CAPABILITY_TARGET_REVIEW_2026-09-18.md` identifies AC-003's permitted-request
  test that did not exercise its forbidding clause, and AC-002's assertion that accepted a forbidden
  initial grant.
- `.scratch/seed-system/STAGED_CAPABILITY_TARGET_ACCEPTANCE.md` records Stage A/B ratification and
  promotion to AC-106/107, plus the corresponding test-repair plan.
- `.scratch/seed-system/ESSENTIAL_PROHIBITION_SWEEP_2026-09-19.md` applies the guidance to the
  Essential inventory and distinguishes forbidden constructions from permitted actions with no
  extra effect.
- `.scratch/seed-system/STAGED_SELF_AND_MASTER_ACCEPTANCE.md` records the next ratified
  application, promoted to AC-108/109.

The evidence grade is user-reported failure plus recorded application, not an independent A/B
skill-execution trace. The claim that the first draft used one AC per violation is supported only
by the commit trailer `Rejected: one AC per violation`; the rejected draft was not recovered.
The existing untracked `.scratch/seed-tdd/ac106-ac107-red.log` is product-bug evidence, not proof
that the guidance improved skill behavior; it is outside the cited commit.
Effectiveness remains unverified by an independent comparison; application records establish use.

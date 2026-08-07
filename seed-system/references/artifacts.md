# Seed System Artifacts

Use this reference when creating or updating seed-system files.

## Input contract

Read these seed-body files when present. Do not edit them.

```text
docs/ESSENTIAL_DOMAIN.md          # frozen inherited language
docs/ESSENTIAL_USECASE.md         # input coverage material only, not output canonical
docs/SEED_BODY_SYSTEM_PARKING.md  # SF-nnn seed evidence
docs/SEED_BODY_LATER.md           # context
docs/SEED_BODY_QUESTIONS.md       # context and upstream gaps
docs/SEED_BODY_CRITERIA.md        # seed-body gate evidence
```

If `ESSENTIAL_USECASE.md` is absent but `ESSENTIAL_DOMAIN.md` and clear seed-body notes exist, proceed
by asking the user which Essential outcomes must be covered. Do not invent missing Essential intent.
This is the minimum partial-input exception. If `ESSENTIAL_DOMAIN.md` is absent, or no seed-body
package exists at all, stop and route the user to seed-body instead of using conversation-only
evidence.

## Working paths

```text
.scratch/seed-system/SEED_SYSTEM_FLOWS.md         # raw system-flow evidence
.scratch/seed-system/SEED_SYSTEM_PRIOR.md         # category checklist, question material only
.scratch/seed-system/SEED_SYSTEM_HARVEST.md       # vocabulary and constraint harvest report
.scratch/seed-system/SEED_SYSTEM_CANDIDATES.md    # AC candidate queue
.scratch/seed-system/SEED_SYSTEM_IMPL_PROPOSAL.md # implementation defaults, after AC ratification
.scratch/seed-system/SEED_SYSTEM_TESTS.md         # test command and AC lifecycle records
.scratch/seed-system/SEED_SYSTEM_LATER.md         # explicit v1-out items
.scratch/seed-system/SEED_SYSTEM_QUESTIONS.md     # deferred questions and back-to-Essential gaps
.scratch/seed-system/SEED_SYSTEM_CRITERIA.md      # closing-gate demand document
.scratch/seed-system/SEED_SYSTEM_REJECTED.md      # explicit rejection log
```

Materialize accepted output under the target project's `docs/`:

```text
docs/ACCEPTANCE.md
docs/SEED_SYSTEM_IMPL_PROPOSAL.md
docs/SEED_SYSTEM_TESTS.md
docs/SEED_SYSTEM_LATER.md
docs/SEED_SYSTEM_QUESTIONS.md
docs/SEED_SYSTEM_CRITERIA.md
```

Do not create `SYSTEM_DOMAIN.md` or `SYSTEM_USECASE.md`.

## Evidence

Evidence is a turn reference plus a short quote. Code does not exist yet, so user utterance and
ratification are the provenance.

```md
Evidence:
- T7 "끊기면 두 번 될 수 있잖아" - original concern
- SF-007 (seed) "밖 취소 감지 방식 미결" - seed-body parking
- T12 (ratified) "맞아, 멱등키로 막자" - approved assumption
```

Use LLM knowledge to ask better questions or propose implementation defaults. Do not use it as
Evidence for canonical Acceptance.

## Raw flows

`SEED_SYSTEM_FLOWS.md` stores one raw system-flow fragment per item.

```md
## SYF-001

Fragment:
- [발주확인]을 채널에 올리다 중간에 끊기면 -> 재시도해도 한 번만 반영된다 ({멱등})

Serves:
- ESSENTIAL_USECASE #2 (발주확인)

Evidence:
- T7 "끊기면 두 번 될 수 있잖아" - original utterance

Notes:
- SF-004 seed absorbed; channel write path still needs seam selection.
```

Keep raw flows raw. Mark unratified system terms with `{term}`. Use inherited Essential terms as
`[Term]`. Rewrite into Acceptance candidates later; do not edit the corpus to look canonical.

## Candidate queue

Queue only `acceptance`, `implementation-hint`, and `question` candidates. Use `AC-{nnn}` only for
Acceptance scenarios that are staged for review; use `SC-{nnn}` for raw candidate records when an
Acceptance ID is not yet assigned.

```md
## SC-001

Type:
acceptance

Label:
[assumption]

Subject:
중복 없이 발주확인 반영

Content:
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

Blocked by:
- Seam confirmation
```

Labels are queue-only: `[assumption]`, `[conflict]`, `[unclassified-layer]`.
Canonical `ACCEPTANCE.md` must not contain labels or `{term}` markers.

## ACCEPTANCE.md

Record one atomic scenario per `## [Subject]`.

```md
# ACCEPTANCE

## [Return Created Order ID]

ID:
AC-001

Basis:
proposed

Seam:
- Order creation API

Given:
- A valid order request.

When:
- The customer creates an [Order].

Then:
- The response includes the created [Order] ID.

Evidence:
- T4 (ratified) "return the created order ID from the order creation API"
```

Requirements:

- `ID` is stable and unique.
- `Basis` is `inherited` when every clause traces to ratified Essential content, `proposed` when
  any clause adds system-designed behavior; when unsure, use `proposed`.
- `Seam` is the public boundary where every `Then` can be asserted.
- Given/When/Then use Essential language and observable outcomes.
- Evidence quotes user utterance or ratification.
- When an AC covers an inherited use case from `ESSENTIAL_USECASE.md`, Evidence also names it as
  `ESSENTIAL_USECASE #n (subject)`. If the number and subject later disagree, the subject governs.
- Split scenarios when one seam cannot faithfully observe all outcomes.

Contract hash fields are ID, Subject, Seam, Given, When, and Then. Exclude Basis and Evidence because
provenance changes must not stale the test.

When any included field changes semantically, recompute the hash and invalidate each affected test
record immediately:

```md
Status:
- gap — contract changed; test relink required

Notes:
- Previous test: tests/acceptance/order-create.test.ts
- Previous marker: @acceptance: AC-001 sha256:<stale-contract-hash>
```

Remove the stale active `Marker` field. A later `$tdd` cycle must update or replace the test, attach
the current marker, and demonstrate `red` or `green` before that status can be restored.

## SEED_SYSTEM_TESTS.md

Record the test command once and one lifecycle record per Acceptance ID.

```md
# SEED_SYSTEM_TESTS

Test command:
- npm test -- acceptance

Test directory:
- tests/acceptance

## MT-001

Acceptance:
- AC-001

Status:
- red

Test:
- tests/acceptance/order-create.test.ts

Marker:
- @acceptance: AC-001 sha256:<canonical-contract-hash>

Notes:
- RED confirmed before implementation.
```

Allowed statuses:

- `red`
- `green`
- `gap — <concrete reason>`

Use `gap — test harness not created yet` when the design is complete but `$tdd` has not authored
the runnable test. Replace the gap with `red` or `green` once a faithful test exists.
Use `gap — contract changed; test relink required` whenever an Acceptance semantic edit invalidates
a previously linked `red` or `green` record.

## SEED_SYSTEM_IMPL_PROPOSAL.md

Create this only after the Acceptance body is ratified.

```md
## IP-001

Area:
Synchronization

Default:
- Event queue plus channel webhook ingestion; polling is fallback for channels without webhook support.

Why:
- AC-001 requires retry-safe single reflection of [발주확인].

Alternatives:
- Full polling. Simpler, but weaker latency and rate-limit behavior.

Status:
- accepted | changed(T{n}) | alternative accepted(T{n}) | deferred

Deferred values:
- Concrete polling interval and queue product.
```

Implementation proposals may mention technology. Acceptance scenarios should not, unless the
technology choice is itself user-visible product behavior.

## Criteria, later, questions, rejected

- `SEED_SYSTEM_CRITERIA.md` is a demand document: list what must be true for the Acceptance body to
  be testable. Point to candidate or canonical AC IDs; do not paste answers as prose.
- `SEED_SYSTEM_LATER.md` stores explicit v1-out system flows with the reason and affected AC area.
- `SEED_SYSTEM_QUESTIONS.md` stores deferred decisions and `back-to-Essential` gaps. Do not resolve
  Essential gaps inside seed-system.
- `SEED_SYSTEM_REJECTED.md` stores explicit rejected candidates with reason and Evidence.

## Supply and demand

- Raw flows and candidates are supply.
- Criteria, inherited Essential coverage, and category priors are demand.
- Acceptance is the ratified contract.
- Tests are the executable constraint.

The loop pulls supply toward demand until the user can ratify a complete, testable Acceptance body.

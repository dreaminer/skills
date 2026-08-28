# Seed System Artifacts

Schemas for seed-system's contract files. Mechanical facts — the canonical contract-hash
computation, the structural gates, and the label list rejected in canonical documents — are owned
by `scripts/check-acceptance.py`. When a sentence here seems to disagree with the script, the
script is the reference and the sentence is the defect.

## Input contract

Read these seed-body files from the target project's `docs/` when present. Do not edit them.

```text
docs/ESSENTIAL_DOMAIN.md          # frozen inherited language
docs/ESSENTIAL_USECASE.md         # input coverage material only, not output canonical
docs/SEED_BODY_SYSTEM_PARKING.md  # SF-nnn seed evidence
docs/SEED_BODY_LATER.md           # context
docs/SEED_BODY_QUESTIONS.md       # context and upstream gaps
docs/SEED_BODY_CRITERIA.md        # seed-body gate evidence
```

If `ESSENTIAL_DOMAIN.md` is absent, or no seed-body package exists at all, stop and route the user
to seed-body. If `ESSENTIAL_USECASE.md` is absent but `ESSENTIAL_DOMAIN.md` and clear seed-body
notes exist, ask the user which Essential outcomes must be covered; do not invent missing
Essential intent.

## Definition links

In seed-system outputs, definition links appear only in `ACCEPTANCE.md` `Evidence:` and
`SEED_SYSTEM_IMPL_PROPOSAL.md` `Why:`. When either field names a definition from another
materialized seed document, point to its existing `##` section with
`[label](relative-path.md#GFM-heading-anchor)`.
Keep the referenced artifact identity in the label (`ESSENTIAL_USECASE #n (subject)`, `SF-nnn`,
or `AC-nnn`) so a definition link remains distinguishable from an unrelated Markdown link.

Keep parser-owned values (`ID`, `Basis`, `Acceptance`, `Risk`, `Layer`, `Status`, `Test`, `Marker`)
and contract-hashed values (Subject, Seam, Given, When, Then) as plain text. The canonical target
file set, GFM anchor resolution, and link-integrity checks live in `scripts/check-acceptance.py`.

## Working notes

`.scratch/seed-system/` is free-form; nothing in it carries a schema. Two shapes that have worked
— examples, not requirements.

A raw flow fragment. `[Term]` is inherited Essential language; `{term}` marks an unratified system
term. Canonical files carry neither queue labels nor `{term}` markers — the rejected-label list is
the script's.

```md
## SYF-001

Fragment:
- [발주확인]을 채널에 올리다 중간에 끊기면 -> 재시도해도 한 번만 반영된다 ({멱등})

Evidence:
- T7 "끊기면 두 번 될 수 있잖아" - original utterance
```

An Acceptance candidate staged for review: the scenario in its final `ACCEPTANCE.md` form, plus
the queue label `[assumption]` and a `Blocked by:` line while confirmation is pending.

## Evidence

Evidence is a turn reference plus a short quote. Code does not exist yet, so user utterance and
ratification are the provenance.

```md
Evidence:
- T7 "끊기면 두 번 될 수 있잖아" - original concern
- [SF-007 · 밖 취소 감지](SEED_BODY_SYSTEM_PARKING.md#sf-007) (seed)
  "밖 취소 감지 방식 미결" - seed-body parking
- T12 (ratified) "맞아, 멱등키로 막자" - approved assumption
```

Use LLM knowledge to ask better questions or propose implementation defaults, not as Evidence for
canonical Acceptance.

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
- When an AC covers an inherited use case from `ESSENTIAL_USECASE.md`, Evidence also links it in
  the exact label form `[ESSENTIAL_USECASE #n (subject)]`, for example:
  `[ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)`. The parenthesized
  subject is required for coverage checking; if the number and subject later disagree, the subject
  governs.
- Split scenarios when one seam cannot faithfully observe all outcomes.

The contract hash covers behavioral fields only — ID, Subject, Seam, Given, When, Then. Basis and
Evidence are provenance and stay outside it, so provenance edits never stale a test. The canonical
computation lives in `scripts/check-acceptance.py`; do not restate it in prose.

When any hashed field changes semantically, invalidate each affected test record immediately:

```md
Status:
- gap — contract changed; test relink required

Notes:
- Previous test: tests/acceptance/order-create.test.ts
- Previous marker: @acceptance: AC-001 sha256:<stale-contract-hash>
```

Remove the stale active `Marker` field. A later `$seed-tdd` cycle must update or replace the test,
attach the current marker, and demonstrate `red` or `green` before that status can be restored.

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

Risk:
- A duplicate delivery creates two order confirmations.

Layer:
- integration

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

- `red` — the linked test fails because the selected behavior is absent.
- `green` — the linked test passes under the current marker.
- `gap — <concrete reason>` — a faithful runnable test cannot exist yet, with the concrete reason.

Common gap wordings: `gap — test harness not created yet` (design complete, `$seed-tdd` has not
authored the runnable test) and `gap — contract changed; test relink required` (a semantic
Acceptance edit invalidated a linked record).

Implementation handoff needs RED evidence regardless of Basis; a gap is honest but not verified.
Missing behavior uses an observed working-tree RED. Behavior already present before its AC slice
may instead use `$seed-tdd`'s isolated sensitivity RED: the record becomes `green` with the Notes
token `PREEXISTING_GREEN: <mutation and failing assertion evidence>`; until that proof exists it
stays `gap — RED not observed; sensitivity unproven`.

Every record states its worst v1-relevant failure outcome as `Risk` and the narrowest harness that
can refute it as `Layer`: `unit` (policy, calculation, boundary values), `integration` (data or
external connections), `browser` (user-visible flow), or `observability` (performance or
operations). Seam says where to observe; Layer says what kind of test refutes the risk.

## SEED_SYSTEM_IMPL_PROPOSAL.md

Create this only after the Acceptance body is ratified.

```md
## IP-001

Area:
Synchronization

Default:
- Event queue plus channel webhook ingestion; polling is fallback for channels without webhook support.

Why:
- [AC-001 · Return Created Order ID](ACCEPTANCE.md#return-created-order-id) requires retry-safe
  single reflection of [발주확인].

Alternatives:
- Full polling. Simpler, but weaker latency and rate-limit behavior.

Status:
- accepted | changed(T{n}) | alternative accepted(T{n}) | deferred

Deferred values:
- Concrete polling interval and queue product.
```

Implementation proposals may mention technology. Acceptance scenarios should not, unless the
technology choice is itself user-visible product behavior.

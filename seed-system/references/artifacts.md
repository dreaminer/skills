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

Delivery closure requires the canonical Essential use-case inventory. Treat a missing seed-body
package, missing `ESSENTIAL_DOMAIN.md` or `ESSENTIAL_USECASE.md`, or a use-case file with no
parseable current `## [Subject]` entries as missing input. Route it through seed-body human review
and continue only with the canonical inventory ratified there.

## Definition links

In seed-system outputs, definition links appear in `ACCEPTANCE.md` `Evidence:` and `Closes:`, and
in `SEED_SYSTEM_IMPL_PROPOSAL.md` `Why:`. When any such field names a definition in another
materialized Seed document, point to its existing `##` section with
`[label](relative-path.md#GFM-heading-anchor)`. Keep the referenced artifact identity in the label
(`ESSENTIAL_USECASE #n (subject)`, `SF-nnn`, or `AC-nnn`) so a definition link remains
distinguishable from an unrelated Markdown link.

Keep parser-owned values (`ID`, `Basis`, `Acceptance`, `Risk`, `Layer`, `Status`, `Test`, `Marker`)
and contract-hashed values (Subject, Seam, Given, When, Then) as plain text. `Closes` is the
deliberate Acceptance exception: it contains exact Essential definition links, while the normalized
Essential subjects named by valid links participate in the contract hash. Link numbering, path
spelling, and anchor encoding remain link-integrity concerns rather than test obligations. The
canonical target file set, GFM anchor resolution, and link-integrity checks live in
`scripts/check-acceptance.py`.

Realization records add one deliberate exception: `Proposal:` is an inline definition link whose
label contains its `IP-nnn`. Other parser-owned values remain plain text. The checker validates the
target `## IP-nnn` heading without placing Markdown inside the realization hash.

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

Closes:
- [ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)

Evidence:
- T4 (ratified) "return the created order ID from the order creation API"
- [ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)
```

Requirements:

- `ID` is stable and unique.
- `Basis` is `inherited` when every clause traces to ratified Essential content, `proposed` when
  any clause adds system-designed behavior; when unsure, use `proposed`.
- `Seam` is the public boundary where every `Then` can be asserted.
- Given/When/Then use Essential language and observable outcomes.
- `Closes` is optional. Put it only on a scenario ratified as the supported-entry reachability
  proof for one or more inherited Essential use cases. Each value is an exact
  `ESSENTIAL_USECASE` definition link in the same label form required by Evidence. The test must
  enter as an intended consumer through a supported entry, traverse the maintained composition
  for in-scope collaborators, and observe the outcome through a supported output. A component
  API qualifies when it is itself the target's supported delivery interface. Independently
  promised consumer entries need their own closing scenarios; incidental implementation adapters
  do not.
- Evidence quotes user utterance or ratification.
- When an AC covers an inherited use case from `ESSENTIAL_USECASE.md`, Evidence also links it in
  the exact label form `[ESSENTIAL_USECASE #n (subject)]`, for example:
  `[ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)`. The parenthesized
  subject is required for coverage checking; if the number and subject later disagree, the subject
  governs.
- Split scenarios when one seam cannot faithfully observe all outcomes.

The contract hash covers test obligations — ID, Subject, Seam, Given, When, Then, and the normalized
Essential Subject set named by `Closes` when present. Basis and Evidence are provenance and stay
outside it, so provenance edits never stale a test. Adding, removing, or changing a `Closes`
Subject changes which Essential outcomes the test claims to discharge and therefore stales its
marker. Renumbering or re-encoding a link to the same Subject does not. The canonical computation
lives in `scripts/check-acceptance.py`; do not restate it in prose.

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

Every record states its worst v1-relevant adverse outcome as `Risk`, not a paraphrase of the AC
Subject or `Then`, and the narrowest harness that can refute it as `Layer`: `unit` (policy,
calculation, boundary values), `integration` (data or external connections), `browser`
(user-visible flow), or `observability` (performance or operations). Seam says where to observe;
Layer says what kind of test refutes the risk. If the proposed harness cannot refute the stated
Risk, revise the Seam/Layer or split the scenario before handoff.

### Realization lifecycle records

The same `SEED_SYSTEM_TESTS.md` carries a realization record only after `$seed-realize` has
evidence for a non-deferred implementation proposal. No record means implicit `pending`; do not
backfill empty records merely to enumerate the proposal document.

```md
## IP-001

Proposal:
- [IP-001 · Synchronization](SEED_SYSTEM_IMPL_PROPOSAL.md#ip-001)

Status:
- verified

Marker:
- @realization: IP-001 sha256:<canonical-realization-hash>

Evidence:
- code: implementation/src/outbox.ts
- integration: implementation/tests/outbox.integration.test.ts
- command: npm test -- outbox.integration.test.ts (exit 0)

Notes:
- Retry and restart behavior were exercised against SQLite.
```

Allowed statuses are `pending` and `verified`. A pending record omits `Marker` and `Evidence`.
A verified record contains at least one existing project-relative path with kind `artifact`,
`code`, `config`, `integration`, `migration`, or `deployment`, plus one `command` line recording
the observed exit result. Repository artifacts and dry runs prove only what they observe; they do
not prove a live deployment.

The checker owns path, marker, and completion mechanics. `$seed-realize` owns the judgment that
the evidence proves the selected Default.

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

`Status` is `accepted`, `changed(T{n})`, `alternative accepted(T{n})`, or `deferred`. When a
different choice is accepted, rewrite `Default` to the selected choice and keep the rejected choice
under `Alternatives`.

The realization hash covers only the proposal heading `IP-nnn` and normalized `Default` lines.
Rationale and provenance edits do not stale evidence; a selected-Default edit does. The canonical
computation lives in `scripts/check-acceptance.py`.

Every non-deferred proposal forms the closed-world realization set. Deferred proposals need no
lifecycle record. Missing records are legal during design and fail `--complete realization` by
their exact `IP-nnn`.

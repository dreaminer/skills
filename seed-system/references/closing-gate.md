# Seed System Closing Gate

Use this reference when divergence appears complete.

The convergence order is fixed:

```text
scan -> harvest -> Acceptance staging -> criteria -> batch ratification
     -> implementation proposal -> test handoff records -> materialization
```

## 1. Scan once

Scan the working body once before creating or updating criteria. Route blockers instead of solving
them silently.

| Check | Question | Route |
|---|---|---|
| Coverage | Does each inherited Essential outcome have at least one AC naming it in Evidence? | Criteria |
| Testability | Can every Then be observed at the declared seam? | Criteria |
| Atomicity | Does each scenario test one behavior at one seam? | Candidate rewrite |
| Boundary | Did implementation details leak into Acceptance? | Candidate rewrite or proposal |
| Failure paths | Are relevant failure, retry, reverse, duplicate, and conflict flows included? | Criteria |
| Vocabulary | Are terms inherited or ratified? | Candidate rewrite |
| v1 boundary | Did LATER material leak into v1 Acceptance? | Later or criteria |
| Essential gap | Is a new product intent needed? | Questions, back-to-Essential |
| Implementation fit | Can the proposal plausibly realize every AC? | Proposal revision |
| Test lifecycle | Does each AC have red, green, or concrete gap? | Test record |

Expose at most three blockers at a time. Prefer blockers that affect Acceptance completeness or
testability over polish.

## 2. Harvest and rewrite

Harvest vocabulary and constraints from `SEED_SYSTEM_FLOWS.md`; do not publish a System Domain.

Use the harvest to:

- normalize scenario wording into inherited Essential language;
- identify load-bearing state, boundary, retry, idempotency, and conflict concepts;
- find scenario splits where one raw flow contains multiple observable outcomes;
- propose seams that can observe the outcomes.

Stage one `acceptance` candidate per atomic scenario.

## 3. Criteria

Create `SEED_SYSTEM_CRITERIA.md` as the demand document for testable completion.

```md
# SEED_SYSTEM_CRITERIA

## Required questions

- [x] Q1. [coverage] 발주확인 retry flow has an AC scenario. -> AC-001
- [ ] Q2. [testability] AC-003 cancellation conflict has an observable seam. -> unanswered
- [x] Q3. [failure] duplicate delivery outcome is stated. -> AC-001

## Deferred

- Q9. audit log retention duration -> SEED_SYSTEM_QUESTIONS.md
```

Criteria answers must point to staged or canonical Acceptance IDs, later/questions records, or
implementation proposal IDs. Do not bury answer prose in criteria.

Changing the criteria list requires meta-ratification again. Merely checking off an existing
criterion does not.

## 4. Batch ratification

Use two stages unless the user explicitly asks for a quick combined pass.

Stage A asks whether the criteria are the right definition of enough:

```text
완성도를 판정하기 위한 Acceptance 기준은 이 목록이면 충분해?
```

Stage B presents the full staged `ACCEPTANCE.md`, LATER summary, QUESTIONS summary, and notable
rejections in one batch. Group scenarios by `Basis`: for `inherited`, ask the user to confirm the
mapping to ratified Essential content and that the declared seam observes its result; for
`proposed`, ask for content ratification:

```text
이 Acceptance 몸체로 v1 계약을 확정할까? 바꿀 항목만 짚어줘.
```

Apply partial edits only to affected scenarios, then re-present the batch. Rejected candidates go
to `SEED_SYSTEM_REJECTED.md`.

## 5. Implementation proposal

Enter only after Acceptance is ratified.

Derive proposal areas from the accepted scenarios and raw constraints:

- storage/state model;
- external ports and authentication;
- synchronization, retry, idempotency, ordering, and conflicts;
- mirroring or non-API automation;
- stack and test harness;
- deployment and operations.

For each area, propose one default, why it satisfies specific AC IDs, alternatives, status, and
deferred fine values. Let the user mark only changes.

Implementation choices do not modify Acceptance. If a choice cannot satisfy an AC, revise the
proposal or return to Acceptance ratification if the user wants to change the product behavior.

## 6. Test handoff records

Create or update `SEED_SYSTEM_TESTS.md` after Acceptance ratification.

For each AC:

- choose or confirm the seam before test authoring;
- state the worst-failure `Risk` and pick the narrowest refuting `Layer` as specified in
  [artifacts](artifacts.md);
- record `gap — test harness not created yet` if no test exists;
- after a semantic Acceptance edit, invalidate affected `red`/`green` records as specified in
  [artifacts](artifacts.md);
- when `$tdd` authors the test, replace the gap with `red` once the missing behavior fails as
  expected;
- after implementation, record `green` only when the current marker hash is linked and the test
  passes.

Semantic review is required. The marker proves lexical linkage only. Check that every Then has an
observable assertion at the declared seam and that the test does not pin internals.

## 7. Materialization

After Acceptance and implementation proposal ratification, write the accepted files under `docs/`.

If no tests have been authored yet, materialization may still finish as a design handoff, but the
status is not implementation-complete. Return a `$tdd` handoff with:

- AC IDs and contract hashes;
- seams;
- expected assertions per Then;
- worst-failure risk and chosen verification layer per AC;
- proposed test command and directory;
- current gaps.

Before claiming completion, run `scripts/check-acceptance.py` against the project `docs/` and
declared test directory, and resolve every reported failure. It verifies structure, hash-marker
linkage, and coverage; semantic review stays with the human and agent.

Completion requires every v1 AC to be `green` with the current hash. Otherwise report the exact
non-complete state: RED pending implementation, gap pending test harness, or question pending
ratification.

## 8. Next-step routing

At the end, present categories only unless the user asks to continue:

- `$tdd` test authoring;
- PRD/spec;
- tickets;
- prototype;
- implementation.

Do not start the next step automatically.

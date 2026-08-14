---
name: seed-tdd
description: Implements a ratified seed-system package as hash-linked Acceptance tracer bullets, proving RED before minimal GREEN.
disable-model-invocation: true
---

# Seed TDD

Advance a completed `seed-system` handoff to working software one Acceptance tracer bullet at a
time.

```text
ratified Acceptance -> hash-linked test -> RED -> minimum implementation -> GREEN
```

This standalone skill embeds the generic `$tdd` principles.

## Authority

- Keep `docs/ESSENTIAL_DOMAIN.md` and `docs/ACCEPTANCE.md` read-only as the inherited language and
  human-ratified behavior contract.
- Follow ratified choices in `docs/SEED_SYSTEM_IMPL_PROPOSAL.md` as the implementation defaults.
- Restrict seed-document writes to lifecycle fields in `docs/SEED_SYSTEM_TESTS.md`.
- Write project-owned tests, production code, and the minimum test harness already authorized by
  the proposal.
- Route behavioral or material design changes to `$seed-system`, preserving the current evidence
  and lifecycle state.

## 1. Establish a valid handoff

Resolve the target project and require all four documents above. From the project root, locate and
run `python3 <seed-system-skill>/scripts/check-acceptance.py --docs <project-docs>` without
`--complete`; `<seed-system-skill>` is the `seed-system/` directory installed beside this skill,
the same default `contract-markers.py` resolves. Read the repository instructions, relevant ADRs,
and `CONTEXT.md` when present. Resolve the declared test command and directory, the accepted stack
and harness, and the unmodified test baseline. When the handoff contains `gap — test harness not
created yet`, record the baseline as `not yet runnable`; Step 2 owns slice selection.

Classify a missing document, invalid contract package, unresolved material choice, or in-scope
baseline failure that obscures the selected AC as `SEED_TDD_BLOCKED` with its exact route. The
handoff is established only when the checker passes, required choices are ratified, and the
baseline is either recorded runnable evidence or the accepted harness gap.

## 2. Select one tracer bullet

Resume an existing `red` record first. Otherwise select, in order: a contract-change relink gap;
the first `gap — test harness not created yet` that establishes the thinnest end-to-end path;
another gap enabled by current GREEN slices and its stated `Risk`; then document order.

Run `python3 <seed-tdd-skill>/scripts/contract-markers.py --docs <project-docs>` only to obtain
current markers. Select exactly one lifecycle record, then read its AC from `ACCEPTANCE.md` and its
`Risk` and `Layer` from `SEED_SYSTEM_TESTS.md`. Selection is complete only when that selected pair
supplies a current marker, declared `Seam`, `Risk`, `Layer`, test command, and chosen
project-relative test destination.

## 3. Prove RED

Before assessing the first selected test in an invocation, read
[Acceptance test quality](references/test-quality.md) completely and apply every rule to every
slice. For an existing RED, rerun its narrow test and verify that its marker and failure still match
the current AC. Create the minimum accepted harness only when the selected slice needs it, and build
it so the declared test command runs as written; route a declared command that cannot be made to run
to `$seed-system` rather than amending it.

Reserve `red` for a failure showing the selected behavior is absent: an assertion derived from
`Then` fails, or the declared `Seam` itself is missing where the test reaches for it. Classify
harness, build, fixture, configuration, infrastructure, test-discovery failures, and import failures
outside that seam as concrete gaps. Never add behavior-free production code to turn a missing seam
into an assertion failure. An immediate pass follows the reference's `UNEXPECTED_GREEN` branch; a
successful sensitivity proof records the already-present behavior as GREEN and returns to Step 2,
while an unproven test remains a concrete gap.

RED is complete only when the narrow command exhibits a failure satisfying the reference's RED
criteria, the lifecycle record contains `Status: red`, the test path and exact current marker, and
the seed-system checker passes. Production implementation begins only after this criterion holds.

## 4. Reach minimum GREEN

Implement the smallest production slice that satisfies the selected AC through its ratified seam
and accepted implementation proposal. Keep future AC behavior and optional refactoring outside the
slice. Use real internal collaborators; isolate environmental boundaries according to the test
quality reference.

Run the selected test and the maintained relevant suite. GREEN is complete only when both pass,
the current-marker lifecycle record says `green`, its execution evidence is recorded, and the
seed-system checker passes. A conflict with another AC or ratified implementation choice routes to
`$seed-system` with both sources and the observed failure.

## 5. Complete the implementation

Return to Step 2 until every AC is GREEN or a routed blocker is reached. When every record is GREEN,
audit every `Then` against its assertion at the declared seam. Map every `accepted`, `changed`, or
`alternative accepted` implementation choice to code, configuration, or test evidence. Exclude
each item's `Deferred values` and every item whose `Status` is `deferred`. Run the declared full
suite and required repository checks, then run
`python3 <seed-system-skill>/scripts/check-acceptance.py --docs <project-docs> --complete` from the
project root.

Return `SEED_TDD_COMPLETE` only when every `Then` is faithfully asserted, the full suite passes,
every non-deferred accepted proposal choice has implementation evidence, and the completion checker
reports every v1 AC current-hash GREEN. Otherwise return
`SEED_TDD_BLOCKED` with the affected AC, unchanged upstream contract, preserved lifecycle evidence,
and one exact next route.

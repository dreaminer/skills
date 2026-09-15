---
name: seed-tdd
description: Implements one ratified Seed Acceptance contract at a time as a hash-linked test from faithful RED to minimal GREEN. Use when the user explicitly requests seed-tdd or an active seed-loop selects the TDD owner.
---

# Seed TDD

Advance the Acceptance axis one tracer bullet at a time.

```text
ratified AC -> current-hash test -> faithful RED -> minimum behavior -> GREEN
```

This skill owns AC lifecycle only. It does not prove every implementation proposal, perform a
repository-wide realization audit, or write IP lifecycle records.

## Authority

- Keep `docs/ESSENTIAL_DOMAIN.md`, `docs/ACCEPTANCE.md`, and
  `docs/SEED_SYSTEM_IMPL_PROPOSAL.md` read-only.
- Write only AC lifecycle fields in `docs/SEED_SYSTEM_TESTS.md` and the selected test/production
  slice.
- Read [Acceptance test quality](references/test-quality.md) completely before the first RED of
  every invocation; it solely owns RED classification and test-double boundaries.
- Resolve the sibling `seed-system/scripts/check-acceptance.py`; the checker solely owns hashes,
  linkage, and completion predicates.

## 1. Establish the handoff

From the project root, inspect the Seed documents, repository instructions, test command, and
current baseline. Run the checker without completion scope. Missing/invalid Seed documents,
unratified choices, or a baseline failure that obscures the selected AC returns
`SEED_TDD_BLOCKED` with one exact owner.

## 2. Select one AC

For a requested behavior recheck, include the requested ACs even when their records are GREEN.
Inspect their tests against `references/test-quality.md` and run the selected scope with current
inputs; use the observed results rather than historical lifecycle notes. If a test is missing or
unfaithful, return to the normal RED/GREEN slice; contract gaps go to `seed-system`. Honor an
inspection-only request by reporting findings without changing production, contracts, or lifecycle
records. Verification of unchanged passing behavior does not require manufacturing a new RED.

For a recheck, select only requested ACs still lacking current verification evidence, one at a time
in document order; finish that scope without replaying already-checked GREEN records. For normal
implementation, choose exactly one record in this order:

1. an existing `red` record;
2. `gap — contract changed; test relink required`;
3. `gap — test harness not created yet` for the thinnest end-to-end path;
4. another gap enabled by current GREEN slices;
5. document order.

Within the same status priority, prefer an AC with `Closes`; replay a contract-changed closing AC
before selecting a new ordinary gap.

Use `scripts/contract-markers.py` only to obtain current markers. Selection is complete when the
AC, Seam, Risk, Layer, any `Closes` obligations, test command, and project-relative test
destination are known.

## 3. RED

Create only the harness needed by this slice. Run the narrow test and classify the observed result
using `references/test-quality.md`. An immediate pass follows its `UNEXPECTED_GREEN` branch; do
not label an unobserved failure RED. Record the current `@acceptance` marker in the test and AC
lifecycle record.

If faithful RED cannot be observed because a concrete non-deferred implementation choice must
exist first, preserve the AC lifecycle evidence and return:

```text
SEED_TDD_BLOCKED
Owner: seed-realize
Evidence: <clickable AC and IP definition links plus observed failure>
Need: <one realizable capability>
Resume: <narrow command that should reach RED afterward>
```

Do not broaden this route to a global implementation audit; the blocker must affect the selected
AC's executable seam.

## 4. Minimum GREEN

Implement the smallest production behavior satisfying the selected AC through its ratified seam.
Follow relevant ratified defaults, but do not verify unrelated IPs. Run the narrow test and maintained
relevant suite. Mark the AC `green` only when both pass with the current hash and execution evidence
is recorded. Contract conflicts with Essential, another AC, or a ratified choice route to
`$seed-system`; distinguish them from test or implementation defects using the Essential
consistency guidance in `references/test-quality.md`.

## 5. Continue or complete

For a requested recheck, first finish current verification of every selected AC or report the
remaining blocker; all records being historically GREEN does not end that work. An inspection-only
run reports its findings and executed scope without converting them into an implementation-complete claim.

Return to selection until blocked or all AC records are current-hash GREEN. Then audit each `Then`
against its assertion at the declared Seam and each closing AC against the supported-entry rules
in `references/test-quality.md`, run the declared full suite and required repository checks, and
run:

```sh
python3 <seed-system-skill>/scripts/check-acceptance.py --docs <project-docs> --complete acceptance
```

Return `SEED_TDD_COMPLETE` only for this Acceptance axis. State explicitly that realization is a
separate axis. In every report, a referenced Seed definition is a clickable link to its exact `##`
heading; code and tests use project-relative paths.

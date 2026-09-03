# Acceptance Test Quality

Apply every rule here when creating or repairing a Seed TDD test.

## Contract binding

- Use the exact marker printed by `<seed-tdd-skill>/scripts/contract-markers.py`:
  `@acceptance: AC-nnn sha256:<hash>`.
- Exercise the AC's declared public `Seam` and observe results exclusively through that interface.
- Make the Given facts explicit, perform the When action once, and assert every observable clause
  in Then.
- Name the actor goal or automatic trigger and final domain result.
- Treat the contract's examples or independent known literals as the sole source of expected
  values.
- Use realistic, non-degenerate facts and keep each cause beside its observable effect.

Several assertions may express one logical outcome. A file may cover several ACs, but each lifecycle
record names a file containing that AC's current marker. The marker proves lexical linkage only;
the reached seam and assertions prove semantic fidelity.

## Essential closure

When an AC has `Closes`, its test is also the reachability proof for every linked Essential use
case:

- Enter through a supported entry point as an intended consumer invokes the Seed target.
- Traverse the maintained composition that entry uses for in-scope collaborators.
- Observe the ratified outcome through a supported output. Private state and side-channel
  assertions may supplement that observation but cannot carry closure.
- A component API is the supported entry only when it is itself the target's delivered consumer
  interface. An application, executable, or worker closer reaches the component through its
  maintained runtime wiring.
- Decide closure from the supported entry and maintained composition, independently of `Layer`.
  A pure library can close through an in-process public API, while an `integration` label can still
  hide disconnected module composition.
- Give each independently promised consumer entry a closing AC. Incidental adapters that
  Essential intent never promised need no duplicate closer.

Before RED, require the lifecycle `Risk` to name an adverse v1 consequence and the proposed
harness to refute that consequence. A paraphrase of the AC Subject or `Then` does not meet this
bar. If either condition fails, keep the lifecycle evidence intact and return `SEED_TDD_BLOCKED`
with `Owner: seed-system`.

## Test doubles

Exercise real internal collaborators. Place test doubles at environmental boundaries: external
services, time, randomness, networks, external stores, or unavoidable filesystem I/O. Give each
double a specific boundary contract; prefer operation-specific interfaces over a generic
conditional fetcher.

Acceptance assertions observe domain results. Internal calls, private methods, collaborator call
counts, and database side-channel queries remain diagnostic implementation details.

## RED classification

A faithful RED has all three properties:

1. the test runner discovers and executes the selected test;
2. the test reaches, or fails while reaching for, the declared public seam; and
3. the failure shows the selected behavior is absent — either an assertion derived from a `Then`
   clause fails, or that seam's own module, attribute, or implementation is missing.

Record harness, build, syntax, fixture, configuration, infrastructure, discovery failures, and
import failures outside the selected seam as `gap — <concrete reason>`. These outcomes require
harness repair or investigation while preserving the assertion. Do not add behavior-free production
code to convert a missing seam into an assertion failure; the missing seam is the stronger evidence
of the two, and the stub is production code written before RED.

## UNEXPECTED_GREEN

When a new current-marker test passes before implementation of its AC:

1. verify that it reaches the declared seam and asserts every `Then`;
2. confirm the behavior was already present in the tree as it stood before this slice, which after
   the first slice is no longer the handoff baseline;
3. create an isolated copy with `mktemp -d` or its platform equivalent, register cleanup, and apply
   there one reversible mutation that removes or corrupts the reached behavior;
4. run the narrow command and require the test to fail at the intended `Then` assertion; and
5. discard the scratch copy, rerun the narrow command in the untouched original tree, require
   GREEN, and record the test path, current marker, `Status: green`, and the note
   `PREEXISTING_GREEN: <mutation and failing assertion evidence>`.

A passing test without this sensitivity proof remains
`gap — RED not observed; sensitivity unproven`. A mutation that changes a different behavior does
not qualify.

## Lifecycle update after RED

Preserve the record's `Acceptance`, `Risk`, and `Layer`. Set:

```md
Status:
- red

Test:
- <project-relative-test-path>

Marker:
- @acceptance: AC-nnn sha256:<current-hash>

Notes:
- RED: <command> failed at <Then-derived assertion> with <observed missing outcome>.
```

Run the seed-system checker after the update. Its success proves structure and hash linkage; inspect
the test separately for the semantic rules above.

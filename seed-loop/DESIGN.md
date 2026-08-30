# Seed Loop — Design Decisions

## Decision

`seed-loop` is the single entry/resume router for four separately owned concerns:

```text
seed-body -> seed-system -> (seed-tdd <-> seed-realize) -> aggregate completion
```

The arrows are dependencies, not a strict waterfall. An AC may need a concrete IP before faithful
RED, and realization may expose a ratified system choice that must return upstream.

The loop owns only target continuity, next-owner selection, replay order, and aggregate completion.
It does not restate leaf procedures or artifact schemas. It loads one sibling leaf at a time because
a skill cannot invoke another user-only skill by name.

## State and evidence

No canonical phase-state file or new stable ID exists. Current documents, checker results, and leaf
terminals determine state. `.scratch/seed-loop/ACTIVE_CHANGE.md` is optional ephemeral memory for a
change spanning turns or owners.

The checker exposes two independent completion axes. Acceptance GREEN does not imply that ratified
storage, runtime, scheduler, migration, or deployment choices are realized. Plain `--complete`
remains backward-compatible syntax for strict aggregate `--complete all`.

## Ownership

- `seed-body`: Essential language and outcomes.
- `seed-system`: human-ratified AC and IP choices plus artifact schema.
- `seed-tdd`: AC RED/GREEN lifecycle.
- `seed-realize`: non-deferred IP realization lifecycle and evidence judgment.
- `seed-system/scripts/check-acceptance.py`: mechanical predicates.
- `seed-loop`: selection order and aggregate terminal.

## Change gates

User ratification is required before adding a canonical state artifact, stable ID family, parallel
owners, automatic rollback, a new completion axis, or moving a leaf's human-ratification boundary.
Routing changes must replace an existing selection rule rather than duplicate leaf instructions.

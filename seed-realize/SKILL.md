---
name: seed-realize
description: Realizes ratified non-deferred Seed implementation proposals as real adapters, wiring, migrations, configuration, or operational evidence. Use when an active seed-loop selects the realization owner, seed-tdd is blocked by a concrete IP, or Acceptance is green while implementation proposals remain unverified.
---

# Seed Realize

Advance the realization axis one `IP-nnn` at a time.

```text
ratified Default -> real artifact -> authoritative execution -> verified evidence
```

This skill closes the gap between behavior proven at an Acceptance seam and a ratified technical
choice that must exist in the actual system. It is not another Acceptance TDD loop or a generic
repository implementation skill.

## Authority

- Keep `docs/ACCEPTANCE.md` and `docs/SEED_SYSTEM_IMPL_PROPOSAL.md` read-only.
- Write IP lifecycle records only in `docs/SEED_SYSTEM_TESTS.md`, plus the selected implementation,
  configuration, migration, wiring, and verification artifacts.
- Read [Realization evidence](references/realization-evidence.md) completely before selecting proof.
- Resolve the sibling `seed-system/scripts/check-acceptance.py`; it solely owns proposal parsing,
  hashes, stale markers, links, and completion predicates.

## 1. Establish the handoff

From the project root, inspect repository instructions, Seed documents, current architecture, and
baseline checks. Run the checker without completion scope. If the proposal is absent, unratified,
contradictory, or structurally invalid, return `SEED_REALIZE_BLOCKED` with `Owner: seed-system`.

## 2. Select one proposal

Choose exactly one non-deferred proposal in this order:

1. the IP named by an active `SEED_TDD_BLOCKED` handoff;
2. a stale verified record whose `Default` changed;
3. an explicit `pending` record;
4. a missing record, in proposal document order.

Run `scripts/realization-markers.py --docs <project-docs>` to obtain current markers. Read the
selected `Default`, linked AC definitions in `Why`, existing implementation, and the narrowest
evidence that could actually distinguish realized from merely planned.

## 3. Realize the selected Default

Implement the smallest coherent vertical capability promised by the selected Default: real adapter,
wiring, persistence, migration, scheduler, configuration, deployment artifact, or comparable system
boundary. Reuse current AC tests but do not create fake ACs for technical choices with no natural
user-visible behavior.

Choose routine implementation details within the ratified ACs and Default. A missing decision
about promised behavior or the technical choice itself is material underspecification and belongs
to `$seed-system`.

If the selected Default is wrong, materially underspecified, or cannot be observed with the current
authorized environment, do not silently substitute it or claim live operation. Route the exact
choice to `$seed-system` for change or deferral.

## 4. Verify and record

Run the narrow authoritative command and relevant maintained suite. Only after the evidence passes,
append or update the selected `## IP-nnn` record in `SEED_SYSTEM_TESTS.md` using the sibling
[artifact schema](../seed-system/references/artifacts.md):

- `Proposal` links to the exact proposal heading;
- `Status` is `verified`;
- `Marker` is the current `@realization` hash;
- `Evidence` names existing project-relative artifacts and the observed command result.

Never edit the proposal to make evidence fit. Never use repository configuration or a dry run as
proof of a live deployment.

## 5. Continue, resume, or complete

Run `--complete realization`. If the selected IP unblocked an AC, return
`SEED_REALIZE_PROGRESS` with `Resume owner: seed-tdd` and its narrow command; the loop decides the
next owner. Otherwise continue one IP at a time.

Return `SEED_REALIZE_COMPLETE` only when every non-deferred IP is current-hash verified, the relevant
suite passes, and `--complete realization` succeeds. Return `SEED_REALIZE_BLOCKED` with one owner,
clickable definition links, observed evidence, needed decision/capability, and exact resume command.
Code and tests are reported as project-relative paths.

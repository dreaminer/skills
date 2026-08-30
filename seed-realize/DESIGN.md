# Seed Realize — Design Decisions

## Decision

`seed-realize` owns the lifecycle from a ratified non-deferred `IP-nnn` Default to real artifact and
execution evidence. It exists separately because `seed-tdd` owns one observable Acceptance behavior,
while some ratified choices are infrastructure or operations with no honest standalone AC.

No new canonical document or ID family is introduced. `SEED_SYSTEM_IMPL_PROPOSAL.md` remains the
human-ratified choice source written by `seed-system`; `SEED_SYSTEM_TESTS.md` carries mutable AC and
IP lifecycle records. A missing IP record is implicit pending.

## Ownership

- `seed-system/references/artifacts.md`: artifact schemas.
- `seed-system/scripts/check-acceptance.py`: proposal set, hash, linkage, and completion mechanics.
- `seed-realize/SKILL.md`: one-IP execution and evidence judgment.
- `seed-realize/references/realization-evidence.md`: evidence kinds and scope limits.
- `seed-loop/SKILL.md`: TDD/realization selection order.

## Change gates

User ratification is required before moving these ownership boundaries, adding a canonical artifact
or stable ID, broadening `verified` beyond observable evidence, or merging realization back into
Acceptance completion.

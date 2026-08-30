---
name: seed-loop
description: Orchestrates an explicitly started greenfield Seed run across Essential shaping, Acceptance design, Acceptance TDD, and implementation realization. Use to start or resume seed-loop, continue its active human ratification, or receive a Seed leaf completion, progress, or blocker.
---

# Seed Loop

The user calls `$seed-loop <project path or service slice>` once. After that, route among
`seed-body`, `seed-system`, `seed-tdd`, and `seed-realize` without requiring the user to invoke each
leaf again.

The initial call authorizes normal transitions, not human ratification. Stop at every leaf-owned
question and apply only the user's answer. Keep one active owner at a time.

## Enter or resume

Identify target, active owner, and outstanding decision from the latest leaf terminal plus current
files. If target is the only missing fact, ask once. A project with substantial implementation but
no Seed artifacts is not a greenfield recovery target; return `SEED_LOOP_BLOCKED` and recommend an
evidence-recovery flow. A Seed implementation already in progress may resume normally.

Resolve each sibling leaf installed beside this skill. Load and follow only the selected leaf's
`SKILL.md`; on a transition, release the previous leaf instructions before loading the next. Direct
leaf invocation remains available for users who intentionally want only one phase.

## Compute the next owner

Observe the target after every entry and leaf return. The checker is the sole source of structural,
link, hash, and completion facts. Select exactly one owner in this order:

1. An active upstream decision or change goes to its original owner, then affected downstream work
   is replayed in dependency order.
2. Missing or invalid Essential artifacts go to `seed-body`; missing, unratified, or structurally
   invalid Acceptance/proposal artifacts go to `seed-system`.
3. A current `SEED_TDD_BLOCKED` naming `Owner: seed-realize` goes to `seed-realize` before selecting
   another AC. After `SEED_REALIZE_PROGRESS` names `Resume owner: seed-tdd`, resume that AC.
4. Any non-green, missing, or stale AC lifecycle record goes to `seed-tdd`.
5. When the Acceptance axis is complete, any missing, pending, or stale non-deferred IP goes to
   `seed-realize`. Deferred IPs are excluded; a technical IP needs no invented AC.
6. Only both completed axes plus the full suite and required repository checks can complete the loop.

Use the sibling `seed-system/scripts/check-acceptance.py` as follows:

```text
--links-only             body definition-link integrity
<no completion scope>   system structure and current linkage
--complete acceptance   AC coverage and current-hash GREEN
--complete realization  every non-deferred IP current-hash verified
--complete all          aggregate Seed completion
```

A plain legacy `--complete` is equivalent to `--complete all`. Exit `0` means the selected gate
passes, `1` reports a project defect or incomplete lifecycle, and `2` means the checker could not
run. Do not infer a phase from filenames alone when the checker gives a stronger fact.

## Upstream change and replay

When a downstream leaf needs an upstream decision, restore that owner first. Human-ratify the
change, have `seed-system` review direct and semantic AC/IP impact, then replay only affected AC and
IP work. Acceptance TDD and realization may alternate; this is not a waterfall.

For a multi-turn or cross-leaf change only, keep `.scratch/seed-loop/ACTIVE_CHANGE.md`:

```md
Origin:
Owner:
Evidence:
Affected:
Decision needed:
Replay:
Last progress:
```

When `Evidence` or `Affected` names a Seed definition, use a clickable Markdown link to the exact
artifact `##` heading. Code and tests use project-relative paths. Delete no history and create no
canonical phase-state document.

## Terminals

Leaf outputs are evidence, not commands to skip recomputation. Accept
`SEED_TDD_COMPLETE`, `SEED_TDD_BLOCKED`, `SEED_REALIZE_PROGRESS`,
`SEED_REALIZE_COMPLETE`, and leaf-specific blockers, then compute the next owner again.

Return aggregate completion only as:

```text
SEED_LOOP_COMPLETE
Target: <project-relative path>
Acceptance: <count, --complete acceptance result>
Realization: <count, --complete realization result>
Verification: <full suite and repository commands with observed results>
```

Otherwise return:

```text
SEED_LOOP_BLOCKED
Owner: <seed-body|seed-system|seed-tdd|seed-realize>
Evidence: <clickable definitions and observed result>
Need: <one decision or capability>
Resume: $seed-loop <project-relative target>
```

Never declare completion from a leaf token alone, silently narrow a ratified Default, or treat AC
GREEN as proof that unrelated infrastructure or deployment choices are realized.

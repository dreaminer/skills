# body-shaping — script contract tests

Regression tests for the four runtime scripts (`check-body.sh`, `check-question.sh`,
`next-question.sh`, `progress.sh`). They exist because the **shell protocol** SKILL.md depends on must hold
even if a script's internals change.

## Run

```sh
sh tests/run.sh     # exit 0 = all pass, 1 = a failure
```

## What is fixed — and what is not

Tests pin only each script's **public contract**: small static `docs/` fixtures in →
observed **exit code / stdout / stderr** out. They do **not** pin awk expressions,
internal helper functions, or line counts — so a script can be rewritten (even in a
non-awk language) and still pass as long as its observable behaviour is unchanged.

| Script | Pinned contract |
|---|---|
| `check-body.sh` | exit `0`/`1`/`2`; on a violation, stdout names the offending `[ref]` and its required layer; the four-way directional matrix (`ED→ED`, `EU→ED`, `SD→{SD,ED}`, `SU→{SD,ED,EU,SU}`); backtick spans ignored; stray `{candidate}` fails; a missing canonical doc exits `2` and names the file on stderr. |
| `check-question.sh` | validates one selected queue entry before Review: exact `Type`/`Subject`/`Basis`, ready `Blocked by`, no candidate notation, and references resolvable in the layers allowed by `Type`. |
| `next-question.sh` | the exact sentinels `queue-empty` / `none-ready` / `Q-nnn <type>`; priority Essential→System, Domain→UseCase, then lowest `Q-`; blocked and unknown-`Type` candidates skipped. |
| `progress.sh` | the exact single line (SKILL.md relays it verbatim) and its derived arithmetic; missing files count as `0` and never error. |

## Why `EU→SD` is the named regression

DESIGN.md records the one real bug: an **Essential UseCase referencing a System Domain
term** (the abstract-depends-on-concrete inversion), and the over-correction that then
wrongly blocked the *sound* `System→Essential` direction. So:

- `check_regression_eu_sd` reproduces that exact inversion (must fail).
- `check_inversion_ed_sd` covers the sibling `Essential Domain → System` inversion.
- `check_clean` doubles as the over-correction guard: its `SD→ED` and `SU→ED` refs
  must **pass**.

## Promotion boundary

Promote is an LLM action, not a shell command, so this suite cannot execute it directly. The
`nq_unblocked_after_promote` fixture pins its deterministic queue result: after Promote clears a
confirmed dependency from `Blocked by`, the formerly blocked use case is ready for
`next-question.sh` to select.

# yolo-body-shaping — Design Rationale

> Maintainer notes for `yolo-body-shaping`. Companion to `$body-shaping` and `$auto-body-shaping`.
> This file is not loaded at runtime. Keep accepted decisions and rejected alternatives so the next
> maintainer does not reopen the same arguments without a real failure.

## North Star

Let body-shaping make progress on projects whose only domain artifact is code, without letting
auto-reasoned content silently colonize canonical documents. Maximum auto-progression with audit
traceability.

## Relationship to sibling skills

| Skill | Confirmation source | Default escalation |
|---|---|---|
| `$body-shaping` | every candidate confirmed by user | user answers each review |
| `$auto-body-shaping` | validator PASS = auto, else user | one human question per ambiguous candidate |
| `$yolo-body-shaping` | validator PASS = canonical; Decision Maker DECIDE_YES = inferred | only `TRULY_NEEDS_HUMAN` reaches the user |

A separate skill (not a mode flag on `auto-body-shaping`) is intentional: the document layout,
verdict vocabulary, and per-candidate consent model differ. Forking the skill keeps each one
readable and lets them evolve independently.

## Decisions

| Decision | Why |
|---|---|
| Decision Maker is a third role, not a Validator widening | Validator must remain a pure evidence/notation/classification check. Domain inference is a different responsibility; mixing them creates Validator overconfidence and erodes the meaning of `PASS`. |
| Code-only evidence is allowed for canonical `PASS` | The `auto-body-shaping` gate that required human-authored docs for Essential made progress impossible on code-only projects. Direct evidence — even from code — is still direct evidence. Inference is the part that needs isolation, not all code-rooted content. |
| Inferred content lives in `INFERRED_*.md`, not in canonical | Canonical documents are the project's ubiquitous language. They must remain anchored to direct evidence; mixing inference into them would let auto-on-auto spread silently and corrupt the shared vocabulary. |
| Four inferred files mirror the four canonical layers | Keeps `check-body.sh` directional rules applicable without modification. A single `INFERRED.md` or two files would force a separate validator. Four files match the existing rule surface. |
| Self-evidence determines isolation, not transitive contamination | Strict contagion (any inferred dependency contaminates the consumer) collapses to "everything is inferred" on code-only projects and defeats the skill's purpose. Self-evidence with metadata tracking lets canonical content carry its own truth while still recording the inferred shoulders it stands on. |
| `[Term]` body references from canonical to inferred are forbidden | If canonical body content can name inferred items as if they were canonical, the canonical layer silently inherits inferred semantics. Tracking dependency in metadata only (`Depends on inferred:`) keeps the reader's reading order honest. |
| 2-hop depth limit on accumulated inferred dependencies | One hop of inference is a pragmatic, reviewable judgment. Two hops of inference stacked on each other (inferred-from-inferred-from-inferred) creates a reasoning chain whose error compounds and whose individual steps are hard to audit. 2-hop is the smallest limit that allows useful chains without permitting compounded fabrication. |
| Re-evaluation queue (`REEVAL_QUEUE.md`) | When an inferred item is later confirmed or rejected by the user, its dependents' status may flip. Without a queue, those dependents silently retain stale assumptions. The queue makes the dependency change actionable on the next run. |
| `Confirmation: auto-validator` vs `auto-decision` labels | Two labels make audit and rollback grep-friendly. A single `auto` label would hide which automation tier produced a given entry and make it expensive to recover the canonical/inferred boundary after the fact. |
| `path:line` evidence is a verification snapshot | Line numbers are used so the validator can ground a claim at promotion time. They are not promised to remain live pointers after the source changes; re-evaluation uses the live file, not the snapshot. |
| Inferred items can unblock UseCase consumers only inside inferred space (or via metadata) | Otherwise an inferred Term invisibly satisfies a canonical UseCase's `Blocked by`, smuggling inferred content into the canonical layer. The check is structural and fits inside the existing blocked-by logic. |

## Rejected Alternatives

- **Add Decision Maker as a mode to `$auto-body-shaping`.** Rejected because the consent model and
  document layout diverge. A mode flag would require runtime branching in nearly every workflow
  step and obscure which skill is in effect.
- **One sidecar `BODY_PROVENANCE.md`.** Rejected for the same reason `auto-body-shaping` rejected
  it: the sidecar drifts on rename, merge, or delete and silently goes wrong.
- **Strict contagion isolation (any inferred dependency makes the consumer inferred).** Rejected
  because in a code-only project virtually every UseCase ends up inferred, eliminating canonical's
  signal value. The self-evidence rule keeps canonical meaningful while still tracking the chain.
- **No depth limit.** Rejected because inference compounds error: a 3-hop chain of inferred
  reasoning is essentially fabrication that no validator can ground. Even with audit labels the
  recovery cost is too high once the chain is live.
- **Single `INFERRED.md` (no layer split).** Rejected because `check-body.sh`'s directional rules
  rely on per-layer files; merging would require a parallel validator with extra rules.
- **Auto-promote inferred items to canonical on a fixed schedule.** Rejected: scheduled promotion
  hides the human review step the inferred isolation was designed to enable. Promotion to canonical
  must remain explicit, either by the user or by a re-evaluation that meets validator `PASS`.
- **Allow `TRULY_NEEDS_HUMAN` to mean "the run continues without this item".** Rejected because a
  partial answer would leak into subsequent dependency calculations as if the item were resolved.
  `TRULY_NEEDS_HUMAN` must block until answered or until the user explicitly stops the run.

## Boundary Cases

- **Validator PASS for an item that body-references an inferred term.** Allowed only if the
  candidate's body content does not introduce a `[Term]` reference to the inferred entry. The
  canonical item records the dependency in metadata only. If the body itself names the inferred
  term as if it were canonical, the verdict downgrades to `UNDECIDED` for the Decision Maker.
- **Decision Maker returns `DECIDE_YES` but with `Depth: 2` exceeded.** Treat as
  `TRULY_NEEDS_HUMAN`. The depth check overrides the verdict's positive sign.
- **Decision Maker returns `DECIDE_NO` for an item the validator already returned `UNDECIDED` on.**
  Append to `REJECTED.md` with both verdicts in the reason line. This preserves the trace if the
  user later disputes the rejection.
- **Re-evaluation flips an inferred item to canonical.** Re-run validator on its dependents to see
  whether their `Depends on inferred:` reference should change to nothing (now grounded
  canonically) or remain (still depends on other inferred items).

## Future Work

- Add an explicit coverage mode that repeats Recover until zero new grounded candidates appear.
- Add an inferred-ratio alarm: pause the run when the inferred layer grows beyond a configurable
  fraction of canonical, so the user can decide whether to keep extrapolating.
- Add a Validator/Decision Maker disagreement vote only if observed runs show Decision Maker
  overconfidence; until then, keep the pipeline single-pass.
- Consider a compact "audit pass" command that lists every `auto-decision` item with its evidence
  for a human reviewer to batch-approve or reject without re-running yolo end-to-end.

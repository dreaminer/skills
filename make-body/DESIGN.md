# Make Body — Design

Design rationale for maintainers. The SKILL.md holds the executable contract; this file holds the
*why*, so a future change does not re-litigate a settled decision or reintroduce a rejected one.

## North Star

Reconstruct the behavior a codebase already implements into a body with two clearly separated
languages: **System** (what the implementation calls things, observed from code) and **Essential**
(what the business means, confirmed by a human). It is reconstruction, not product design: the skill
never invents a policy, actor, permission, cardinality, lifecycle, or outcome that the code does not
support.

## Core principles (these govern future decisions)

1. **Provenance is deterministic; fidelity is judgment.** Scripts can prove an Evidence pointer
   names a real in-scope line. Whether the `Content` overshoots that line is a model judgment — so
   it lives in a coordinator step (the consistency gate), never pretending to be a script.
2. **Determinism stays in scripts; judgment stays in the coordinator.** Selection, hashing, preview,
   and structural checks are byte-stable scripts. Classification, conflict resolution, and fidelity
   are the agent's job. Neither side does the other's work.
3. **A gate must be unbypassable, not merely instructed.** Where a guarantee matters (no System
   apply without the consistency gate), the script is shaped so the unsafe action is structurally
   impossible, not just discouraged in prose.
4. **Guard real failure modes, not hypothetical ones — but a mechanical generator makes a "real"
   one.** The mechanical seeder re-emits the same scaffolds every run, so a rejected candidate's
   resurrection is guaranteed, not speculative. That is why make-body script-enforces rejection
   suppression where body-shaping (whose recovery is LLM-driven) leaves it to instruction.
5. **Rejection is terminal; review is not.** Only an explicit human rejection is archived and
   suppressed. A candidate merely awaiting review stays in the queue.

## Key decisions

- **System auto-promotes; Essential never does.** System language is code-observed and can be
  machine-checked against code; Essential meaning is a human judgment. `promote-next-system.py`
  refuses an Essential candidate with `NEEDS_HUMAN` (exit 3). If the agent judges a System
  candidate ambiguous, it does not call the auto-promotion script and sends the candidate to
  maintainer review.
- **Essential review is rendered deterministically; the judgment stays human.** Because Essential
  candidates are never auto-promoted, `review-candidate.py` adds — only for `essential-domain` /
  `essential-usecase` Types — a deterministic review frame: a fixed reviewer checklist plus the
  canonical System terms that are *lexically co-located* with the candidate (every token of a
  `SYSTEM_DOMAIN`/`SYSTEM_USECASE` subject appears in the candidate's `Content` or cited Evidence
  line). The script never generates per-candidate questions and never decides what the code cannot
  establish — that judgment follows `references/essential-review.md` and is made by a human/coordinator.
  Three guards bound the change: (1) the System render path is byte-for-byte unchanged — the frame is
  purely additive, gated on Essential Type; (2) "co-located" is lexical token co-occurrence, never a
  semantic-relevance judgment; (3) `essential-review.md` is a human-judgment protocol, not an
  auto-verdict sub-agent like the consistency gate — Essential auto-promotion stays impossible.
- **The consistency gate is a coordinator (LLM) step, not a script.** Fidelity ("does `Content`
  exceed the cited code?") cannot be decided deterministically. The gate spawns an isolated
  sub-agent — separate context, because the context that produced the candidate rationalizes its own
  over-inference. This is the trust model, not an implementation detail: the gate is the only thing
  standing between an over-inferred System claim and a canonical document.
- **The script stops before apply (`AWAIT_GATE`, exit 0).** `promote-next-system.py` prepares and
  reviews a byte-stable preview, then hands off. It never applies. Applying is a separate, deliberate
  `apply-promotion.py` call the agent makes only after the gate returns `READY`. This makes
  "System apply without the gate" structurally impossible, satisfying principle 3 — the alternative
  (keep auto-apply, instruct the agent to gate first) left the exact hole open. The handoff uses
  exit **0**, not a distinct nonzero code: structural safety comes from removing the apply step, not
  from the exit code, and exit semantics read cleanest as error (1/2) vs. proceed (0, AWAIT_GATE)
  vs. halt-for-human (3, NEEDS_HUMAN) — where a naive runner halting on the nonzero human case is
  itself the safe outcome. The agent reads the preview path from the `AWAIT_GATE` stdout line
  regardless, so a distinct code would buy little.
- **P0 gate is one-hop: `READY` → apply, anything else → `NEEDS_HUMAN`.** No rewrite-then-reapply.
  Trimming an overshoot proves the excess can be cut, not that the remainder is worth recording;
  a re-trim-then-auto-apply trusts the gate's *edit* before its *judgment* has been validated, and
  reintroduces a multi-hop loop that the one-hop rule deliberately avoids.
- **`READY` is additive.** It is "Content does not exceed Evidence," layered on top of the
  deterministic evidence/conflict/duplicate/stale/preview gates — never a replacement for them.
- **Rejection suppression is script-enforced in the extractors.** `MAKE_BODY_REJECTED.md` is keyed
  per Evidence pointer by `(Type, Subject, Evidence pointer)`. The three extractors read it through
  `rejected_index.py` and never re-seed a matching scaffold; `check-rejected.py` flags any queued
  candidate that re-cites *any one* rejected `(Type, Subject, pointer)` triple, even alongside new
  evidence. A genuinely new claim is one that shares *no* rejected pointer for that Type+Subject —
  rejection is bound to each pointer, not to the full Evidence set and not to the name. Bootstrap
  carries `MAKE_BODY_REJECTED.md` in `MANAGED_FILES`, so the archive is staged and suppression holds
  on the bootstrap path, not only on incremental extraction.
- **`MAKE_BODY_REJECTED.md` is an optional archive.** It is created by `init-docs.py`, validated by
  `check-rejected.py` if present, and counted by `report-status.py`; an absent archive is valid and
  suppresses nothing. This keeps it parallel to body-shaping's `REJECTED.md` and avoids forcing the
  file into every fixture and consumer.
- **`Reason` is free text, not an enum.** Do not enumerate rejection subtypes — that re-tables a
  judgment the skill keeps human.

## Rejected alternatives (do not reintroduce without a new, real reason)

- **Bake fidelity into a script.** Detecting over-inference against source needs a model. A
  deterministic proxy would either pass real overshoots or fail valid claims. Rejected.
- **Keep `promote-next-system.py` auto-applying and instruct the agent to gate first.** Leaves the
  unsafe action reachable (an agent can call the convenience script directly). Rejected in favor of
  the `AWAIT_GATE` stop-before-apply handoff.
- **Add a `Basis: observed/proposed` field like body-shaping.** make-body already routes by Type
  (System = code-observed → gate then auto; Essential = human-confirmed → always human), so the
  field is redundant here. Rejected; the routing principle is kept, the field is not.
- **Generate the Essential reviewer's questions inside the review script.** That moves judgment into
  deterministic code — the same error the consistency gate avoids. Rejected: the script renders a
  fixed frame plus lexical co-location; the coordinator authors the questions and the uncertainty
  call, following `references/essential-review.md`.
- **Surface "related" System terms on an Essential candidate by semantic relevance.** Choosing which
  System term *relates* to a candidate is inference. Rejected in favor of lexical token co-occurrence,
  which is deterministic and explainable, even at the cost of occasionally listing an unrelated
  same-word term (a human filters it; the script never claims a relationship).
- **Rewrite-then-reapply in P0.** Deferred to P1 (below), not adopted now.
- **Send `NEEDS_HUMAN`/deferred candidates to `MAKE_BODY_REJECTED.md`.** Conflating "awaiting review"
  with "rejected" makes the archive over-suppress legitimate candidates. Rejected: only explicit
  human rejection is archived.
- **Flag a resurrection only when the *full* Evidence-pointer set matches.** Too weak: re-queuing a
  rejected scaffold with one throwaway pointer appended changes the set and bypasses suppression.
  Rejected; any shared `(Type, Subject, pointer)` triple is a resurrection. The over-block this
  trades against is bounded — resurrection is a surfaced check failure a human resolves, never a
  silent delete — so re-queue prevention wins.

## Failure modes to avoid

- **Silent canonical corruption.** An over-inferred System claim that auto-promotes looks
  authoritative and is hard to detect later. This is the failure the consistency gate exists to
  prevent; never weaken it to "speed up" auto-promotion.
- **Over-suppression.** A rejection keyed too loosely (e.g. by Subject alone) would suppress valid
  new candidates that share a name. Keep the key bound to Evidence.
- **Trusting the gate's edit before its judgment.** See the one-hop decision; do not open the
  rewrite path before the P1 conditions are met.

## Deferred to P1 — rewrite-then-reapply

Opening an auto path where a gate `REWORK` is mechanically applied and re-checked (rather than
escalated) requires all of:

- enough real `REWORK` examples reviewed to trust the gate's edits;
- evidence that `SAFE_CONTENT` / `REMOVE_EXACTLY` edits preserve useful meaning (not just trim to a
  bounded-but-empty claim);
- a designed oscillation bound (a candidate cannot loop edit→re-check indefinitely); and
- tests covering degraded-content and over-trimming cases.

Richer Essential review rendering is **no longer deferred** — shipped as the deterministic Essential
review frame in `review-candidate.py` plus the human-judgment protocol `references/essential-review.md`
(see Key decisions). The first-run worked trace also shipped, as `references/first-run.md`, linked from
`SKILL.md`.

## Deferred — framework observation recipes (conditional)

`references/framework-observation-recipes.md` (NestJS / FastAPI / Django+Celery, "where a human looks
for Evidence") is **not** added now. Guarding a flow no real project has hit is the hypothetical-guard
trap this skill avoids. Add it only after a real project surfaces a flow whose Evidence the lexical
adapters cannot point at, and then scope it strictly to what those adapters miss — dependency
injection, dynamic wiring, runtime registration — never restating facts an adapter already collects
(e.g. FastAPI route / Celery task decorators, which `collect-python-facts.py` already indexes). It
must keep the lexical/non-semantic boundary: observation → Evidence; inference → conflict.

Also rejected outright (identity-breaking, not deferred): a general semantic analyzer (TypeScript
compiler call graph, Python import/DI resolver) and a greenfield product-planning/policy-generation
mode. The first contradicts the lexical fact principle and weakens the consistency gate's trust model
by manufacturing false confidence; the second contradicts the North Star — make-body reconstructs, it
does not design.

## How to use this when expanding the skill

Before adding a rule or a script, ask: (1) Is this deterministic provenance (script) or judgment
(coordinator)? (2) Does it make a needed guarantee *structural*, or only *instructed*? (3) Is the
failure it guards against real in this skill, or hypothetical? If hypothetical, do not add the guard.

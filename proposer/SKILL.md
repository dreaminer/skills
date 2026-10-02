---
name: proposer
description: "Builds one final exact-match edit proposal for a target skill as chief architect over strategy-lens-differentiated clean-context sub-proposals (minimal edit / structural / additive; 1-3, default 3), rejecting directions already FAILED in the modification history. Use when an improvement loop (criteria-opt Stage 4) needs edit instructions for dimensions scoring below 100, or when the user asks to turn a frozen score report into a patch proposal. It only produces the final modification proposal: no rubric work (the `rubricator` skill), no running (Runner), no scoring (the `scorer` skill), no gating (Judger), no edit application (Rebuilder)."
---

# Proposer

## Purpose

Turn one frozen score report into exactly one final modification proposal that the Rebuilder can
apply with zero discretion. The Proposer is the only stage that designs changes, and it never
applies them: its output is a list of exact-match edits — unique-match old/new text pairs —
specific enough that Stage 5 needs no judgment, plus the per-edit fingerprint fields the loop uses
to prevent oscillation.

## Required Inputs

- `OBJECTIVE_ANALYSIS`: the slice of `FINAL_RUBRIC` above the `### 평가 항목 정의` heading. The
  dimension table is not re-sent; dimension requirements arrive via the 고득점 요건 column of
  `FINAL_EVAL_RESULT`.
- `CURRENT_SKILL_SOURCE`: the current version of the target skill source (prompt text or code).
- `FINAL_EVAL_RESULT`: the frozen 5-column deduction table from the `scorer` skill.
- `MODIFICATION_HISTORY`: the orchestrator-maintained record of prior loops' proposals with
  per-edit outcomes.
- `CURRENT_LOOP`: the loop number, echoed into the proposal header.
- Optional `sub_agents` count (1-3, default 3): how many clean-context sub-proposers to run. Lens
  assignment per count is defined in
  [references/proposer-prompts.md](references/proposer-prompts.md).
- Optional user constraints: output-path override, `session_id`, or a request to skip the default
  save.

If the score report or the source is missing, ask first. Do not run the target or score a run to
fill the gap — those are Runner's and the `scorer` skill's jobs.

## Process

1. **Select targets.** Only dimensions scoring below 100 in `FINAL_EVAL_RESULT` are targets; the
   calling loop gates on the Judger's `CONTINUE_TO_STAGE_4` before invoking this skill.
2. **Get strategy-differentiated sub-proposals.** Use clean contexts when available —
   `sub_agents` (1-3, default 3) sub-agents, none seeing another's output, each running the same
   4-A prompt with its assigned `{{STRATEGY_FOCUS}}` lens. At 3, one lens each: 최소 수정
   (smallest surgical replacement), 구조 개편 (restructure so the failure class cannot recur),
   보강 추가 (fill the gap with new content, including `(신규 파일)` edits); at 2 and 1, the
   merged assignments in the prompts reference keep all three strategies in play. Every
   sub-proposer receives the full inputs and targets every dimension below 100 — the lens sets
   fix-strategy priority, it does not slice the input. Each returns `proposals` JSON per
   [references/proposer-prompts.md](references/proposer-prompts.md).
3. **Synthesize as chief architect.** Run the 4-B prompt: check for side effects between proposals
   (fixing A must not break B), keep the target skill's architectural coherence, pick one direction
   per deduction when lens alternatives compete (resolution certainty versus side-effect risk), and
   reject any edit whose fingerprint — normalized Target 위치, 감점 유형, 수정 전략 — matches an
   `outcome: FAILED` edit in `MODIFICATION_HISTORY`. All three fields must match; do not extend
   rejection to semantic similarity, and `PENDING`/`SUCCESS` entries are not grounds for rejection.
   Side-effect checking spans the whole frozen rubric, not only this loop's proposals: an edit
   likely to degrade a dimension currently at 100 is reworked or dropped, and an accepted
   trade-off is stated in its 수정 이유. For each `NEW_DROP` in `MODIFICATION_HISTORY`, run the
   evidence-vs-diff check: if the drop's 검증된 근거 cites text or procedure a prior loop's edit
   introduced, treat it as a regression and prefer correcting or reverting that original edit
   over stacking a compensating new one; with no textual link, treat it as an ordinary defect
   and assign no blame. Apply the 4-B boundary/safety veto: reject or rework edits that broaden
   the target's trigger or scope, weaken guards or human gates, introduce unguarded destructive
   or outward actions, create sibling-trigger overlap, or add style-only content no deduction
   implicates — unless the deduction's own quoted evidence names that exact boundary as the
   defect.
4. **Emit the final proposal.** The [최종 스킬 수정 제안서] markdown per the 4-B output format and
   nothing else.
5. **Save the proposal by default.** Default path is
   `<target-skill>/docs/criteria-opt/<session>/loop-<CURRENT_LOOP>/4-proposal.md`, where
   `<target-skill>` is derived from `CURRENT_SKILL_SOURCE`'s path and `<session>` is the latest
   same-day `<YYYYMMDD>-<letter>` under `<target-skill>/docs/criteria-opt/` or `<YYYYMMDD>-a` if
   none exists. Under criteria-opt the loop passes this path explicitly. A user-supplied
   `output_path` or `session_id` overrides the corresponding auto value. Skip the save only
   when the user requests no-save or the target skill directory is unavailable; in that case
   print the path that would have been used and return the proposal in-chat.

## Outputs

- [최종 스킬 수정 제안서]: loop number, 수정 목표, and a numbered edit list. Each edit carries
  `[target_dimension]`, `[감점 유형]`, `[수정 전략]`,
  `[Target 위치]`, `[기존 내용]`, `[수정할 내용]`, and `[수정 이유]`.
  Fingerprint matching follows Process step 3; `target_dimension` identifies the score to track.

Edit contract — what makes the proposal mechanically applicable:

- `[기존 내용]` is a verbatim quote appearing exactly once in the current source; widen the quote
  until it is unique.
- `[수정할 내용]` is the complete replacement text for the whole quote.
- A new file is expressed as `[기존 내용]: (신규 파일)` with the full file content in
  `[수정할 내용]`; the Rebuilder fails the edit if the path already exists.
- No two edits may overlap in the text they touch; the Rebuilder validates every edit first, then
  replaces in listed order.

Downstream contract:

- The Rebuilder (criteria-opt Stage 5) applies the proposal validate-then-apply, all-or-nothing,
  with zero discretion — an edit that fails unique match fails the whole rebuild, so quote
  precision is a correctness obligation of this skill.
- The proposal doubles as the loop's modification-history entry.

## Modification History Schema

`MODIFICATION_HISTORY` is a system artifact the orchestrator maintains — not an LLM prompt and not
this skill's output. This skill only reads it for fingerprint rejection; the schema lives here
because each entry is one of this skill's proposals plus outcomes:

- Append: after a successful Stage 5 rebuild, the loop's whole proposal (every edit with its
  fingerprint fields) is added as `outcome: PENDING`.
- Outcome: right after the next loop's `FINAL_EVAL_RESULT` freezes, each `PENDING` edit's
  `[target_dimension]` score is compared before/after — higher → `outcome: SUCCESS (이전 점수 →
  새 점수)`; equal or lower → `outcome: FAILED (이전 점수 → 새 점수)`.
- `NEW_DROP`: at the same freeze the orchestrator also compares every frozen dimension, not only
  targeted ones; a non-targeted dimension that drops below 100 is recorded as a factual `NEW_DROP`
  line (dimension, 이전 점수 → 새 점수) in that loop's entry. It carries no causal attribution
  and is not an edit outcome — whether it is a regression is decided by this skill's
  evidence-vs-diff check in the next loop.
- A loop ending in `INVALID_SCORE_REPORT` or `REBUILD_FAILED` marks its proposal
  `outcome: FAILED (사유 표기)` without score comparison.

## Rules

- Target only dimensions below 100; do not touch content that no deduction implicates.
- Preserve the target skill's essential purpose; edits snipe the deduction causes, not style.
- A lens is a strategy priority, not a quota: a sub-proposer whose lens fits a deduction poorly
  proposes the natural fix for it instead, and no lens has a per-loop minimum.
- Lens diversity exists to keep distinct [수정 전략] directions available after a `FAILED`
  fingerprint; synthesis picks per deduction, it does not collapse everything into one strategy
  unexamined.
- Every 수정 이유 must state why the edit resolves the quoted deduction — logical causation, not
  preference.
- Protect passing dimensions: do not accept an edit whose predictable side effect degrades a
  dimension currently at 100 without stating that trade-off in its 수정 이유.
- Boundary and safety are veto criteria in synthesis: an edit that broadens the target's trigger,
  scope, or responsibility, weakens an existing guard, preview, dry-run, rollback, or
  human-confirmation step, introduces an unguarded destructive or outward action (delete, push,
  deploy, install, network write), or shifts the description into overlap with a sibling skill's
  trigger is rejected even when it would resolve the deduction — unless the deduction's quoted
  evidence names that exact boundary as the defect.
- `NEW_DROP` attribution is evidence-based only: an edit is blamed for a drop only when the
  drop's quoted evidence traces to text that edit introduced — temporal order alone is not
  causation.
- Do not apply edits, run the target, score runs, gate the loop, or modify the rubric or the score
  report.
- Fingerprint rejection is exact three-field matching against `FAILED` entries only.
- Do not save outside the default artifact-layout path unless the user supplied an explicit
  override.

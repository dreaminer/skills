---
name: criteria-opt
description: Runs a rubric-first skill improvement loop — frozen rubric, run, deduction scoring, deterministic gate, targeted proposal, mechanical rebuild. Use when the user asks to optimize, improve, harden, or run an improvement or evaluation loop over an agent skill, rather than merely review one proposed edit or run a one-shot audit.
---

# Criteria Opt

## Purpose

Create a rubric, run current behavior, score by deductions, gate the loop, propose targeted edits,
then mechanically rebuild only from the approved proposal.

## Inputs

- Target skill objective and requirements.
- Optional target `SKILL.md` and behavior-affecting references.
- Current skill source.
- Current loop count, `max_loop`, and cumulative modification history.
- Optional user constraints for scoring language, output path, or required dimensions.
- Optional `sub_agents` count (1-3, default 3): how many clean-context sub-agents each
  lens-differentiated stage (0, 2, 4) runs; lens assignments per count are defined in each skill's
  prompts reference, and the chief-synthesis step always runs regardless of count.

Before Stage 0, batch every run-shaping choice the invocation leaves undetermined into one ask:
objective, `max_loop`, the Stage 1 run input/environment (for an interactive target, the scripted
answers or the stop-at-gate point), and `sub_agents`. Ask once, at framing only, skipping items the
inputs already determine; if the objective is inferable from `SKILL.md`, state the inference
instead of asking. Never ask mid-loop — a gap found after Stage 0 is filled with the recorded
default, not a new question. Non-interactive defaults: objective inferred from `SKILL.md` (stop if
not inferable), `max_loop: 3`, `sub_agents: 3`; record any default applied unasked.

## Stages

### 0: Rubricator

Delegate to the standalone `rubricator` skill.

- In: target skill objective and requirements; optional target `SKILL.md` and behavior-affecting
  references; optional user constraints (rubric language, output path, required dimensions);
  optional `sub_agents` count.
- Out: `FINAL_RUBRIC` — one frozen document with `OBJECTIVE_ANALYSIS` embedded above its
  `### 평가 항목 정의` heading. Frozen for the whole session; only logged typo or formatting fixes
  afterward. Saved as `0-rubric.md` per the artifact layout below.

### 1: Runner

This is a system process, not an LLM prompt. Run the current skill version in the requested
environment or safe sandbox, capture behavior-relevant artifacts and exit status, encapsulate them as
`RUNNER_OUTPUT`, and pass it unchanged to Stage 2.

`RUNNER_OUTPUT` must include `target_skill`, `run_input`, `artifacts`, `exit_status`, `errors`, and
`notes`; keep it raw, with no scoring, failure-hiding summary, fixes, or filtering.

Run safety: prefer a throwaway sandbox copy of the run input; never mutate the target skill source
or the original fixtures, and never take unguarded destructive or outward actions (delete outside
the sandbox, push, deploy, install, network write). Create the sandbox under
`.criteria-opt-runs/<target-skill>-<session>/sandbox/run-<N>/` at the orchestrating repository
root — disposable scratch, never committed and never saved as a stage artifact; quote any evidence
the capsule needs inside `RUNNER_OUTPUT` itself rather than relying on the sandbox surviving. Drive an interactive target only from the
scripted answers or stop-at-gate point fixed at framing; the Runner never improvises an answer and
never prompts a live human — an unanswered question stops the run, recorded raw in `notes`.

### 2: Scorer

Delegate to the standalone `scorer` skill.

- In: `FINAL_RUBRIC` (the whole document), `RUNNER_OUTPUT` (the raw capsule, unmutated), and the
  optional `sub_agents` count.
- Out: `FINAL_EVAL_RESULT` — the 5-column deduction table
  `| 평가 항목명 | 최종 평점 | 감점 이유 | 검증된 근거 (Evidence) | 고득점 요건 |`, every frozen
  dimension exactly once, numeric 0-100, no total row, no objective-analysis head. The Scorer
  records defects only; it never praises, proposes patches, or changes the rubric.

### 3: Judger

This is a system decision tree, not an LLM prompt. Read `FINAL_EVAL_RESULT`, the frozen
dimension-name list from `FINAL_RUBRIC`, and the loop counters:

1. If any frozen dimension is missing or duplicated — judged by verbatim name comparison against
   that list — or any score is non-numeric or outside `0-100`, return `INVALID_SCORE_REPORT` and
   stop.
2. Else if every evaluation item is `>= 90`, return `SUCCESS` and stop.
3. Else if `current_loop >= max_loop`, return `MAX_LOOP_EXCEEDED` and stop.
4. Else return `CONTINUE_TO_STAGE_4`.

### 4: Proposer

Delegate to the standalone `proposer` skill. Run only after `CONTINUE_TO_STAGE_4`.

- In: `OBJECTIVE_ANALYSIS` (the slice of `FINAL_RUBRIC` above `### 평가 항목 정의`), the current
  skill source, `FINAL_EVAL_RESULT`, `MODIFICATION_HISTORY`, `current_loop`, and the optional
  `sub_agents` count.
- Out: the [최종 스킬 수정 제안서] — exact-match edit instructions (unique-match old/new text
  pairs; `(신규 파일)` for new files) targeting only dimensions below 90, each edit carrying its
  fingerprint fields; edits whose fingerprint matches a `FAILED` history entry are rejected, and
  boundary/safety-violating edits (trigger or scope broadening, guard weakening, unguarded
  destructive actions, sibling-trigger overlap) are vetoed in synthesis. It does not apply edits.

### 5: Rebuilder

This is a system process, not an LLM prompt. Use `references/rebuilder-stage.md`. First validate
every edit against the current source (each old text matches exactly once; `(신규 파일)` edits
require the target path to be absent), then mechanically apply the proposal: unique-match
replacement per edit, file creation for new-file edits. All-or-nothing — any validation failure
returns `REBUILD_FAILED` with no files changed. No LLM regenerates the skill source.

## Outputs

- `FINAL_RUBRIC`: the frozen Markdown rubric with `OBJECTIVE_ANALYSIS` embedded, from the
  `rubricator` skill.
- `RUNNER_OUTPUT`: target skill, run input, artifacts, exit status, errors, and mechanical run notes.
- `FINAL_EVAL_RESULT`: the 5-column Markdown table defined by the `scorer` skill.
- Judger decision: `SUCCESS | INVALID_SCORE_REPORT | MAX_LOOP_EXCEEDED | CONTINUE_TO_STAGE_4`.
- Final modification proposal: the exact-match edit list defined by the `proposer` skill; it
  doubles as the modification-history entry for the loop.
- Rebuilder result per `references/rebuilder-stage.md`: modified source files plus a per-edit
  apply log, or `REBUILD_FAILED` with no files changed.

## Artifact Layout

Stage artifacts are saved in the target skill's directory under `docs/criteria-opt/<session>/`,
where `<session>` is `<YYYYMMDD>-<letter>` (e.g. `20260704-a`). Filenames start with the producing
stage number, so any artifact is identified by session, loop, and stage alone:

```
<target-skill>/docs/criteria-opt/<session>/
  0-rubric.md              # FINAL_RUBRIC — frozen once per session, loop-independent
  history.md               # MODIFICATION_HISTORY — cumulative, loop-independent, no stage number
  loop-<N>/
    1-runner-output.md     # RUNNER_OUTPUT capsule
    2-eval-result.md       # FINAL_EVAL_RESULT
    3-judgment.md          # Judger decision plus the counters it read
    4-proposal.md          # [최종 스킬 수정 제안서] — only after CONTINUE_TO_STAGE_4
    5-rebuild-log.md       # per-edit apply log, or the REBUILD_FAILED record
```

- Loop-independent artifacts sit at the session root; a terminal loop directory simply lacks the
  `4-`/`5-` files.
- The orchestrator passes these paths to the `rubricator`, `scorer`, and `proposer` skills as
  their explicit `output_path`. Those skills also default to this same layout when run
  standalone — an out-of-loop invocation against the same target lands in the same session
  directory. See each skill's SKILL.md for the exact default-path derivation and no-save
  fallback.
- `docs/` is not part of `CURRENT_SKILL_SOURCE`: the Runner does not treat it as
  behavior-affecting reference material, the Scorer does not read prior artifacts as evidence, and
  the Proposer must not target files under `docs/`.

## Validation

Trigger boundary and one real end-to-end run trace live in `references/validation-evidence.md`.
Open it when auditing whether this skill fires on the right requests — a one-shot read-only audit
or a single proposed-edit review is not this loop's job — or when you need evidence that the loop
measurably moves a target skill's dimension scores.

## Rules

- Do not patch, rewrite, or optimize the target skill during these stages.
- Do not let later candidate outputs influence the rubric.
- Do not include generic quality preferences unless they directly support the target objective.
- Every criterion must be observable, measurable, and tied to a rationale.
- Prefer the smallest rubric that can control the later improvement loop.
- Treat automation as optional evidence gathering, not as success by itself.
- Runner is a system process; do not recast it as a judging or patch-proposal prompt.
- Do not mutate `RUNNER_OUTPUT` before passing it to the next stage.
- Scorer is deduction-only: no praise, no bonus points, and every deduction needs quoted evidence.
- Judger is deterministic; do not reinterpret scores, thresholds, or loop counters.
- Proposer must not apply edits or repeat a failed modification-history direction.
- The orchestrator maintains the modification history: append each accepted proposal as `PENDING`
  after a successful rebuild, then mark per-edit `SUCCESS`/`FAILED` by score delta once the next
  loop's `FINAL_EVAL_RESULT` is frozen (schema in the `proposer` skill). At the same freeze,
  compare every frozen dimension against the previous loop, not only targeted ones: a dimension
  no edit targeted that drops below 90 is recorded in that loop's history entry as a factual
  `NEW_DROP` line (dimension, 이전 점수 → 새 점수) — a label, not a verdict. The orchestrator
  must not attribute the drop to any edit; causal attribution is the Proposer's evidence-vs-diff
  check, and scores are never adjusted because of a `NEW_DROP`.
- At a terminal decision (`SUCCESS` or `MAX_LOOP_EXCEEDED`), the orchestrator records in the
  terminal entry of `history.md` the per-dimension delta from the session's first
  `FINAL_EVAL_RESULT` to the last, flagging every dimension that ends below its starting score.
  Applied `FAILED` edits stay in the source, so a flagged regression is surfaced for the user's
  revert decision (e.g. via git); the loop itself never reverts at terminal.
- Rebuilder is mechanical; no interpretation beyond the final proposal is allowed.

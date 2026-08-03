---
name: scorer
description: Scores a target skill's run capsule (RUNNER_OUTPUT) against a frozen rubric by deduction-only audit — lens-differentiated clean-context sub-scorers (1-3, default 3) cross-validated by a chief auditor. Use when an improvement loop (criteria-opt Stage 2) needs a score report for a run, or when the user asks to score or audit a skill run against a frozen rubric. It only produces the final score report: no rubric creation or edits (Rubricator), no running (Runner), no gating (Judger), no patch proposals (Proposer).
---

# Scorer

## Purpose

Turn one run capsule and one frozen rubric into exactly one defect-evidenced score report that the
Judger can gate on. Scoring is deduction-only: every dimension starts at 100, only defects are
recorded, and every deduction is proven by quoting the run capsule.

The Scorer audits what the run **did**, not what the target skill document promises. Its recall
risk is asymmetric: over-deduction is filtered by cross-validation, but a defect all scorers miss
inflates the score and lets the Judger's `>= 90` gate pass defective behavior. The three detection
lenses exist to break that correlated miss.

## Required Inputs

- `FINAL_RUBRIC`: the frozen rubric document from Rubricator, received whole — the
  `OBJECTIVE_ANALYSIS` head above the `### 평가 항목 정의` heading plus the dimension table
  `| 평가 항목명 | 고득점 요건 (100점 기준) | 기반 근거 |`. The head is context for reading the
  requirements; deductions map only to frozen dimensions and their 고득점 요건.
- `RUNNER_OUTPUT`: the raw run capsule from Runner with `target_skill`, `run_input`, `artifacts`,
  `exit_status`, `errors`, and `notes` — unmutated, unfiltered, unsummarized.
- Optional user constraints: scoring language, output-path override, `session_id` /
  `loop_number`, or a request to skip the default save.
- Optional `sub_agents` count (1-3, default 3): how many clean-context sub-scorers to run. Lens
  assignment per count is defined in
  [references/scorer-prompts.md](references/scorer-prompts.md).

If either required input is missing, ask first. Do not draft a rubric or run the target to fill
the gap — those are Rubricator's and Runner's jobs. To score a static artifact that was never run,
the caller must wrap it as a `RUNNER_OUTPUT` capsule (artifact under `artifacts`, `notes` stating
it is static); the evidence-quoting rules then apply unchanged.

## Process

1. **Validate the inputs.** Extract the frozen dimension list from `FINAL_RUBRIC`; confirm the
   capsule carries all six fields. A broken capsule goes back to the caller, not into scoring.
2. **Run lens-differentiated sub-scorers.** Use clean contexts when available — `sub_agents`
   (1-3, default 3) sub-agents, none seeing another's result, each running the same 2-A prompt
   with its assigned `{{DEFECT_FOCUS}}` lens. At 3, one lens each: omission (요구된 증거의 부재),
   distortion (수행됐지만 잘못됨), violation/excess (금지·범위 초과); at 2 and 1, the merged
   assignments in the prompts reference cover all three axes. Every sub-scorer receives the full
   rubric and the full capsule, and scores **every** frozen dimension — the lens sets
   defect-hunting priority, it does not slice the rubric or the input. Each returns deduction
   JSON per [references/scorer-prompts.md](references/scorer-prompts.md).
3. **Cross-validate as chief auditor.** Merge the sub-scorer reports with the 2-B prompt:
   union-then-filter. A deduction survives on the coherence of its quoted evidence, never on how
   many scorers found it — a Critical found by one lens is kept if its evidence holds; a deduction
   echoed by every sub-scorer is removed if its evidence does not. Merge duplicate reports of the same
   defect into one deduction without double-counting penalty points. Remove lens-induced
   over-deductions (defects the 고득점 요건 never required).
4. **Emit `FINAL_EVAL_RESULT`.** The 5-column Markdown table per the 2-B output format and nothing
   else: every frozen dimension exactly once, numeric `0-100` scores, no total row, no
   objective-analysis head.
5. **Save the FINAL_EVAL_RESULT by default.** Default path is
   `<target-skill>/docs/criteria-opt/<session>/loop-<N>/2-eval-result.md`. Under criteria-opt the
   loop passes this path explicitly; standalone runs derive `<target-skill>` from the run
   capsule's `target_skill` (or the frozen rubric's `대상 스킬` line), pick the latest same-day
   `<session>` (`<YYYYMMDD>-<letter>`) under that directory or create `<YYYYMMDD>-a` if none
   exists, and choose `<N>` = next unused `loop-<N>/` starting at 1. A user-supplied
   `output_path`, `session_id`, or `loop_number` overrides the corresponding auto value. Skip
   the save only when the user requests no-save or the target skill directory is unavailable;
   in that case print the path that would have been used and return the report in-chat.

## Outputs

- `FINAL_EVAL_RESULT` (`최종 평가 결과서`): the Markdown table
  `| 평가 항목명 | 최종 평점 | 감점 이유 | 검증된 근거 (Evidence) | 고득점 요건 |` and nothing
  else — it never carries the rubric's `OBJECTIVE_ANALYSIS` head or its 기반 근거 column.

Downstream contract: the Judger validates that every frozen dimension appears exactly once with a
numeric `0-100` score — a malformed report is `INVALID_SCORE_REPORT`, so report shape is itself a
correctness obligation. `>= 90` on every dimension means SUCCESS, so 90+ may only appear when the
run is deployment-ready with no minor defect. The Proposer targets dimensions below 90 using the
감점 이유 and 검증된 근거 columns — write them specific enough to aim an edit at — and the 고득점
요건 column is the only path by which dimension requirements reach it, so reproduce 평가 항목명 and
고득점 요건 verbatim from the frozen rubric.

## Rules

- Deduction-only: no praise, no bonus points, no strengths commentary. Full compliance is a
  wordless 100.
- Every deduction quotes concrete content from `RUNNER_OUTPUT`. An omission deduction proves the
  absence by quoting the place in the capsule where the evidence should have appeared.
- Score the run capsule, not the target skill source; a promise in the skill document is not
  evidence of behavior.
- Do not mutate, summarize, or filter `RUNNER_OUTPUT`; do not re-run the target or patch anything.
- Every sub-scorer scores every frozen dimension. A lens is a search priority, not a quota: a
  sub-scorer finding no defects on its lens reports full marks rather than inventing deductions.
- Deduction acceptance is evidence coherence, not headcount. Never resolve sub-scorer disagreement
  by majority vote.
- Do not add, remove, reinterpret, or reweight rubric dimensions; the rubric is frozen.
- Do not gate the loop, declare SUCCESS, count loops, or propose patches — Judger and Proposer own
  those.
- Do not save outside the default artifact-layout path unless the user supplied an explicit
  override.

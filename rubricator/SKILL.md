---
name: rubricator
description: "Frames a target skill's objective and freezes a deduction-scoring rubric, synthesized as chief architect from lens-differentiated clean-context drafts (1-3, default 3). Use when an improvement loop (criteria-opt Stage 0) needs evaluation criteria fixed before any run, scoring, or patching, or when the user asks to draft, design, or freeze a rubric for a skill. It only produces the objective analysis and the frozen rubric: no running (Runner), no scoring (the `scorer` skill), no gating (Judger), no patch proposals (Proposer)."
---

# Rubricator

## Purpose

Fix the evaluation criteria before any improvement work exists. The rubric must precede the loop:
later stages score against it, gate on it, and must not treat out-of-rubric changes as progress.

Two artifacts come out of this skill and nothing else:

- `OBJECTIVE_ANALYSIS`: what the target skill must achieve, which failure modes matter, and what
  stays out of scope.
- `FINAL_RUBRIC`: exactly one frozen deduction-scoring rubric derived from that objective.

## Required Inputs

- Target skill objective and requirements.
- Optional target `SKILL.md` and behavior-affecting references.
- Optional user constraints: rubric language, output-path override, required dimensions, or a
  request to skip the default save.
- Optional `sub_agents` count (1-3, default 3): how many clean-context drafters to run. Lens
  assignment per count is defined in
  [references/rubricator-prompts.md](references/rubricator-prompts.md).

If the objective is missing, ask first. If it is inferable from the target `SKILL.md`, state the
inferred objective and continue.

## Process

1. **Frame the objective.** Write `OBJECTIVE_ANALYSIS` as a concise purpose statement for the
   target skill: what it must achieve, what failure modes matter, and what must stay out of scope.
2. **Get lens-differentiated rubric drafts.** Use clean contexts when available — `sub_agents`
   (1-3, default 3) sub-agents, none seeing another's draft, each running the same 0-A prompt
   with its assigned `{{DRAFT_FOCUS}}` lens. At 3, one lens each: achievement (catches
   omissions), failure-mode (catches distortions), boundary (catches excess and violations); at
   2 and 1, the merged assignments in the prompts reference cover all three axes. Every
   sub-agent receives the full `OBJECTIVE_ANALYSIS` — the lens sets mining priority, it does not
   slice the input. Each returns `suggested_rubric` JSON per
   [references/rubricator-prompts.md](references/rubricator-prompts.md).
3. **Synthesize as chief architect.** Compare the drafts by rationale, not by wording (0-B
   prompt). Merge duplicates — treating cross-lens convergence as strong evidence a criterion is
   load-bearing — remove criteria that do not directly follow from the target objective, and
   rewrite vague criteria into measurable ones.
4. **Freeze the final rubric.** Produce exactly one `FINAL_RUBRIC`. After this point the rubric
   must not change inside the same improvement session except for logged typo or formatting fixes.
5. **Save the FINAL_RUBRIC by default.** Default path is
   `<target-skill>/docs/criteria-opt/<session>/0-rubric.md`, where `<session>` is
   `<YYYYMMDD>-<letter>` (letter starts at `a` and increments if the same-day session already
   exists under that directory). Under criteria-opt the loop passes this path explicitly;
   standalone runs compute it from the resolved target skill directory. A user-supplied
   `output_path` overrides the default. Skip the save only when the user requests no-save or the
   target skill directory is unavailable (e.g., only free-form requirements were given) — in
   that case, print the path that would have been used and return the rubric in-chat. Never
   save into the target's `references/`: that directory is behavior-affecting skill source, and
   a rubric stored there contaminates later runs.

## Outputs

- `FINAL_RUBRIC`: one Markdown document per the 0-B output format — `OBJECTIVE_ANALYSIS` embedded
  verbatim above the fixed `### 평가 항목 정의` heading, followed by the dimension table
  `| 평가 항목명 | 고득점 요건 (100점 기준) | 기반 근거 |`.
- `OBJECTIVE_ANALYSIS` is not a separate file: it is the slice of `FINAL_RUBRIC` above the
  `### 평가 항목 정의` heading. The two freeze together and must never version apart.

Downstream contract — who consumes which slice:

- The `scorer` skill receives the whole document, starts each dimension at 100, and deducts
  against the 고득점 요건 column; its report (`FINAL_EVAL_RESULT`) carries that column onward, so
  the dimension table is never re-sent downstream.
- The Judger reads only the dimension-name list, checking every frozen dimension appears exactly
  once with a numeric 0-100 score.
- The Proposer receives only the `OBJECTIVE_ANALYSIS` slice; dimension requirements reach it via
  the 고득점 요건 column of `FINAL_EVAL_RESULT`, keeping a single conveyance path.
- A dimension name is an identity — downstream stages match on it verbatim.

## Rules

- Every criterion must be observable, measurable, and tied to a rationale that traces back to the
  target objective.
- Prefer the smallest rubric that can control the later improvement loop.
- Remove criteria that do not directly follow from the target objective; do not add generic
  quality boilerplate the objective never asked for.
- A lens is a mining priority, not a quota: a drafter may return few or no criteria for its
  lens, and the final rubric has no per-lens minimum.
- Write each 고득점 요건 as an observable requirement. A score of 100 means no verified violation
  in the supplied run, not a guarantee of defect-free behavior on other inputs.
- Do not run the target, score outputs, propose patches, or edit the target skill.
- Do not rank, average, or pre-weight dimensions; the rubric defines criteria, not verdicts.
- Do not change the rubric after freeze except logged typo or formatting fixes.
- Do not save outside the default artifact-layout path unless the user supplied an explicit
  override; the target's `references/` is off-limits regardless.

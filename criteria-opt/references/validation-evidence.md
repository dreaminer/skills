# Validation Evidence

Lightweight behavior evidence for `criteria-opt` itself: a trigger boundary versus its sibling
skills, and one real end-to-end run trace. This is not an extra checklist for every skill the loop
optimizes — it exists so an auditor can check that `criteria-opt` fires at the right time and that
the loop demonstrably changes a target skill's scores.

## Trigger Smoke Set

Expected to invoke `criteria-opt`:

| Prompt | Expected reason |
| --- | --- |
| "이 스킬을 rubric 만들어서 채점하고 개선 루프 돌려줘." | Iterative rubric → run → score → gate loop over a skill. |
| "make-body를 max_loop 3으로 최적화 루프 태워줘." | Multi-loop optimization with an explicit loop budget. |
| "Harden this skill by running the improvement loop until every dimension passes." | Loop-until-gate over a skill, not a single edit. |

Expected not to invoke `criteria-opt`:

| Prompt | Expected reason |
| --- | --- |
| "이 스킬 한번 감사해줘 / 트리거·구조 점검해줘." | One-shot read-only audit — no run/score loop; not this skill's job. |
| "이 제안(한 edit)만 검토해서 수락할지 봐줘." | Single proposed-edit review, not an improvement loop. |
| "온보딩 워크플로우 개선해줘." | Generic workflow improvement, no agent-skill object. |
| "이 코드 리뷰해줘." | Code review, not a skill improvement loop. |

The description's contrast clauses ("rather than merely review one proposed edit or run a one-shot
audit") narrow `criteria-opt`'s own over-firing on those intents: one-shot audits and single-edit
reviews are user-invoked flows that never auto-fire, so the clauses guard against this skill
absorbing their requests rather than resolving a model-routing contest.

## End-to-End Run Trace

Historical evidence below uses the former `>= 90` gate. The current gate requires every dimension
to equal 100. Preserve these recorded scores and decisions; they are not validation of the new
gate, and the missing raw run artifacts prevent rescoring this trace under the current rules.

Session `make-body/docs/criteria-opt/20260704-a/` — a real 3-loop run to terminal. Rubric: 10
dimensions, gate threshold `>= 90` on every dimension.

| Stage | Observed outcome |
| --- | --- |
| loop-1 baseline (`2-eval-result`) | Three dimensions below gate: 증거 결박 실재성 **84**, 배치 승격·정합성 무결성 **85**, Essential 인간 비준 게이트 **88**. |
| loop-1 → loop-2 freeze | Targeted dimensions recovered: 84 → **97**, 85 → **90**, 88 → **100**. Non-targeted `NEW_DROP` caught by the freeze comparison: flow-first R1 절차 순서 준수 100 → **88** (collateral, recorded as a label, not attributed to any edit). |
| loop-2 → loop-3 freeze | The `NEW_DROP` dimension recovered under loop-2's targeted edits: flow-first 88 → **100**. NEW_DROP check found no further sub-90 non-targeted drop. |
| loop-3 TERMINAL | Judger = `SUCCESS`: every dimension `>= 90`, lowest 96 (기록 규율 96; all others 100). Stage 4/5 not run. |

What this trace demonstrates:

- **Behavior change is measurable** — the loop moved three sub-gate dimensions to pass and reached a
  clean terminal, recorded as concrete score deltas rather than an assertion of improvement.
- **The gate is real** — `SUCCESS` fired only once all dimensions cleared `>= 90`, not on partial
  progress.
- **The NEW_DROP safety net works** — a collateral regression a loop did not target (flow-first
  100 → 88) was surfaced at the freeze and driven back to 100, showing the every-dimension
  comparison catches side effects instead of only crediting targeted gains.

Full per-edit outcomes and the terminal delta record are in
`make-body/docs/criteria-opt/20260704-a/history.md`.

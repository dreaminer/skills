# Great Skill Checklist

This checklist is based on the Trigger, Structure, Steering, and Pruning frame from
`[한영자막] 좋은 Agent Skill을 만드는 방법` and its linked `writing-great-skills` reference.

## Trigger

The skill must be reachable at the right time without adding avoidable context load.

- Invocation mode is deliberate.
  - Model-invoked: keep a description only when the agent or another skill must discover it.
  - User-invoked: use `disable-model-invocation: true` when only the human should remember and call it.
  - Router: consider one user-invoked router when many user-invoked skills create cognitive load.
- Description is precise.
  - First sentence says what the skill does.
  - Trigger clause names distinct branches, not synonym piles.
  - Trigger wording uses terms the user, docs, or codebase actually use.
  - It avoids false positives from generic words such as improve, help, quality, workflow, or review
    unless those are narrowed by object and situation.
- The description does not restate body identity, implementation details, or generic virtues.
- Trigger examples or sample prompts exist when trigger risk is material.

Common findings:

- Overbroad model-invoked description that fires on unrelated work.
- User-invoked skill that should be reachable by another skill.
- Trigger branches hidden only in the body, so the agent never loads the skill.
- Several phrases naming the same branch, wasting context and weakening the trigger.

## Structure

The skill should expose what every run needs and disclose what only some runs need.

- `SKILL.md` contains the operational core: ordered steps, required gates, and always-needed rules.
- Reference material moves behind clear context pointers when only some branches need it.
- Each context pointer says when to open the referenced file, not merely that the file exists.
- Steps end with checkable completion criteria.
- Branches are explicit enough that the agent knows which path it is in.
- Related definitions, rules, and caveats are co-located instead of scattered.
- Split only when it earns a cost:
  - by invocation, when a distinct leading word should trigger independently;
  - by sequence, when visible later steps cause premature completion.

Common findings:

- Sprawl: `SKILL.md` is long because reference was not disclosed.
- Hidden must-have material: required instructions live behind a weak pointer.
- Premature completion risk: later steps are visible while the current step has a fuzzy done state.
- Fragmentation: one concept is explained across several sections or files.

## Steering

The wording should make the agent follow the same process each run.

- The skill uses leading words that recruit useful existing model priors.
- Leading words are strong enough to change behavior, not decorative labels.
- Instructions describe the positive target behavior.
- Prohibitions are kept only for hard guardrails and paired with what to do instead.
- Completion criteria are both clear and demanding where quality depends on exhaustive work.
- The text requires legwork inside a step when the agent must inspect every file, case, branch,
  candidate, or evidence item.
- The skill avoids vague endings such as "reach understanding", "make it good", or "handle edge cases"
  unless paired with observable evidence.

Common findings:

- Negation-driven steering that repeats the unwanted behavior.
- Weak no-op leading words such as careful, high quality, or best practices.
- Completion criteria that allow the agent to stop after a plausible summary.
- Missing legwork demand, so the agent can skip evidence collection.

## Pruning

Every retained line should still change behavior or preserve maintainability.

- Each meaning has one authoritative home.
- Repeated meaning is consolidated unless a repeated leading word is intentionally steering behavior.
- Stale details, obsolete branches, and old failure patches are removed.
- Sentence-level no-op test passes: the line changes behavior compared with the model default.
- Generic advice is deleted, not rephrased.
- Safety guardrails are specific to the skill's real risks.

Common findings:

- Sediment: old instructions from prior incidents remain after the workflow changed.
- Duplication: the same rule appears in frontmatter, body, and reference with slight differences.
- No-op prose: "be thorough", "follow best practices", "ensure quality".
- Defensive accretion: many narrow patches that should be replaced by one stronger principle.

## Validation

A good skill should have evidence that it improves behavior or at least a plan to produce that
evidence.

- Trigger tests cover true positives and false positives.
- Execution tests or example tasks show the skill changes output versus no skill or previous skill.
- Risky changes are compared against traces, eval fixtures, or known failure cases.
- Claims of improvement are tied to observable outcomes such as pass rate, elapsed time, token usage,
  fewer clarification loops, fewer missed files, or fewer invalid outputs.
- Missing validation is reported as a gap, not guessed away.

Common findings:

- The skill has no examples, traces, smoke tasks, or evals.
- Only success paths are tested; trigger false positives and failure paths are ignored.
- The skill is judged by readability without checking whether it changes agent behavior.
- A proposed edit adds process but no way to measure whether the process helped.

## Source Notes

- Video basis: https://www.youtube.com/watch?v=69Tpanmk288
- Linked reference from the video: https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md
- Validation emphasis: https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills

# Validation Smoke Examples

Use this file only as lightweight validation evidence for `skill-auditor` itself, or when a
caller asks whether its trigger boundary is correct. It is not an extra checklist for every audited
skill.

## Trigger Smoke Set

Expected to invoke `skill-auditor`:

| Prompt | Expected reason |
| --- | --- |
| "Audit this agent skill for trigger and structure problems." | Direct request to audit an agent skill. |
| "Is this SKILL.md worth keeping?" | Direct request to judge skill value and maintainability. |
| "Sanity-check whether this skill is triggerable." | Direct request to inspect skill triggerability. |
| "Score this skill's steering and validation evidence." | Direct request to score skill quality axes. |

Expected not to invoke `skill-auditor`:

| Prompt | Expected reason |
| --- | --- |
| "Review this pull request." | Code review, not agent-skill audit. |
| "Improve the onboarding workflow." | Generic workflow improvement, no skill object. |
| "Validate this JSON schema." | Artifact validation, not agent-skill validation. |
| "Is this architecture maintainable?" | Architecture review, not skill maintainability. |

## Example Audit Trace

Input:

```text
Please audit this skill:

---
name: example-helper
description: Helps with quality and workflow. Use when the user asks for help.
---

# Example Helper

Review the user's work carefully and improve it.
Give useful advice.
```

Expected report shape:

```text
Verdict: FAIL

Inferred Contract
- The skill claims to help broadly with user work, but it does not define a specific auditable job.

Findings
- [high] [Trigger] Description is overbroad
  Evidence: "Use when the user asks for help."
  Risk: The skill can load for unrelated requests and add avoidable context load.
  Minimal fix: Narrow the trigger to a specific object and task.

- [high] [Steering] Instructions do not force repeatable behavior
  Evidence: "Review the user's work carefully and improve it."
  Risk: The agent can produce generic advice without inspecting concrete evidence.
  Minimal fix: Replace vague instructions with ordered steps and checkable completion criteria.

- [medium] [Validation] No behavior evidence is present
  Evidence: No examples, traces, smoke tasks, or eval fixtures are linked.
  Risk: The skill is judged by readability rather than observed behavior change.
  Minimal fix: Add true-positive and false-positive trigger examples plus one example audit trace.

Axis Summary
| Axis | Status | Notes |
| --- | --- | --- |
| Trigger | FAIL | Overbroad model-invoked description. |
| Structure | NEEDS_WORK | Body is short but lacks ordered execution structure. |
| Steering | FAIL | Vague instructions do not constrain output. |
| Pruning | NEEDS_WORK | Generic no-op prose dominates the body. |
| Validation | FAIL | No validation evidence. |

Validation Gaps
- None beyond the validation finding above.
```

This trace checks that `skill-auditor` starts with a verdict, lists findings in severity order,
quotes short evidence, avoids praise, and reports missing validation instead of guessing behavior
quality.

## PASS Boundary Trace

Input:

```text
Please audit this skill:

---
name: json-schema-checker
description: Validates JSON Schema files for syntax, draft compatibility, and repository-specific schema conventions. Use when the user asks to validate or sanity-check a JSON Schema file or schema directory.
---

# JSON Schema Checker

## Workflow

1. Read the target schema files.
2. Identify the declared draft and validate syntax with the repository's existing schema tooling.
3. Check repository-specific conventions only when a linked convention file exists.
4. Report blocking validation failures first, then non-blocking convention gaps.

## Output

- Verdict: PASS | NEEDS_WORK | FAIL
- Blocking failures
- Convention gaps

## Smoke Examples

- `schema/valid-user.schema.json` should pass syntax and draft checks.
- `schema/missing-type.schema.json` should fail because a required property has no type.
```

Expected report shape:

```text
Verdict: PASS

Inferred Contract
- The skill validates JSON Schema files for syntax, draft compatibility, and local conventions.

Findings
- None.

Axis Summary
| Axis | Status | Notes |
| --- | --- | --- |
| Trigger | PASS | Trigger is narrowed to JSON Schema files or schema directories. |
| Structure | PASS | Workflow has ordered evidence collection and reporting steps. |
| Steering | PASS | The skill requires tool-backed validation before reporting. |
| Pruning | PASS | Instructions are short and behavior-affecting. |
| Validation | PASS | The skill has lightweight smoke examples but no runtime trace. |

Validation Gaps
- Add one smoke fixture with a passing schema and one failing schema if this skill will be reused.
```

This trace checks that `skill-auditor` can return `PASS` with non-blocking validation gaps instead
of manufacturing findings when the core contract is intact.

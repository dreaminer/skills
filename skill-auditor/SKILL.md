---
name: skill-auditor
disable-model-invocation: true
description: Audits agent skills for predictable invocation, structure, steering, pruning, and evidence-backed validation. Use when the user asks to audit, harden, or sanity-check an agent skill or SKILL.md.
---

# Skill Auditor

## Purpose

Check whether an agent skill is likely to earn its context/cognitive cost by making agent behavior
more predictable, not merely by being well written.

## Inputs

- Target skill directory or `SKILL.md`.
- Any behavior-affecting references linked from `SKILL.md`.
- Optional sample prompts, traces, eval results, or observed failures.
- Optional user goal: audit only, score, compare versions, or propose fixes.

## Workflow

1. Collect the target skill source.
   - Read `SKILL.md` completely.
   - Read only references directly needed by links, branches, or checks in `SKILL.md`.
   - Treat examples, scripts, and eval fixtures as evidence when they affect behavior.
   - When auditing `skill-auditor` itself or checking its trigger boundary, use
     [Validation Smoke Examples](references/validation-smoke.md) as lightweight evidence.

2. State the inferred contract.
   - Identify the skill's job, expected trigger phrases, likely invocation mode, main branches,
     and completion criteria.
   - If the contract is unclear, mark that as a finding instead of asking the user to define it.

3. Audit every axis in [Great Skill Checklist](references/great-skill-checklist.md).
   - `Trigger`: whether the skill should be model-invoked or user-invoked, and whether its
     description can trigger at the right time without broad false positives.
   - `Structure`: whether steps, reference, disclosed files, branches, and split points sit at
     the right information level.
   - `Steering`: whether the wording produces repeatable agent behavior through leading words,
     positive instructions, legwork, and checkable completion criteria.
   - `Pruning`: whether duplicated meaning, stale sediment, sprawl, no-ops, and weak guardrails
     dilute the skill.
   - `Validation`: whether there is evidence the skill improves behavior, triggers correctly, and
     does not quietly hurt performance.

4. Produce a verification report.
   - Start with the verdict, then list findings ordered by severity.
   - Use these severity levels consistently:
     - `high`: likely wrong invocation, incoherent contract, unsafe behavior, or output that cannot
       perform the stated job.
     - `medium`: repeatability, maintainability, or validation weakness that can change audit
       results but does not by itself block `PASS` when the skill's core job is intact.
     - `low`: local clarity, fixture, or evidence-packaging issue with low behavior risk.
   - Classify missing validation evidence consistently:
     - If the skill has lightweight smoke examples or fixtures and makes no claim of observed
       runtime improvement, report missing stronger run evidence under `Validation Gaps`, not as a
       blocking finding.
     - Use a validation finding when there are no examples, traces, smoke tasks, or eval fixtures;
       when the skill claims observed improvement without evidence; or when the user explicitly
       asked to validate runtime behavior.
   - For each finding include: `severity`, `axis`, `evidence`, `risk`, and `minimal fix`.
   - `minimal fix` is always a short remediation direction, not a full edit proposal.
   - Quote only short snippets needed to prove the issue.
   - Do not praise; note strengths only when they explain why no finding exists on an axis.

5. Assign a verdict.
   - `PASS`: no high-severity findings, and the skill has plausible trigger, structure, steering,
     pruning, and at least lightweight validation evidence. Medium or low findings may still be
     present if they are reported as non-blocking gaps.
   - `NEEDS_WORK`: one or more `high` findings, but the skill's contract is recoverable with local
     edits.
   - `FAIL`: the trigger is unsafe or incoherent, the body does not support the stated job, or the
     skill is mostly duplicated, stale, untestable, or no-op content.
   - Use the same status rule in `Axis Summary`: `PASS` for an axis that supports the core job,
     even with non-blocking gaps; `NEEDS_WORK` for a recoverable `high` issue; `FAIL` for an
     unrecoverable or contract-breaking issue.

6. If the user asked for fixes, propose the smallest edits.
   - Treat these as a separate edit proposal beyond the per-finding `minimal fix`.
   - Apply a behavior-leverage gate before proposing any edit: the edit must improve invocation
     accuracy, execution repeatability, evidence quality, safety, or maintainability enough to
     justify its added context and cognitive cost.
   - Prefer description tightening, sharper completion criteria, moving reference behind a pointer,
     deleting no-ops, or consolidating duplicate meaning.
   - Leave non-blocking validation gaps as gaps unless a lightweight fixture or trace would clarify
     a verdict boundary without making the skill materially heavier.
   - Do not broaden scope, add generic best-practice prose, or rewrite the whole skill unless the
     contract is unrecoverable.

## Output Format

```
Verdict: PASS | NEEDS_WORK | FAIL

Inferred Contract
- ...

Findings
- [severity] [axis] Finding title
  Evidence: ...
  Risk: ...
  Minimal fix: ...

Axis Summary
| Axis | Status | Notes |
| --- | --- | --- |

Validation Gaps
- ...
```

## Rules

- Judge behavior leverage, not prose polish.
- Prefer observed traces and evals over intuition; when evidence is missing, say so.
- Do not repeat the same missing evidence as both a finding and a validation gap.
- A line earns its place only if it changes invocation, execution, safety, or maintainability.
- Keep each meaning in one source of truth.
- Do not edit files during an audit unless the user explicitly asks for implementation.

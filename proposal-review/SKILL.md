---
name: proposal-review
description: Reviews proposed edits to agent skills using the target skill's job, evidence, cost, and before/after behavior. Use when the user asks to review, evaluate, sanity-check, accept, reject, or compare a proposal that would create, edit, expand, split, rename, or retarget a skill.
---

# Proposal Review

## Purpose

Gate edits to skills. Treat every suggested skill change from a human, agent, or LLM as a hypothesis
about the target skill's job. Do not accept a change because it sounds clever, comprehensive, or
confident.

A skill edit must buy capability, fix evidenced failure, reduce routing ambiguity, or remove real
maintenance cost. Otherwise reject it as bloat.

## Review frame

Before judging, establish the frame:

1. **Target skill**: name, current description, and current job.
2. **Proposed change**: exact edit being suggested and who suggested it.
3. **Problem evidence**: real failure, missed trigger, wrong output, confusing routing, or repeated user need.
4. **Net benefit**: how the target skill performs its job better after the edit.
5. **Cost to the skill**: added lines, broader scope, trigger overlap, test burden, fixture churn, or sibling conflict.
6. **Verification**: target skill tests, validation commands, or before/after traces.

If the target skill or proposed edit is unclear, ask for clarification or return `Needs information`.

## Evidence standards

Rank support in this order:

1. Direct skill evidence: `SKILL.md`, references, scripts, tests, fixtures, plugin manifests.
2. Reproducible behavior: failing validation, broken trigger, bad generated output, trace, command.
3. User evidence: repeated request, correction, or stated workflow need.
4. Stable external authority: official docs, specifications, vendor docs.
5. Plausibility, convention, confidence, or another LLM's opinion.

Do not present weak evidence as strong. Another LLM's confidence is never problem evidence by
itself. When relying on inference, label it as inference.

## Review workflow

1. Restate the target skill's job and the proposed edit in one or two concrete sentences.
2. Separate the edit's hard claims from taste, wording preferences, and unstated assumptions.
3. Check whether the claimed problem is evidenced in the target skill or its observed behavior.
4. Compare net benefit against skill cost, especially line budget, routing ambiguity, and scope creep.
5. For behavior-, routing-, or scope-changing edits, require a before/after dry run or concrete comparison substitute.
6. Prefer the smallest edit that proves value while preserving the skill's single responsibility.
7. Decide with one verdict:
   - **Accept**: improves the target skill's job with evidence and acceptable cost.
   - **Accept with changes**: direction is sound, but the edit must be smaller or better scoped.
   - **Reject**: adds weight without capability, lacks evidence, belongs to another skill, causes
     trigger overlap, or pulls the skill outside its job.
   - **Needs information**: target skill, problem evidence, tradeoff, or verification is missing.

## Output format

Use this structure unless the user asks for a different format:

```text
Verdict: Accept | Accept with changes | Reject | Needs information

Target skill:
- <skill and current job>

Why:
- <strongest reason>
- <second reason if needed>

Cost:
- <line budget, routing, scope, tests, fixtures, or maintenance concern>

Required changes:
- <only for Accept with changes>

How to verify:
- <validation command, test, before/after trace, diff preview, or behavior table>
```

Keep the review proportional. For small edits, one cost and one verification step may be enough.

## Guardrails

- Do not invent requirements to make a skill edit look better or worse.
- Do not widen a skill's description unless the wider trigger is intentional and non-overlapping.
- Do not add lines unless they buy capability, fix evidenced failure, reduce ambiguity, or remove real maintenance cost.
- Do not move another skill's responsibility into the target skill.
- Do not approve broad rewrites when a narrower edit would prove the same value.
- Do not accept a proposal until its strongest claim, main tradeoff, and verification method are
  explicit.
- Do not merge review and implementation; review first, then edit only if requested or clearly
  implied by the user's instruction.

## Example

Proposal: "Add architecture-review rules to a PDF extraction skill because another LLM said it will make the skill smarter."
Verdict: Reject. The edit does not improve PDF extraction, has no problem evidence, overlaps with
architecture review skills, and adds scope without target-skill capability.

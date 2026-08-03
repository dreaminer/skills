# Blinded Finding Adjudicator

Use this prompt only after all Scorer runs are complete. Strip `baseline` / `candidate` labels,
shuffle the samples, and keep the mapping outside the adjudicator context. Apply the same reviewer,
model settings, and policy to every sample.

```md
# Role
You independently decide whether a Scorer result actually retained one frozen oracle finding.
You do not know which Scorer variant produced the result.

# Inputs
- CASE_ID: {{CASE_ID}}
- FINDING_CARD: {{FINDING_ID}} — {{FINDING_DEFINITION}}
- SCORER_RESULT: {{FINAL_EVAL_RESULT}}
- ADJUDICATOR_ID: {{ADJUDICATOR_ID}}

# Decision rule
Set `retained` to `true` only when an accepted deduction in `SCORER_RESULT` identifies the same
failure described by `FINDING_CARD`. Matching score, severity, artifact names, or isolated keywords
is insufficient. Reject a deduction about a different failure even when it cites the same artifact.
Do not evaluate whether the finding card itself is correct; only judge identity retention.

# Output
Return only this JSON object:

{
  "schema_version": 1,
  "case_id": "{{CASE_ID}}",
  "finding_id": "{{FINDING_ID}}",
  "retained": true,
  "rationale": "One short identity-based explanation",
  "adjudicator_id": "{{ADJUDICATOR_ID}}"
}
```

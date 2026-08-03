# Result Layout

Do not commit model outputs by default. Save local experiment results in this shape:

```text
results/
  baseline/
    run-1/
      <case-id>.md
      <true-defect-case-id>.adjudication.json
      metrics.json
    run-2/
    run-3/
  candidate/
    run-1/
    run-2/
    run-3/
```

Each `<case-id>.md` is the Scorer's exact `FINAL_EVAL_RESULT`. The checker accepts the frozen
baseline prompt's two native artifact forms and the candidate's locator-rich form:

```text
A-001: "exact quote from the artifact"
A-001(final-response): "exact quote from the artifact"
[A-001@final-response] "exact quote from the artifact"
```

An artifact id must match `[A-Za-z0-9][A-Za-z0-9._-]*`; a locator must match
`[A-Za-z0-9][A-Za-z0-9._/-]*`. Because the result is an unescaped Markdown table, an exact quote
must be one line and cannot contain `"` or `|`.
All forms require the artifact id and exact quote to match `RUNNER_OUTPUT`; when a locator is present,
it must match too. This lets the unchanged baseline copy evidence already present in its fixed
Sub-scorer inputs without requiring a locator it was never shown.

Every true-defect result also requires a sidecar produced after variant labels are removed and the
samples are shuffled. Use the same independent human or model reviewer for both variants:

```json
{
  "schema_version": 1,
  "case_id": "true-omission",
  "finding_id": "missing-final-decision",
  "retained": true,
  "rationale": "The accepted deduction is the missing final decision described by the finding card.",
  "adjudicator_id": "blind-reviewer-1"
}
```

`finding_id` must equal the frozen oracle finding card. `retained` answers whether the result
actually accepted that same defect, not whether it merely deducted points. The Scorer output and
the adjudication sidecar must be produced in separate contexts.

Every run requires a `metrics.json` for the whole batch:

```json
{
  "execution": {
    "model": "model identifier",
    "settings": {
      "temperature": 0
    },
    "tool_policy": "same policy label for both variants",
    "clean_context": true
  },
  "cost": {
    "calls": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "latency_ms": 0
  }
}
```

All baseline and candidate runs must have identical `execution` objects. The comparison command
treats `cost` as reported information, not an acceptance gate, until a budget is agreed.

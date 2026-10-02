# Scorer Before/After Comparison

This suite isolates the Scorer decision seam agreed for the adversarial-validation experiment:

```text
FINAL_RUBRIC + RUNNER_OUTPUT + fixed SUB_SCORERS_OUTPUTS
  -> accepted/rejected deductions in FINAL_EVAL_RESULT
```

It does **not** modify `scorer/SKILL.md` or its live prompts. Discovery outputs are frozen so the
first comparison measures validation behavior rather than stochastic differences in defect search.

## Fixed cases

| Case | Ground truth | Failure mode controlled |
| --- | --- | --- |
| `true-omission` | defect | Required final decision is absent. |
| `true-distortion` | defect | Final claim contradicts raw execution counts. |
| `true-violation` | defect | A dry-run performs an external write. |
| `out-of-rubric` | no defect | All finders demand a citation the rubric never required. |
| `misquoted-context` | no defect | A negated phrase is truncated into the opposite meaning. |
| `ambiguous-insufficient` | no defect | A conditional requirement is charged when its precondition is false. |
| `duplicate-defect` | defect, once | Two lenses report the same underlying failure. |
| `clean-run` | no defect | Empty deductions must remain a valid result. |
| `true-minor` | defect, once | A required timestamp suffix is absent; duplicate Minor findings deduct once. |
| `false-minor` | no defect | A formatting preference is charged despite full rubric compliance. |
| `major-boundary` | defect | A 10-point Major deduction must still block SUCCESS. |

The oracle for each case is fixed in `fixtures/<case>/expected.json`. Never pass that file to a
Scorer agent. Each case's other three files are the complete comparison capsule; each variant still
receives only the fields declared by its frozen prompt.

## Validate the suite

```sh
scorer/tests/run.sh
```

This runs the comparison CLI tests and validates all fixture contracts, Runner fields, artifact
identifiers, frozen lens outputs, dimensions, deductions, and oracle evidence.

## Run the experiment

Use the same model, model settings, tool policy, and clean-context policy for both variants. Run all
eleven cases three times per variant as fixed by `comparison-contract.json`.

1. Render a case input when needed:

   ```sh
   node scorer/tests/render-case.mjs true-omission
   ```

2. For `baseline`, use `prompts/baseline-main-scorer.md`. It intentionally receives the same inputs
   the pre-change prompt declared. Keep `RUNNER_OUTPUT` in the experiment capsule for oracle grounding,
   but do not silently add it to the baseline prompt.
3. For `candidate`, use section 2-B of `../references/scorer-prompts.md`, including its raw
   `RUNNER_OUTPUT` input and explicit deduction formula. Both variants are evaluated against the
   current 100-only gate; the frozen baseline prompt remains unchanged. This is a combined contract
   comparison, not evidence isolating the effect of adding raw input alone.
4. Save each exact five-column result under the layout in `results/README.md`. The checker accepts
   the frozen baseline's native artifact citations as well as the candidate's locator-rich form, so
   output formatting alone cannot bias the verdict. Record identical execution metadata plus calls,
   tokens, and latency in every run's required `metrics.json`.
5. Remove variant labels, shuffle the true-defect results, and have the same independent reviewer
   apply `prompts/blinded-finding-adjudicator.md`. Save one adjudication sidecar beside each
   true-defect result. The Scorer never sees the oracle finding card.
6. Compare:

   ```sh
   scorer/tests/run.sh \
     scorer/tests/results/baseline \
     scorer/tests/results/candidate
   ```

Pass `--json` directly to `compare-results.mjs` when machine-readable output is needed. The CLI
loads the bundled comparison contract by default. An alternate `--contract` must still use schema 1,
exactly three runs, required metrics, and matching execution metadata; it cannot weaken those
controls.

## Decision rule

`IMPROVED` requires strictly fewer false positives and no regression in false negatives, score
contracts, gate decisions, evidence validity, or repeated-run stability.
`INCONCLUSIVE` means a trade-off occurred; `REGRESSED` rejects the candidate; `NO_CHANGE` is not
evidence that the added calls buy capability. Cost is reported separately until a budget is agreed.

A true defect is retained only when its blinded adjudication matches the stable oracle `finding.id`
and its cited artifact quote is grounded. Its numeric score is checked separately. This avoids both
keyword matching and the possibility that an unrelated deduction at the expected score masquerades
as defect retention.

Only after the isolated comparison passes should the candidate be exercised through a full
`criteria-opt` loop to observe downstream proposal quality and regression behavior.

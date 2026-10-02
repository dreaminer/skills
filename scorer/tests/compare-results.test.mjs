import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const scriptPath = new URL("./compare-results.mjs", import.meta.url).pathname;
const defaultEvidenceRef = {
  artifact_id: "A-001",
  locator: "final-response",
  quote: "최종 결과 없음",
};

function writeJson(filePath, value) {
  writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

function writeContract(root) {
  const contractPath = path.join(root, "unit-comparison-contract.json");
  writeJson(contractPath, {
    schema_version: 1,
    runs_per_variant: 3,
    require_metrics: true,
    require_matching_execution: true,
  });
  return contractPath;
}

function writeExpected(caseDir, value) {
  const expected = value.truth === "DEFECT" && !value.finding
    ? {
        ...value,
        finding: {
          id: "missing-final-decision",
          definition: "요구된 최종 판정이 결과에서 누락되거나 미기록 상태다.",
        },
      }
    : value;
  writeJson(path.join(caseDir, "expected.json"), expected);
  writeJson(path.join(caseDir, "runner-output.json"), {
    artifacts: [
      {
        artifact_id: defaultEvidenceRef.artifact_id,
        locator: defaultEvidenceRef.locator,
        content: defaultEvidenceRef.quote,
      },
    ],
  });
}

function writeAdjudication(runDir, caseId, retained) {
  writeJson(path.join(runDir, `${caseId}.adjudication.json`), {
    schema_version: 1,
    case_id: caseId,
    finding_id: "missing-final-decision",
    retained,
    rationale: retained
      ? "The accepted deduction is the frozen missing-final-decision finding."
      : "The frozen missing-final-decision finding was not accepted.",
    adjudicator_id: "blind-reviewer-test",
  });
}

function sealExperiment(root) {
  const fixturesDir = path.join(root, "fixtures");
  const expectations = readdirSync(fixturesDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => JSON.parse(readFileSync(
      path.join(fixturesDir, entry.name, "expected.json"),
      "utf8",
    )));
  const defaultExecution = {
    model: "model-under-test",
    settings: { temperature: 0 },
    tool_policy: "no-tools",
    clean_context: true,
  };

  for (const variant of ["baseline", "candidate"]) {
    const variantDir = path.join(root, variant);
    let runDirs = readdirSync(variantDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && entry.name.startsWith("run-"))
      .map((entry) => path.join(variantDir, entry.name))
      .sort();
    while (runDirs.length < 3) {
      const target = path.join(variantDir, `run-${runDirs.length + 1}`);
      cpSync(runDirs.at(-1), target, { recursive: true });
      runDirs.push(target);
    }

    for (const runDir of runDirs) {
      for (const expected of expectations.filter((item) => item.truth === "DEFECT")) {
        const adjudicationPath = path.join(runDir, `${expected.case_id}.adjudication.json`);
        if (!existsSync(adjudicationPath)) {
          const report = readFileSync(path.join(runDir, `${expected.case_id}.md`), "utf8");
          const retained = !/^\|[^\n]*\|\s*100\s*\|/m.test(report);
          writeAdjudication(runDir, expected.case_id, retained);
        }
      }

      const metricsPath = path.join(runDir, "metrics.json");
      const metrics = existsSync(metricsPath)
        ? JSON.parse(readFileSync(metricsPath, "utf8"))
        : {};
      writeJson(metricsPath, {
        execution: metrics.execution ?? defaultExecution,
        cost: {
          calls: 0,
          input_tokens: 0,
          output_tokens: 0,
          latency_ms: 0,
          ...metrics.cost,
        },
      });
    }
  }
}

function scoreReport(
  score,
  evidence = score === 100
    ? ""
    : `[${defaultEvidenceRef.artifact_id}@${defaultEvidenceRef.locator}] "${defaultEvidenceRef.quote}"`,
  reason = "최종 결과가 누락됨",
) {
  return `### [최종 평가 결과서]
| 평가 항목명 | 최종 평점 | 감점 이유 | 검증된 근거 (Evidence) | 고득점 요건 |
| :--- | :--- | :--- | :--- | :--- |
| 근거 충실성 | ${score} | ${score === 100 ? "" : reason} | ${evidence} | 요구된 사실을 실행 결과에 근거해 정확하게 보고한다. |
`;
}

for (const score of [90, 96, 99]) {
  test(`a retained defect scoring ${score} continues the loop`, () => {
    const root = mkdtempSync(path.join(os.tmpdir(), "scorer-gate-"));
    const caseDir = path.join(root, "fixtures", "boundary-defect");
    mkdirSync(caseDir, { recursive: true });
    writeExpected(caseDir, {
      case_id: "boundary-defect",
      dimension: "근거 충실성",
      truth: "DEFECT",
      score_expectation: { operator: "eq", value: score },
      expected_gate: "CONTINUE_TO_STAGE_4",
      required_evidence: [defaultEvidenceRef],
    });
    for (const variant of ["baseline", "candidate"]) {
      const runDir = path.join(root, variant, "run-1");
      mkdirSync(runDir, { recursive: true });
      writeFileSync(path.join(runDir, "boundary-defect.md"), scoreReport(score));
    }
    sealExperiment(root);
    const result = JSON.parse(execFileSync(process.execPath, [
      scriptPath, "--fixtures", path.join(root, "fixtures"),
      "--baseline", path.join(root, "baseline"),
      "--candidate", path.join(root, "candidate"), "--json",
    ], { encoding: "utf8" }));
    assert.equal(result.candidate.gate_errors, 0);
    assert.equal(result.candidate.false_negatives, 0);
    assert.equal(result.candidate.score_contract_errors, 0);
  });
}

test("a spurious Minor deduction is both a false positive and a gate error", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-minor-"));
  const caseDir = path.join(root, "fixtures", "clean-run");
  mkdirSync(caseDir, { recursive: true });
  writeExpected(caseDir, {
    case_id: "clean-run", dimension: "근거 충실성", truth: "NO_DEFECT",
    score_expectation: { operator: "eq", value: 100 },
    expected_gate: "SUCCESS", required_evidence: [],
  });
  for (const variant of ["baseline", "candidate"]) {
    const runDir = path.join(root, variant, "run-1");
    mkdirSync(runDir, { recursive: true });
    writeFileSync(path.join(runDir, "clean-run.md"), scoreReport(variant === "baseline" ? 100 : 96));
  }
  sealExperiment(root);
  const result = JSON.parse(execFileSync(process.execPath, [
    scriptPath, "--fixtures", path.join(root, "fixtures"),
    "--baseline", path.join(root, "baseline"),
    "--candidate", path.join(root, "candidate"), "--json",
  ], { encoding: "utf8" }));
  assert.equal(result.behavior_verdict, "REGRESSED");
  assert.equal(result.baseline.gate_errors, 0);
  assert.equal(result.candidate.false_positives, 3);
  assert.equal(result.candidate.gate_errors, 3);
});

test("reports an improvement when the candidate removes a baseline false positive", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "out-of-rubric");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });

  writeExpected(caseDir, {
    case_id: "out-of-rubric",
    dimension: "근거 충실성",
    truth: "NO_DEFECT",
    score_expectation: { operator: "eq", value: 100 },
    expected_gate: "SUCCESS",
    required_evidence: [],
  });
  writeFileSync(path.join(baseline, "out-of-rubric.md"), scoreReport(85));
  writeFileSync(path.join(candidate, "out-of-rubric.md"), scoreReport(100));
  writeJson(path.join(baseline, "metrics.json"), {
    cost: {
      calls: 1,
      input_tokens: 100,
      output_tokens: 20,
      latency_ms: 1000,
    },
  });
  writeJson(path.join(candidate, "metrics.json"), {
    cost: {
      calls: 3,
      input_tokens: 300,
      output_tokens: 60,
      latency_ms: 2500,
    },
  });
  sealExperiment(root);

  const output = execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  );
  const result = JSON.parse(output);

  assert.equal(result.behavior_verdict, "IMPROVED");
  assert.equal(result.baseline.false_positives, 3);
  assert.equal(result.candidate.false_positives, 0);
  assert.equal(result.baseline.cost.calls, 3);
  assert.equal(result.candidate.cost.calls, 9);
  assert.equal(result.candidate.cost.latency_ms, 7500);

  const markdown = execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
    ],
    { encoding: "utf8" },
  );
  assert.match(markdown, /Behavior verdict: IMPROVED/);
  assert.match(markdown, /\| false_positives \| 3 \| 0 \| -3 \|/);
});

test("reports an inconclusive trade-off when a false-positive gain loses a true defect", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");

  for (const caseId of ["out-of-rubric", "true-omission"]) {
    mkdirSync(path.join(fixtures, caseId), { recursive: true });
  }
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });

  writeExpected(path.join(fixtures, "out-of-rubric"), {
    case_id: "out-of-rubric",
    dimension: "근거 충실성",
    truth: "NO_DEFECT",
    score_expectation: { operator: "eq", value: 100 },
    expected_gate: "SUCCESS",
    required_evidence: [],
  });
  writeExpected(path.join(fixtures, "true-omission"), {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });

  writeFileSync(path.join(baseline, "out-of-rubric.md"), scoreReport(85));
  writeFileSync(path.join(candidate, "out-of-rubric.md"), scoreReport(100));
  writeFileSync(path.join(baseline, "true-omission.md"), scoreReport(85));
  writeFileSync(path.join(candidate, "true-omission.md"), scoreReport(100));
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.behavior_verdict, "INCONCLUSIVE");
  assert.equal(result.baseline.false_positives, 3);
  assert.equal(result.baseline.false_negatives, 0);
  assert.equal(result.candidate.false_positives, 0);
  assert.equal(result.candidate.false_negatives, 3);
});

test("treats missing required evidence as a regression", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });

  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });
  writeFileSync(path.join(baseline, "true-omission.md"), scoreReport(85));
  writeFileSync(path.join(candidate, "true-omission.md"), scoreReport(85, "unstructured evidence"));
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.behavior_verdict, "REGRESSED");
  assert.equal(result.baseline.evidence_errors, 0);
  assert.equal(result.candidate.evidence_errors, 3);
  assert.deepEqual(result.candidate.failures, [
    {
      run_id: "run-1",
      case_id: "true-omission",
      errors: ["EVIDENCE", "FALSE_NEGATIVE"],
    },
    {
      run_id: "run-2",
      case_id: "true-omission",
      errors: ["EVIDENCE", "FALSE_NEGATIVE"],
    },
    {
      run_id: "run-3",
      case_id: "true-omission",
      errors: ["EVIDENCE", "FALSE_NEGATIVE"],
    },
  ]);
});

test("enforces the pre-agreed run count when a comparison contract is supplied", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "clean-run");
  const contractPath = path.join(root, "comparison-contract.json");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "clean-run",
    dimension: "근거 충실성",
    truth: "NO_DEFECT",
    score_expectation: { operator: "eq", value: 100 },
    expected_gate: "SUCCESS",
    required_evidence: [],
  });
  writeJson(contractPath, {
    schema_version: 1,
    runs_per_variant: 3,
    require_metrics: true,
    require_matching_execution: true,
  });
  writeFileSync(path.join(baseline, "clean-run.md"), scoreReport(100));
  writeFileSync(path.join(candidate, "clean-run.md"), scoreReport(100));

  const result = spawnSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /requires 3 runs per variant/);
});

test("reports a regression when candidate scores become unstable across repeated runs", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });

  for (const variant of ["baseline", "candidate"]) {
    for (const run of ["run-1", "run-2"]) {
      mkdirSync(path.join(root, variant, run), { recursive: true });
    }
  }
  writeFileSync(path.join(root, "baseline", "run-1", "true-omission.md"), scoreReport(85));
  writeFileSync(path.join(root, "baseline", "run-2", "true-omission.md"), scoreReport(85));
  writeFileSync(path.join(root, "candidate", "run-1", "true-omission.md"), scoreReport(85));
  writeFileSync(path.join(root, "candidate", "run-2", "true-omission.md"), scoreReport(80));
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.join(root, "baseline"),
      "--candidate",
      path.join(root, "candidate"),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.behavior_verdict, "REGRESSED");
  assert.equal(result.baseline.unstable_cases, 0);
  assert.equal(result.candidate.unstable_cases, 1);
});

test("does not call the candidate improved when false positives do not fall", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });

  for (const variant of ["baseline", "candidate"]) {
    for (const run of ["run-1", "run-2"]) {
      mkdirSync(path.join(root, variant, run), { recursive: true });
    }
  }
  writeFileSync(path.join(root, "baseline", "run-1", "true-omission.md"), scoreReport(85));
  writeFileSync(path.join(root, "baseline", "run-2", "true-omission.md"), scoreReport(80));
  writeFileSync(path.join(root, "candidate", "run-1", "true-omission.md"), scoreReport(85));
  writeFileSync(path.join(root, "candidate", "run-2", "true-omission.md"), scoreReport(85));
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.join(root, "baseline"),
      "--candidate",
      path.join(root, "candidate"),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.baseline.false_positives, 0);
  assert.equal(result.candidate.false_positives, 0);
  assert.equal(result.behavior_verdict, "NO_CHANGE");
});

test("rejects comparisons whose execution metadata differs between variants", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "clean-run");
  const contractPath = path.join(root, "comparison-contract.json");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "clean-run",
    dimension: "근거 충실성",
    truth: "NO_DEFECT",
    score_expectation: { operator: "eq", value: 100 },
    expected_gate: "SUCCESS",
    required_evidence: [],
  });
  writeJson(contractPath, {
    schema_version: 1,
    runs_per_variant: 3,
    require_metrics: true,
    require_matching_execution: true,
  });
  writeFileSync(path.join(baseline, "clean-run.md"), scoreReport(100));
  writeFileSync(path.join(candidate, "clean-run.md"), scoreReport(100));
  writeJson(path.join(baseline, "metrics.json"), {
    execution: {
      model: "model-a",
      settings: { temperature: 0 },
      tool_policy: "no-tools",
      clean_context: true,
    },
    cost: { calls: 1, input_tokens: 100, output_tokens: 20, latency_ms: 1000 },
  });
  writeJson(path.join(candidate, "metrics.json"), {
    execution: {
      model: "model-b",
      settings: { temperature: 0 },
      tool_policy: "no-tools",
      clean_context: true,
    },
    cost: { calls: 1, input_tokens: 100, output_tokens: 20, latency_ms: 1000 },
  });
  sealExperiment(root);

  const result = spawnSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /execution metadata must match/);
});

test("validates artifact id, locator, and exact quote instead of a loose substring", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [
      {
        artifact_id: "A-001",
        locator: "final-response",
        quote: "최종 결과 없음",
      },
    ],
  });
  writeJson(path.join(caseDir, "runner-output.json"), {
    artifacts: [
      {
        artifact_id: "A-001",
        locator: "final-response",
        content: "최종 결과 없음",
      },
    ],
  });
  writeFileSync(
    path.join(baseline, "true-omission.md"),
    scoreReport(85, "[A-404@final-response] \"최종 결과 없음\""),
  );
  writeFileSync(
    path.join(candidate, "true-omission.md"),
    scoreReport(85, "[A-001@final-response] \"최종 결과 없음\""),
  );
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.baseline.evidence_errors, 3);
  assert.equal(result.candidate.evidence_errors, 0);
});

test("detects unstable findings even when repeated runs keep the same score", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });

  for (const variant of ["baseline", "candidate"]) {
    for (const run of ["run-1", "run-2"]) {
      mkdirSync(path.join(root, variant, run), { recursive: true });
    }
  }
  writeFileSync(path.join(root, "baseline", "run-1", "true-omission.md"), scoreReport(85, "최종 결과 없음"));
  writeFileSync(path.join(root, "baseline", "run-2", "true-omission.md"), scoreReport(85, "최종 결과 없음"));
  writeFileSync(path.join(root, "candidate", "run-1", "true-omission.md"), scoreReport(85, "최종 결과 없음"));
  writeFileSync(path.join(root, "candidate", "run-2", "true-omission.md"), scoreReport(85, "다른 근거: 최종 결과 없음"));
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.join(root, "baseline"),
      "--candidate",
      path.join(root, "candidate"),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.baseline.unstable_cases, 0);
  assert.equal(result.candidate.unstable_cases, 1);
});

test("rejects non-integer or out-of-range scores before comparison", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });
  writeFileSync(path.join(baseline, "true-omission.md"), scoreReport(85, "최종 결과 없음"));
  writeFileSync(path.join(candidate, "true-omission.md"), scoreReport(-1, "최종 결과 없음"));
  sealExperiment(root);

  const result = spawnSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /score must be an integer from 0 to 100/);
});

test("accepts the frozen baseline prompt's native artifact evidence form", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });
  writeFileSync(
    path.join(baseline, "true-omission.md"),
    scoreReport(85, 'A-001(final-response): "최종 결과 없음"'),
  );
  writeFileSync(path.join(candidate, "true-omission.md"), scoreReport(85));
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.baseline.evidence_errors, 0);
  assert.equal(result.baseline.false_negatives, 0);
  assert.equal(result.behavior_verdict, "NO_CHANGE");
});

test("rejects an unrelated deduction even when it has the expected score and evidence", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const contractPath = writeContract(root);
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "true-omission");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "true-omission",
    dimension: "근거 충실성",
    truth: "DEFECT",
    score_expectation: { operator: "lt", value: 90 },
    expected_gate: "CONTINUE_TO_STAGE_4",
    required_evidence: [defaultEvidenceRef],
  });
  writeFileSync(path.join(baseline, "true-omission.md"), scoreReport(85));
  writeFileSync(
    path.join(candidate, "true-omission.md"),
    scoreReport(85, undefined, "최종 결과에서 요구되지 않은 출처 링크가 누락됨"),
  );
  writeAdjudication(candidate, "true-omission", false);
  sealExperiment(root);

  const result = JSON.parse(execFileSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  ));

  assert.equal(result.baseline.false_negatives, 0);
  assert.equal(result.candidate.false_negatives, 3);
  assert.equal(result.behavior_verdict, "REGRESSED");
});

test("applies the bundled comparison contract when --contract is omitted", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "clean-run");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "clean-run",
    dimension: "근거 충실성",
    truth: "NO_DEFECT",
    score_expectation: { operator: "eq", value: 100 },
    expected_gate: "SUCCESS",
    required_evidence: [],
  });
  writeFileSync(path.join(baseline, "clean-run.md"), scoreReport(100));
  writeFileSync(path.join(candidate, "clean-run.md"), scoreReport(100));

  const result = spawnSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--json",
    ],
    { encoding: "utf8" },
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /requires 3 runs per variant/);
});

test("rejects a custom contract that disables mandatory controls", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "scorer-compare-"));
  const fixtures = path.join(root, "fixtures");
  const baseline = path.join(root, "baseline", "run-1");
  const candidate = path.join(root, "candidate", "run-1");
  const caseDir = path.join(fixtures, "clean-run");
  const contractPath = path.join(root, "unsafe-contract.json");

  mkdirSync(caseDir, { recursive: true });
  mkdirSync(baseline, { recursive: true });
  mkdirSync(candidate, { recursive: true });
  writeExpected(caseDir, {
    case_id: "clean-run",
    dimension: "근거 충실성",
    truth: "NO_DEFECT",
    score_expectation: { operator: "eq", value: 100 },
    expected_gate: "SUCCESS",
    required_evidence: [],
  });
  writeFileSync(path.join(baseline, "clean-run.md"), scoreReport(100));
  writeFileSync(path.join(candidate, "clean-run.md"), scoreReport(100));
  writeJson(contractPath, {
    schema_version: 1,
    runs_per_variant: 3,
    require_metrics: false,
    require_matching_execution: false,
  });

  const result = spawnSync(
    process.execPath,
    [
      scriptPath,
      "--fixtures",
      fixtures,
      "--baseline",
      path.dirname(baseline),
      "--candidate",
      path.dirname(candidate),
      "--contract",
      contractPath,
      "--json",
    ],
    { encoding: "utf8" },
  );

  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /cannot disable required metrics/);
});

#!/usr/bin/env node

import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";

const BEHAVIOR_METRICS = [
  "false_positives",
  "false_negatives",
  "score_contract_errors",
  "gate_errors",
  "evidence_errors",
  "unstable_cases",
];
const COST_METRICS = ["calls", "input_tokens", "output_tokens", "latency_ms"];
const DEFAULT_CONTRACT_PATH = new URL("./comparison-contract.json", import.meta.url).pathname;
const ARTIFACT_ID = "[A-Za-z0-9][A-Za-z0-9._-]*";
const LOCATOR = "[A-Za-z0-9][A-Za-z0-9._/-]*";

function fail(message) {
  throw new Error(message);
}

function parseArgs(argv) {
  const args = {};

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];

    if (token === "--json") {
      args.json = true;
      continue;
    }

    if (!token.startsWith("--")) {
      fail(`unexpected argument: ${token}`);
    }

    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      fail(`missing value for ${token}`);
    }
    args[token.slice(2)] = value;
    index += 1;
  }

  for (const required of ["fixtures", "baseline", "candidate"]) {
    if (!args[required]) {
      fail(`missing required --${required}`);
    }
  }

  args.contract ??= DEFAULT_CONTRACT_PATH;

  return args;
}

function readExpectations(fixturesDir) {
  return readdirSync(fixturesDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(fixturesDir, entry.name))
    .sort()
    .filter((caseDir) => existsSync(path.join(caseDir, "expected.json")))
    .map((caseDir) => {
      const expected = JSON.parse(readFileSync(path.join(caseDir, "expected.json"), "utf8"));
      const runnerPath = path.join(caseDir, "runner-output.json");
      return {
        ...expected,
        runner_output: existsSync(runnerPath)
          ? JSON.parse(readFileSync(runnerPath, "utf8"))
          : undefined,
      };
    });
}

function parseTableRow(report, expected) {
  const header = [
    "평가 항목명",
    "최종 평점",
    "감점 이유",
    "검증된 근거 (Evidence)",
    "고득점 요건",
  ];
  const nonEmptyLines = report.split("\n").map((line) => line.trim()).filter(Boolean);
  if (
    nonEmptyLines.length !== 4
    || nonEmptyLines[0] !== "### [최종 평가 결과서]"
    || nonEmptyLines.slice(1).some((line) => !line.startsWith("|"))
  ) {
    fail("score report must contain only the fixed heading and one five-column table");
  }

  const rows = nonEmptyLines
    .filter((line) => line.trim().startsWith("|"))
    .map((line) => line.split("|").slice(1, -1).map((cell) => cell.trim()));
  const headers = rows.filter((cells) => (
    cells.length === header.length
    && cells.every((cell, index) => cell === header[index])
  ));
  if (headers.length !== 1) {
    fail("score report must contain the exact five-column header once");
  }

  const isSeparator = (cells) => (
    cells.length === header.length
    && cells.every((cell) => /^:?-{3,}:?$/.test(cell))
  );
  const separators = rows.filter(isSeparator);
  if (separators.length !== 1) {
    fail("score report must contain the five-column separator once");
  }
  const dataRows = rows.filter((cells) => cells !== headers[0] && cells !== separators[0]);
  if (dataRows.length !== 1 || dataRows[0].length !== header.length) {
    fail("score report must contain exactly one five-column data row for this fixture");
  }

  const row = dataRows[0];

  if (row[0] !== expected.dimension) {
    fail(`missing score row for dimension: ${expected.dimension}`);
  }

  const score = Number(row[1]);
  if (!Number.isInteger(score) || score < 0 || score > 100) {
    fail(`score must be an integer from 0 to 100 for dimension ${expected.dimension}`);
  }
  if (expected.criteria && row[4] !== expected.criteria) {
    fail(`high-score criteria changed for dimension ${expected.dimension}`);
  }
  if (score === 100 && (row[2] !== "" || row[3] !== "")) {
    fail(`a 100 score must have empty reason and evidence for dimension ${expected.dimension}`);
  }
  if (score < 100 && (row[2] === "" || row[3] === "")) {
    fail(`a deducted score must have reason and evidence for dimension ${expected.dimension}`);
  }

  return { dimension: row[0], score, reason: row[2], evidence: row[3], criteria: row[4] };
}

function readRuns(resultsDir, expectations) {
  const runDirs = readdirSync(resultsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && entry.name.startsWith("run-"))
    .map((entry) => path.join(resultsDir, entry.name))
    .sort();

  if (runDirs.length === 0) {
    fail(`no run-* directories under ${resultsDir}`);
  }

  return runDirs.map((runDir) => {
    const metricsPath = path.join(runDir, "metrics.json");
    return {
      run_id: path.basename(runDir),
      metrics: existsSync(metricsPath) ? JSON.parse(readFileSync(metricsPath, "utf8")) : undefined,
      cases: expectations.map((expected) => {
        const resultPath = path.join(runDir, `${expected.case_id}.md`);
        if (!existsSync(resultPath)) {
          fail(`missing result: ${resultPath}`);
        }
        const observed = parseTableRow(readFileSync(resultPath, "utf8"), expected);
        let adjudication;
        if (expected.truth === "DEFECT") {
          const adjudicationPath = path.join(runDir, `${expected.case_id}.adjudication.json`);
          if (!existsSync(adjudicationPath)) {
            fail(`missing blinded adjudication: ${adjudicationPath}`);
          }
          adjudication = JSON.parse(readFileSync(adjudicationPath, "utf8"));
          if (
            adjudication.schema_version !== 1
            || adjudication.case_id !== expected.case_id
            || adjudication.finding_id !== expected.finding?.id
            || typeof adjudication.retained !== "boolean"
            || typeof adjudication.rationale !== "string"
            || adjudication.rationale.length === 0
            || typeof adjudication.adjudicator_id !== "string"
            || adjudication.adjudicator_id.length === 0
          ) {
            fail(`invalid blinded adjudication: ${adjudicationPath}`);
          }
          if (adjudication.retained && observed.score === 100) {
            fail(`${adjudicationPath}: retained cannot be true when no deduction was accepted`);
          }
        }
        return { expected, observed, adjudication };
      }),
    };
  });
}

function scoreMatches(score, expectation) {
  if (!expectation) {
    return true;
  }

  switch (expectation.operator) {
    case "eq":
      return score === expectation.value;
    case "lt":
      return score < expectation.value;
    case "lte":
      return score <= expectation.value;
    case "gt":
      return score > expectation.value;
    case "gte":
      return score >= expectation.value;
    default:
      fail(`unsupported score operator: ${expectation.operator}`);
  }
}

function canonicalize(value) {
  if (Array.isArray(value)) {
    return value.map(canonicalize);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]),
    );
  }
  return value;
}

function parseEvidenceRefs(evidence) {
  const refs = [];
  const patterns = [
    new RegExp(`\\[(${ARTIFACT_ID})@(${LOCATOR})\\]\\s+"([^"|\\n]+)"`, "g"),
    new RegExp(`\\b(${ARTIFACT_ID})(?:\\((${LOCATOR})\\))?\\s*:\\s*"([^"|\\n]+)"`, "g"),
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(evidence)) !== null) {
      refs.push({
        artifact_id: match[1],
        locator: match[2] || undefined,
        quote: match[3],
      });
    }
  }
  return refs;
}

function evidenceIsValid(evidence, expected) {
  const refs = parseEvidenceRefs(evidence);
  if (refs.length === 0) {
    return false;
  }

  const artifacts = expected.runner_output?.artifacts ?? [];
  const refIsGrounded = (ref) => {
    const artifact = artifacts.find((item) => item.artifact_id === ref.artifact_id);
    return Boolean(
      artifact
      && (!ref.locator || artifact.locator === ref.locator)
      && typeof artifact.content === "string"
      && artifact.content.includes(ref.quote),
    );
  };
  if (!refs.every(refIsGrounded)) {
    return false;
  }

  return expected.required_evidence.every((required) => refs.some((ref) => (
    ref.artifact_id === required.artifact_id
    && (!ref.locator || ref.locator === required.locator)
    && ref.quote === required.quote
  )));
}

function resultFingerprint(observed, adjudication) {
  const normalize = (value) => String(value ?? "").trim().replace(/\s+/g, " ");
  return JSON.stringify({
    dimension: normalize(observed.dimension),
    score: observed.score,
    reason: normalize(observed.reason),
    evidence: normalize(observed.evidence),
    criteria: normalize(observed.criteria),
    retained_finding_id: adjudication?.retained ? adjudication.finding_id : null,
  });
}

function validateContract(contract) {
  if (contract.schema_version !== 1) {
    fail("comparison contract schema_version must be 1");
  }
  if (contract.runs_per_variant !== 3) {
    fail("comparison contract must require exactly 3 runs per variant");
  }
  if (contract.require_metrics !== true) {
    fail("comparison contract cannot disable required metrics");
  }
  if (contract.require_matching_execution !== true) {
    fail("comparison contract cannot disable matching execution metadata");
  }
}

function validateMetrics(run, variant) {
  if (!run.metrics) {
    fail(`${variant}/${run.run_id}: metrics.json is required`);
  }

  const { execution, cost } = run.metrics;
  if (
    !execution
    || typeof execution.model !== "string"
    || execution.model.length === 0
    || !execution.settings
    || typeof execution.settings !== "object"
    || Array.isArray(execution.settings)
    || typeof execution.tool_policy !== "string"
    || execution.tool_policy.length === 0
    || execution.clean_context !== true
  ) {
    fail(`${variant}/${run.run_id}: invalid execution metadata`);
  }

  for (const field of COST_METRICS) {
    if (!Number.isFinite(cost?.[field]) || cost[field] < 0) {
      fail(`${variant}/${run.run_id}: cost.${field} must be a non-negative number`);
    }
  }
}

function summarize(runs) {
  let falsePositives = 0;
  let falseNegatives = 0;
  let scoreContractErrors = 0;
  let gateErrors = 0;
  let evidenceErrors = 0;
  const failures = [];
  const fingerprintsByCase = new Map();

  for (const run of runs) {
    for (const { expected, observed, adjudication } of run.cases) {
      const errors = [];
      const fingerprints = fingerprintsByCase.get(expected.case_id) ?? [];
      fingerprints.push(resultFingerprint(observed, adjudication));
      fingerprintsByCase.set(expected.case_id, fingerprints);

      if (expected.truth === "NO_DEFECT" && observed.score < 100) {
        falsePositives += 1;
        errors.push("FALSE_POSITIVE");
      }
      if (!scoreMatches(observed.score, expected.score_expectation)) {
        scoreContractErrors += 1;
        errors.push("SCORE_CONTRACT");
      }

      const observedGate = observed.score >= 90 ? "SUCCESS" : "CONTINUE_TO_STAGE_4";
      if (expected.expected_gate && observedGate !== expected.expected_gate) {
        gateErrors += 1;
        errors.push("GATE");
      }

      const evidenceValid = observed.score < 100
        ? evidenceIsValid(observed.evidence, expected)
        : false;
      if (observed.score < 100) {
        if (!evidenceValid) {
          evidenceErrors += 1;
          errors.push("EVIDENCE");
        }
      }
      if (
        expected.truth === "DEFECT"
        && (
          !adjudication.retained
          || !evidenceValid
        )
      ) {
        falseNegatives += 1;
        errors.push("FALSE_NEGATIVE");
      }

      if (errors.length > 0) {
        failures.push({
          run_id: run.run_id,
          case_id: expected.case_id,
          errors,
        });
      }
    }
  }

  const unstableCases = [...fingerprintsByCase.values()]
    .filter((fingerprints) => new Set(fingerprints).size > 1)
    .length;
  const cost = {
    runs_with_metrics: runs.filter((run) => run.metrics).length,
  };
  for (const field of COST_METRICS) {
    cost[field] = runs.reduce((total, run) => {
      const value = run.metrics?.cost?.[field];
      return total + (typeof value === "number" ? value : 0);
    }, 0);
  }

  return {
    runs: runs.length,
    cases: runs.reduce((total, run) => total + run.cases.length, 0),
    false_positives: falsePositives,
    false_negatives: falseNegatives,
    score_contract_errors: scoreContractErrors,
    gate_errors: gateErrors,
    evidence_errors: evidenceErrors,
    unstable_cases: unstableCases,
    cost,
    failures,
  };
}

function compare(baseline, candidate) {
  const improved = BEHAVIOR_METRICS.some((metric) => candidate[metric] < baseline[metric]);
  const regressed = BEHAVIOR_METRICS.some((metric) => candidate[metric] > baseline[metric]);

  if (regressed) {
    return improved ? "INCONCLUSIVE" : "REGRESSED";
  }
  if (candidate.false_positives < baseline.false_positives) {
    return "IMPROVED";
  }
  return "NO_CHANGE";
}

function renderMarkdown(result) {
  const lines = [
    "# Scorer A/B Comparison",
    "",
    `Behavior verdict: ${result.behavior_verdict}`,
    "",
    "| behavior metric | baseline | candidate | delta |",
    "| --- | ---: | ---: | ---: |",
  ];

  for (const metric of BEHAVIOR_METRICS) {
    lines.push(
      `| ${metric} | ${result.baseline[metric]} | ${result.candidate[metric]} | ${result.candidate[metric] - result.baseline[metric]} |`,
    );
  }

  lines.push(
    "",
    "Cost is reported separately and does not change the behavior verdict until a budget is agreed.",
    "",
    "| cost metric | baseline | candidate | delta |",
    "| --- | ---: | ---: | ---: |",
  );
  for (const metric of COST_METRICS) {
    lines.push(
      `| ${metric} | ${result.baseline.cost[metric]} | ${result.candidate.cost[metric]} | ${result.candidate.cost[metric] - result.baseline.cost[metric]} |`,
    );
  }

  for (const variant of ["baseline", "candidate"]) {
    if (result[variant].failures.length === 0) {
      continue;
    }
    lines.push("", `## ${variant} failures`, "");
    for (const failure of result[variant].failures) {
      lines.push(`- ${failure.run_id}/${failure.case_id}: ${failure.errors.join(", ")}`);
    }
  }

  return `${lines.join("\n")}\n`;
}

const args = parseArgs(process.argv.slice(2));
const contract = JSON.parse(readFileSync(args.contract, "utf8"));
validateContract(contract);
const expectations = readExpectations(args.fixtures);
const baselineRuns = readRuns(args.baseline, expectations);
const candidateRuns = readRuns(args.candidate, expectations);
const adjudicatorIds = [...baselineRuns, ...candidateRuns]
  .flatMap((run) => run.cases)
  .map((item) => item.adjudication?.adjudicator_id)
  .filter(Boolean);
if (new Set(adjudicatorIds).size > 1) {
  fail("the same blinded adjudicator_id must be used for both variants");
}

if (Number.isInteger(contract.runs_per_variant)) {
  if (
    baselineRuns.length !== contract.runs_per_variant
    || candidateRuns.length !== contract.runs_per_variant
  ) {
    fail(`comparison contract requires ${contract.runs_per_variant} runs per variant`);
  }
}

if (contract.require_metrics) {
  for (const run of baselineRuns) {
    validateMetrics(run, "baseline");
  }
  for (const run of candidateRuns) {
    validateMetrics(run, "candidate");
  }
}

if (contract.require_matching_execution) {
  const executionKeys = [...baselineRuns, ...candidateRuns]
    .map((run) => JSON.stringify(canonicalize(run.metrics?.execution)));
  if (new Set(executionKeys).size !== 1) {
    fail("execution metadata must match across all baseline and candidate runs");
  }
}

const baseline = summarize(baselineRuns);
const candidate = summarize(candidateRuns);
const result = {
  behavior_verdict: compare(baseline, candidate),
  baseline,
  candidate,
};

if (args.json) {
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
} else {
  process.stdout.write(renderMarkdown(result));
}

#!/usr/bin/env node

import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";

const fixturesDir = path.resolve(process.argv[2] ?? new URL("./fixtures", import.meta.url).pathname);
const requiredRunnerFields = [
  "target_skill",
  "run_input",
  "artifacts",
  "exit_status",
  "errors",
  "notes",
];
const requiredFiles = [
  "final-rubric.md",
  "runner-output.json",
  "sub-scorers.json",
  "expected.json",
];
const requiredLenses = new Set(["omission", "distortion", "violation_excess"]);
const artifactIdPattern = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;
const locatorPattern = /^[A-Za-z0-9][A-Za-z0-9._/-]*$/;
const severities = new Set(["Critical", "Major", "Minor"]);

function fail(message) {
  throw new Error(message);
}

function readJson(filePath) {
  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch (error) {
    fail(`${filePath}: invalid JSON: ${error.message}`);
  }
}

function validateExpected(caseId, expected) {
  if (expected.case_id !== caseId) {
    fail(`${caseId}: expected.case_id must match the directory name`);
  }
  if (!expected.category || typeof expected.category !== "string") {
    fail(`${caseId}: expected.category must be a non-empty string`);
  }
  if (!expected.dimension || typeof expected.dimension !== "string") {
    fail(`${caseId}: expected.dimension must be a non-empty string`);
  }
  if (!expected.criteria || typeof expected.criteria !== "string") {
    fail(`${caseId}: expected.criteria must be a non-empty string`);
  }
  if (/[|\r\n]/.test(expected.dimension) || /[|\r\n]/.test(expected.criteria)) {
    fail(`${caseId}: dimension and criteria must fit in one unescaped Markdown table cell`);
  }
  if (!new Set(["DEFECT", "NO_DEFECT"]).has(expected.truth)) {
    fail(`${caseId}: expected.truth must be DEFECT or NO_DEFECT`);
  }
  if (
    !expected.score_expectation
    || !new Set(["eq", "lt", "lte", "gt", "gte"]).has(expected.score_expectation.operator)
    || !Number.isInteger(expected.score_expectation.value)
    || expected.score_expectation.value < 0
    || expected.score_expectation.value > 100
  ) {
    fail(`${caseId}: expected.score_expectation must carry an integer value from 0 to 100`);
  }
  if (!Array.isArray(expected.required_evidence)) {
    fail(`${caseId}: required_evidence must be an array`);
  }
  for (const ref of expected.required_evidence) {
    for (const field of ["artifact_id", "locator", "quote"]) {
      if (typeof ref[field] !== "string" || ref[field].length === 0) {
        fail(`${caseId}: every required evidence reference needs non-empty ${field}`);
      }
    }
    if (!artifactIdPattern.test(ref.artifact_id)) {
      fail(`${caseId}: invalid required evidence artifact_id ${ref.artifact_id}`);
    }
    if (!locatorPattern.test(ref.locator)) {
      fail(`${caseId}: invalid required evidence locator ${ref.locator}`);
    }
    if (/["|\r\n]/.test(ref.quote)) {
      fail(`${caseId}: evidence quotes cannot contain a quote, pipe, or newline`);
    }
  }
  if (expected.truth === "DEFECT" && expected.required_evidence.length === 0) {
    fail(`${caseId}: a true defect must name its required evidence`);
  }
  if (expected.truth === "DEFECT") {
    const finding = expected.finding;
    if (
      !finding
      || typeof finding.id !== "string"
      || !artifactIdPattern.test(finding.id)
      || typeof finding.definition !== "string"
      || finding.definition.length === 0
    ) {
      fail(`${caseId}: a true defect needs a stable finding id and definition`);
    }
  }
  if (expected.truth === "NO_DEFECT" && expected.required_evidence.length !== 0) {
    fail(`${caseId}: a no-defect case cannot require accepted-deduction evidence`);
  }
  if (expected.truth === "NO_DEFECT" && expected.finding !== undefined) {
    fail(`${caseId}: a no-defect case cannot declare an oracle finding`);
  }
}

function validateRunner(caseId, runner) {
  for (const field of requiredRunnerFields) {
    if (!Object.hasOwn(runner, field)) {
      fail(`${caseId}: RUNNER_OUTPUT missing ${field}`);
    }
  }
  if (!Array.isArray(runner.artifacts)) {
    fail(`${caseId}: RUNNER_OUTPUT.artifacts must be an array`);
  }

  const artifactIds = new Set();
  for (const artifact of runner.artifacts) {
    for (const field of ["artifact_id", "kind", "locator", "content"]) {
      if (typeof artifact[field] !== "string" || artifact[field].length === 0) {
        fail(`${caseId}: every artifact must carry non-empty ${field}`);
      }
    }
    if (artifactIds.has(artifact.artifact_id)) {
      fail(`${caseId}: duplicate artifact_id ${artifact.artifact_id}`);
    }
    if (!artifactIdPattern.test(artifact.artifact_id)) {
      fail(`${caseId}: invalid artifact_id ${artifact.artifact_id}`);
    }
    if (!locatorPattern.test(artifact.locator)) {
      fail(`${caseId}: invalid artifact locator ${artifact.locator}`);
    }
    artifactIds.add(artifact.artifact_id);
  }
}

function validateSubScorers(caseId, dimension, subScorers) {
  if (!Array.isArray(subScorers) || subScorers.length !== 3) {
    fail(`${caseId}: sub-scorers.json must contain exactly three fixed lens outputs`);
  }
  const lensNames = subScorers.map((entry) => entry?.sub_scorer);
  if (
    new Set(lensNames).size !== requiredLenses.size
    || lensNames.some((lens) => !requiredLenses.has(lens))
  ) {
    fail(`${caseId}: fixed lenses must be omission, distortion, and violation_excess exactly once`);
  }

  for (const entry of subScorers) {
    const evaluation = entry?.output?.evaluation;
    if (!Array.isArray(evaluation)) {
      fail(`${caseId}: ${entry?.sub_scorer ?? "unknown"} missing evaluation array`);
    }
    const matches = evaluation.filter((item) => item.dimension === dimension);
    if (matches.length !== 1) {
      fail(`${caseId}: each sub-scorer must score ${dimension} exactly once`);
    }

    const item = matches[0];
    if (
      !Array.isArray(item.deductions)
      || !Number.isInteger(item.score)
      || item.score < 0
      || item.score > 100
    ) {
      fail(`${caseId}: invalid score or deductions for ${entry.sub_scorer}`);
    }
    const penalty = item.deductions.reduce((total, deduction) => {
      if (!Number.isInteger(deduction.penalty_points) || deduction.penalty_points <= 0) {
        fail(`${caseId}: every deduction needs positive integer penalty_points`);
      }
      if (!severities.has(deduction.severity)) {
        fail(`${caseId}: every deduction needs a recognized severity`);
      }
      for (const field of ["severity", "reason", "evidence"]) {
        if (typeof deduction[field] !== "string" || deduction[field].length === 0) {
          fail(`${caseId}: every deduction needs non-empty ${field}`);
        }
      }
      return total + deduction.penalty_points;
    }, 0);
    if (item.score !== Math.max(0, 100 - penalty)) {
      fail(`${caseId}: ${entry.sub_scorer} score does not equal 100 minus its deductions`);
    }
  }
}

if (!existsSync(fixturesDir)) {
  fail(`fixtures directory does not exist: ${fixturesDir}`);
}

const caseDirs = readdirSync(fixturesDir, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();

if (caseDirs.length === 0) {
  fail(`no fixture cases under ${fixturesDir}`);
}

const seenCategories = new Set();
const seenFindingIds = new Set();
for (const caseId of caseDirs) {
  const caseDir = path.join(fixturesDir, caseId);
  for (const fileName of requiredFiles) {
    if (!existsSync(path.join(caseDir, fileName))) {
      fail(`${caseId}: missing ${fileName}`);
    }
  }

  const expected = readJson(path.join(caseDir, "expected.json"));
  const runner = readJson(path.join(caseDir, "runner-output.json"));
  const subScorers = readJson(path.join(caseDir, "sub-scorers.json"));
  const rubric = readFileSync(path.join(caseDir, "final-rubric.md"), "utf8");

  validateExpected(caseId, expected);
  validateRunner(caseId, runner);
  validateSubScorers(caseId, expected.dimension, subScorers);

  if (!rubric.includes(`| ${expected.dimension} | ${expected.criteria} |`)) {
    fail(`${caseId}: final rubric does not contain the expected dimension and criteria verbatim`);
  }
  if (seenCategories.has(expected.category)) {
    fail(`${caseId}: duplicate fixture category ${expected.category}`);
  }
  seenCategories.add(expected.category);
  if (expected.finding) {
    if (seenFindingIds.has(expected.finding.id)) {
      fail(`${caseId}: duplicate oracle finding id ${expected.finding.id}`);
    }
    seenFindingIds.add(expected.finding.id);
  }

  for (const ref of expected.required_evidence) {
    const artifact = runner.artifacts.find((item) => item.artifact_id === ref.artifact_id);
    if (!artifact) {
      fail(`${caseId}: required evidence names unknown artifact ${ref.artifact_id}`);
    }
    if (artifact.locator !== ref.locator) {
      fail(`${caseId}: required evidence locator does not match ${ref.artifact_id}`);
    }
    if (!artifact.content.includes(ref.quote)) {
      fail(`${caseId}: required evidence quote is absent from ${ref.artifact_id}`);
    }
  }
}

process.stdout.write(`OK: ${caseDirs.length} scorer comparison fixtures are valid\n`);

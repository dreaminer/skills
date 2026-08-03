#!/usr/bin/env node

import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

const caseId = process.argv[2];
if (!caseId || caseId.includes("/") || caseId.includes("..")) {
  throw new Error("usage: node scorer/tests/render-case.mjs <case-id>");
}

const caseDir = new URL(`./fixtures/${caseId}/`, import.meta.url).pathname;
const files = {
  FINAL_RUBRIC: "final-rubric.md",
  RUNNER_OUTPUT: "runner-output.json",
  SUB_SCORERS_OUTPUTS: "sub-scorers.json",
};

for (const fileName of Object.values(files)) {
  if (!existsSync(path.join(caseDir, fileName))) {
    throw new Error(`unknown or incomplete fixture: ${caseId}`);
  }
}

const blocks = [
  "# Fixed Scorer Comparison Input",
  "",
  `Case: ${caseId}`,
  "",
];

for (const [label, fileName] of Object.entries(files)) {
  const language = fileName.endsWith(".json") ? "json" : "md";
  blocks.push(
    `## ${label}`,
    "",
    `\`\`\`${language}`,
    readFileSync(path.join(caseDir, fileName), "utf8").trimEnd(),
    "```",
    "",
  );
}

process.stdout.write(`${blocks.join("\n").trimEnd()}\n`);

---
name: explain-flows
disable-model-invocation: true
description: Derive a compact project-flow guide from project tests qualified by a ready TEST_FLOWS_RESULT.md. Use only when the user explicitly invokes `$explain-flows`, `/explain-flows`, or asks to run the `explain-flows` skill by name to create or refresh QUICK_UNDERSTANDING.md; do not add or modify tests, configuration, or production code.
---

# Explain Flows

Create `<target-project>/docs/QUICK_UNDERSTANDING.md`, unless the human names another
documentation directory inside that project. Derive every statement from existing passing,
regression-effective tests listed in that project's ready `TEST_FLOWS_RESULT.md`.

Treat tests as evidence of code-observed behavior, including existing quirks. They do not prove
business intent.

## Protect the read-only evidence boundary

Read source, tests, configuration, `TEST_FLOWS_RESULT.md`, and existing documentation as needed. Run
non-mutating discovery, test, build, typecheck, and lint commands. Create or update only the resolved
`QUICK_UNDERSTANDING.md`; never create or refresh the Test Flows result.

Do not add or strengthen tests, install dependencies, change test configuration, or modify production
code. When evidence is insufficient, report `EVIDENCE_GAPS`; do not invoke another skill or expand
write scope without separate human authorization.

## 1. Resolve the target, scope, and maintained test commands

Resolve the target project root from the human's request and repository structure. In a monorepo,
use the named product or package; if several product roots remain equally plausible, ask one direct
question before writing.

Resolve:

- **Document:** `<target-project>/docs/QUICK_UNDERSTANDING.md` by default;
- **Result:** prefer `<target-project>/docs/TEST_FLOWS_RESULT.md`; if absent, search the target
  project for that exact filename and use the only match; ask one direct path question when several
  matches remain;
- **Scope:** use the human's named scope when the result covers it, otherwise inherit the result's
  `Scope`; a requested scope outside the ready result is an evidence gap;
- **Evidence:** project-owned tests and final test-verification commands listed by the result.

Consume the installed test stack. Do not ask the human to choose a framework because this skill does
not create tests.

Require an exact `Status` section containing `- FLOW_TESTS_READY`. If the result is missing or not
ready, return `EVIDENCE_GAPS` with `Document changed: no`; do not reconstruct Test Flows'
qualification work.

This step is complete when the target, scope, document path, and maintained commands are explicit and
the document path is inside the target project.

## 2. Establish the observed baseline and map candidate flows

Run the result's final test-verification commands before editing and record failures. Also run any normal
relevant command required by the repository but omitted from the receipt. A failing test cannot
support a document claim.

Inventory the in-scope public entry points. Trace domain-bearing entry points through the decisions,
state and persistence transitions, outgoing effects, and existing tests that observe their outcomes.
Classify supporting or purely technical entry points without turning them into domain scenarios.

Map each actor goal or automatic trigger as:

`starting domain facts → action or trigger → decisions and invariants → state/effects → actor-visible outcome`

Classify candidate tests internally:

- **Process evidence:** crosses real orchestration from starting facts to a final domain outcome.
- **Invariant evidence:** distinguishes meaningful alternatives of a domain rule or lifecycle
  constraint.
- **Technical regression:** protects an implementation concern without explaining a domain outcome
  by itself.

Technical regression tests cannot support a document line by themselves.

This step is complete when every in-scope entry point belongs to a named candidate process or an
evidenced technical/supporting role, and every code-observed decision that changes a domain outcome is
visible in the map.

## 3. Read the qualified evidence

A result-listed test supports the guide only when it still has both forms of fitness:

- **Story fitness:** a reader can recover domain facts, one actor action or automatic trigger, and the
  resulting domain outcome.
- **Regression fitness:** a plausible defect changes a relevant assertion.

For each candidate process or invariant:

1. run the narrow maintained command that discovers the test;
2. identify the exact assertion that observes the domain result or contract effect;
3. inspect the reached production decision;
4. confirm the scenario still expresses starting facts, one trigger, and the observed result recorded
   by Test Flows;
5. classify the scenario as process evidence, invariant evidence, or technical regression.

Treat `FLOW_TESTS_READY` as Test Flows' regression-fitness receipt. Do not rerun mutations or require
a separate red-proof handoff. Exclude missing, failing, unexecutable, or purely technical scenarios
from the guide and report them as evidence gaps. Never repair the gap in this skill.

Maintain an internal trace:

| Evidence scenario | Kind | Domain result | Relevant assertion | Production decision | Result status |
|---|---|---|---|---|---|
| `<test>` | `process/invariant` | `<result>` | `<observation>` | `<decision>` | `FLOW_TESTS_READY` |

This step is complete when every candidate claim has passing result-listed evidence or is explicitly
excluded as a gap.

## 4. Close the in-scope story

Audit the process map against production code and qualified evidence. Every meaningful intermediate
state, durable effect, and domain-changing alternative must reach one of:

- an evidenced continuation;
- an evidenced terminal outcome;
- an `EVIDENCE_GAPS` entry.

Report each gap as:

`**<process or invariant>** — Missing evidence: <untested decision/outcome> | Needed observation: <result or effect a test must expose>`

Do not invent the intended outcome of behavior absent from production code. If a gap prevents a
coherent main flow or leaves an in-scope domain-changing branch unsupported, do not create or replace
the final document. Keep any existing document untouched and hand off the gaps. A narrower scope is
valid only when the human explicitly selected it.

If any in-scope evidence gap remains:

1. do not create or replace the resolved document;
2. return `EVIDENCE_GAPS` with the resolved scope and document path, every missing decision or
   outcome, the observation needed to close it, the non-ready result or failing scenario, commands
   run and baseline result, and `Document changed: no`;
3. stop. This is a completed evidence-gap outcome.

Continue to step 5 only when qualified evidence closes the entire in-scope story.

## 5. Derive the compact guide

Create the resolved document with this shape:

```markdown
# QUICK UNDERSTANDING

<One sentence: who moves what from which starting condition to which final outcome.>

## Main flow

1. **<stage>**
    - [G] <domain facts>.
    - [W] <one action or trigger>.
    - [T] <domain outcome and contract effects>.

## Critical branches

- **<rule or branch>**
    - [G] <domain facts>.
    - [W] <one action or trigger>.
    - [T] <alternate outcome and effects>.
```

Give each scenario one title line followed immediately by three indented list lines: `[G]`, `[W]`,
then `[T]`, exactly once and in that order. Keep each label and its content on one physical line.
Order the main flow so each result prepares the next scenario. Include only branches that change how
a reader predicts the outcome. Join multiple Then effects with semicolons.

Keep test names, file paths, links, commands, counts, coverage data, evidence matrices, technical
variations, suspicions, proposals, and inferred flows out of the document. One scenario may compress
several tests, but every clause must trace to qualified evidence.

This step is complete when a reader can predict the main outcomes in one scan and every scenario is
code-observed, passing, and regression-relevant.

## 6. Verify and hand off

Reach this step only after step 4 confirms `Evidence gaps: none`.

Rerun the selected evidence tests and the normal relevant test command after writing. Compare with the
baseline and separate pre-existing failures from introduced failures. Confirm that only the resolved
document changed and that every document clause still maps to the internal trace.

Hand off only:

- the resolved scope and document path;
- the Test Flows result path and `FLOW_TESTS_READY` status;
- domain processes and invariants represented;
- evidence test files used;
- commands run and baseline-versus-final result;
- `Evidence gaps: none`.

The skill completes in exactly one of two terminal outcomes:

- `GUIDE_WRITTEN`: the compact guide is inside the target project, every claim derives from existing
  passing evidence with regression fitness, normal tests remain intact, only the resolved document
  changed, and `Evidence gaps: none`;
- `EVIDENCE_GAPS`: the existing document remains untouched and every blocking evidence gap is handed
  off with the observation needed to close it.

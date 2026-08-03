# Test Flows result contract

## Role and ownership

Write one regenerable verification receipt after executing the target project's maintained test
commands. Test Flows owns this file. Explain Flows and Make Body may read it but never modify it.

The receipt is not a second description of System behavior. Project-owned tests remain the
executable authority, and `QUICK_UNDERSTANDING.md` remains the optional explanation.

## Default path

Use `<target-project>/docs/TEST_FLOWS_RESULT.md` unless the human selected another documentation
directory inside the target project.

Replace an existing receipt after every completed verification attempt so an old ready result cannot
survive a newer failure.

## Status

- `FLOW_TESTS_READY`: every listed evidence scenario has story fitness, executable red proof, and
  passing final verification, and the resolved scope has no flow-gap proposal.
- `FLOW_TESTS_NOT_READY`: at least one scenario is ineffective or unverified, a required command
  failed or could not run, or another blocker prevents a ready evidence set.

Only `FLOW_TESTS_READY` is consumable evidence for downstream skills.

## Template

```md
# TEST_FLOWS_RESULT

Status:
- FLOW_TESTS_READY

Scope:
- <resolved product or behavior scope>

Test root:
- `<project-relative test root>`

Evidence tests:
- `<project-relative test path>` — <process or invariant and observed result>.

Final test verification:
- `<maintained command>` — exit `0`; <concise passed/failed summary>.

Regression fitness:
- <scenario> — red proof executed; <defect hypothesis>; <relevant failing assertion>.

Flow-gap proposals:
- none
```

For a not-ready result, keep the same headings, set `Status` to `FLOW_TESTS_NOT_READY`, and record the
actual command results under `Final test verification`, including exit `0` when tests passed but a
non-command blocker remains. State an unverified scenario under `Regression fitness`. Put any
in-scope open edge under `Flow-gap proposals`; a nonempty proposal list cannot accompany
`FLOW_TESTS_READY`. Do not invent counts that the runner did not report.

Use project-relative paths. Record the selected evidence commands and the normal full test command
exactly as executed. Keep build, typecheck, and lint outcomes in the human handoff rather than this
test receipt. Summarize results; do not embed raw logs, test source, Given/When/Then prose, or
business interpretation.

# Dreaminer Skills

Installable agent skill collection.

For a code-free project, use `seed-body` to ratify the Essential body and then `seed-system` to prepare Acceptance and implementation design. For an existing implementation, use `test-flows` to establish executable flow tests plus a `TEST_FLOWS_RESULT.md` verification receipt, then use `explain-flows` and `make-body` to consume that evidence without repeating regression proof. Essential language always requires human ratification; automated ratification wrappers are not packaged. `explain-flows` derives a compact Given/When/Then walkthrough without modifying tests. `proposal-review` gates standalone proposed skill edits against the target skill's job, evidence, cost, and before/after behavior. `skill-auditor` verifies whether an agent skill has predictable triggers, structure, steering, pruning, and validation evidence. `criteria-opt` orchestrates a rubric-first skill improvement loop: `rubricator` freezes a deduction-scoring rubric from the target objective, a system Runner captures current behavior, `scorer` audits the run capsule by deduction-only cross-validated sub-scorers, a deterministic Judger gates the loop, `proposer` synthesizes one exact-match edit proposal from strategy-differentiated sub-proposals, and a mechanical Rebuilder applies it all-or-nothing.

Runtime note: `make-body` requires Python 3.10+ as `python3` and POSIX `sh`. It uses only the Python
standard library; no `pip install` is required.

## Install

After pushing this directory to GitHub:

```sh
npx skills@latest add dreaminer/skills
```

The installer reads `.claude-plugin/plugin.json` and installs the skill folders listed there.

## Contents

```text
.claude-plugin/plugin.json
seed-body/SKILL.md
seed-system/SKILL.md
make-body/SKILL.md
test-flows/SKILL.md
test-flows/references/result-contract.md
explain-flows/SKILL.md
proposal-review/SKILL.md
skill-auditor/SKILL.md
skill-auditor/references/great-skill-checklist.md
criteria-opt/SKILL.md
criteria-opt/references/rebuilder-stage.md
rubricator/SKILL.md
rubricator/references/rubricator-prompts.md
scorer/SKILL.md
scorer/references/scorer-prompts.md
proposer/SKILL.md
proposer/references/proposer-prompts.md
```

## Validate

```sh
bun run validate
bun pm pack --dry-run
```

`bun run validate` checks that the plugin manifest points at packaged skill folders with valid `SKILL.md` frontmatter.

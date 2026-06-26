# Dreaminer Skills

Installable agent skill collection.

`body-shaping` recovers a project's ubiquitous language and use cases into confirmed Essential/System domain documents. `body-auto-shaping`, `auto-body-shaping`, and `yolo-body-shaping` provide progressively more automated review loops over that body. `make-body` reconstructs a code-observed System body first, then derives human-confirmed Essential language from a code-only project. `proposal-review` gates proposed skill edits against the target skill's job, evidence, cost, and before/after behavior.

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
body-shaping/SKILL.md
body-shaping/DESIGN.md
body-shaping/references/document-templates.md
body-shaping/scripts/check-body.sh
body-auto-shaping/SKILL.md
auto-body-shaping/SKILL.md
yolo-body-shaping/SKILL.md
make-body/SKILL.md
proposal-review/SKILL.md
```

`body-shaping/DESIGN.md` is maintainer rationale. It is not linked from `SKILL.md`, so agents do not load it during normal skill use.

## Validate

```sh
npm run validate
npm run pack:dry-run
```

`npm run validate` checks that the plugin manifest points at packaged skill folders with valid `SKILL.md` frontmatter.

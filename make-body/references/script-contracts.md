# Script contracts

The R6 script layer is intentionally small.

## `preflight.py`

Check Python 3.10+ and report that no third-party package is required. Never install anything.

## `init-docs.py <docs-dir>`

Create only missing R6 managed files. Preserve every existing file and print `CREATED` or
`PRESERVED` for each managed path.

## `check-body.sh <docs-dir>`

Validate the two canonical Essential files:

- exact document titles and canonical `## [Subject]` headers;
- Domain `Meaning` and UseCase `Given/When/Then` sections;
- at least one `Human-ratified:` Evidence line per entry;
- no `{candidate}` leakage;
- every UseCase `[Term]` resolves in `ESSENTIAL_DOMAIN.md`.

An empty canonical file with only its title is valid before ratification.

## `check-workspace.py <project-root> <docs-dir>`

Require the project and docs directories, invoke `check-body.sh`, and structurally validate conflict,
rejection, and hypothesis files. Do not inspect, execute, link, or score tests.

## `report-status.py <docs-dir>`

Print counts for canonical Domain and UseCase entries, hypothesis statuses, conflicts, rejections,
and every managed output path. Counts never decide meaning.

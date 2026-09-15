# Seed UI review resume regression

Date: 2026-09-15. Reported target: `~/repo/project/inperson/message`.

## Symptom and boundary

The user requested UI-contract review through seed-loop, but received completion and a description
of installed UI rules instead of evidence of a current contract review. The global Seed skill files
matched the repository, excluding a stale installation as the immediate explanation.

Read-only inspection of the target's current files found canonical AC-068 through AC-072 and
browser lifecycle records MT-068 through MT-072. Their notes describe a later user request to promote
UI contracts. Those current files do not establish what existed at the earlier completion, and their
GREEN notes are not a browser run performed during this diagnosis. No target-project files were edited.

## Minimal reproduction

1. Copy `seed-tdd/tests/fixtures/project` into an isolated temporary project.
2. Append a Delivery clause to `docs/ESSENTIAL_USECASE.md`: the customer creates an Order through
   the delivered web screen and sees its ID there. Leave its subject unchanged.
3. Set the fixture's implementation proposal status to deferred, leaving no realization work.
4. Run `seed-system/scripts/check-acceptance.py --docs docs --complete all` from the fixture root.

Observed: exit 0, one AC, zero non-deferred IPs, no failures or warnings. The AC still names the
Order creation API; there is no screen AC. This reproduces the known structural coverage boundary,
not a defect in the checker's declared contract.

An independent agent then applied the pre-fix seed-loop instructions to that fixture and the request
`$seed-loop <fixture> UI 계약이 빠진 게 없는지 검토해줘. 변경은 아직 하지 마.`
The replay assumed the general full suite and repository checks had passed unchanged in that run.
Its selected terminal was `SEED_LOOP_COMPLETE` under selection rule 6. No review-before-completion
route existed. No downstream implementation or real browser run was part of this routing replay.

## Correction and verification scope

Selection rule 2 routes an existing-project start/resume through seed-system's current contract
review. Rule 4 includes explicitly requested behavior rechecks even when lifecycle records are GREEN.
Evidence is reusable within the invocation while inputs and requested scope remain unchanged.
The existing owners keep contract ratification, behavioral evidence, and inspection-only boundaries.

Existing repository regressions, the three edited skills' frontmatter validators, and package dry-run
passed. Routing replays exercise agent decisions; these checks do not prove UI completeness or replace
execution against a real application's browser interface.

A fresh independent replay of the updated instructions selected seed-system first for ordinary
resume, explicit read-only UI-contract review, and requested UI behavior recheck. It identified the
fixture's missing screen AC. After a hypothetical clean current contract review with relevant UI ACs
GREEN, the requested behavior recheck selected seed-tdd for fresh evidence rather than completion.

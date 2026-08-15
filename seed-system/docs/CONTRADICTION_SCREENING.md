# Contradiction screening — 2026-08-15 diet

Self-play mechanical screening of the rewritten seed-system instructions. This is **not a trace**:
it proves only that the instruction chain is free of literal contradictions and broken mechanics.
It is not evidence that the conversation rules produce good sessions — that requires one real
seed-system conversation on a real project, which remains the open completion condition
(`DESIGN.md` § 검증 상태). Not packaged (`package.json` excludes `*/docs`).

- Date: 2026-08-15
- Input: post-diet `SKILL.md`, `references/artifacts.md`, `DESIGN.md`;
  `scripts/check-acceptance.py` byte-identical to pre-diet
- Method: literal walk of the `SKILL.md` instruction chain checking that every step's
  preconditions are producible by prior steps, plus mechanical greps and fixture runs

## Held

- No references to the deleted `references/conversation-loop.md` / `references/closing-gate.md`
  remain anywhere in `seed-system/`. The retired working-file names
  (`SEED_SYSTEM_FLOWS/PRIOR/HARVEST/CANDIDATES/CRITERIA/LATER/QUESTIONS/REJECTED`) appear nowhere
  in the repository.
- Script unchanged: `git diff` empty for `scripts/`; the fixture contract hash pinned by
  `seed-tdd/tests/run.sh` (`9840a2ed…`) still matches; `check-acceptance.py --complete` reports
  0 failures on the fixture; `contract-markers.py` prints the identical marker.
  `bun run validate` passes end to end, including the new `disable-model-invocation` frontmatter.
- Handoff ordering has no D1-style trap: at handoff time every `SEED_SYSTEM_TESTS.md` record is
  `gap — test harness not created yet`, gap records need no `Test`/`Marker` fields (the checker
  skips them), so seed-system never has to compute a contract hash itself. Hashes first become
  load-bearing inside `$seed-tdd`, whose `contract-markers.py` derives them from the canonical
  checker.
- Checker timing cannot exit 2 mid-conversation: the verification rule fires only "before
  presenting materialized output, and after any edit to a materialized `ACCEPTANCE.md`" — staged
  scratch candidates never trigger a run against a nonexistent `docs/ACCEPTANCE.md`. (This wording
  was chosen during the rewrite after the naive "after any Acceptance edit" was caught implying a
  guaranteed exit-2 during staging.)
- `$seed-tdd` interop intact: its Step 1 requires `ESSENTIAL_DOMAIN` + `ACCEPTANCE` +
  `IMPL_PROPOSAL` + `TESTS`, all still materialized; Risk/Layer/Seam/test command/test directory
  all still have schema owners in `artifacts.md`.

## Observed — parked, not screening failures

- **Coverage hard-FAIL on a deliberately deferred use case.** Executed evidence from 2026-08-15
  review: an `ESSENTIAL_USECASE.md` entry intentionally deferred from v1 (`[Cancel Order]`) makes
  `check-acceptance.py` FAIL even without `--complete`, blocking the `$seed-tdd` Step 1 gate.
  Changing the script was outside the ratified diet scope (script behavior frozen). Parked as a
  demotion candidate (FAIL → WARN without `--complete`) awaiting user ratification, with this
  reproduction as its evidence.
- **Identity principle 7 vs the mixed-mode gate.** The principle (publish no System canonical) and
  the script-enforced mixed-mode rejection coexist in `SKILL.md`. Recorded as two facts —
  judgment principle vs mechanical gate — not an ownership-map duplication.

## Verdict

No mechanical contradictions in the post-diet instruction set. Prose reduced 956 → 465 lines.
The conversation path stays unverified until one real session; per the edit gates, no new musts
before that trace.

# Greenfield execution trace

One end-to-end run of `seed-tdd` against a real, runnable greenfield project, following `SKILL.md`
literally to surface instruction defects. Not packaged (`package.json` excludes `*/docs`).

- Date: 2026-08-14
- Project: throwaway reading-list service, `python3` + stdlib `unittest`, 3 ACs
- Handoff input: `ESSENTIAL_DOMAIN.md`, `ACCEPTANCE.md`, `SEED_SYSTEM_IMPL_PROPOSAL.md`
  (IP-001..003 accepted, IP-004 deferred), `SEED_SYSTEM_TESTS.md` with all three records at
  `gap — test harness not created yet`
- Outcome: `gap -> RED -> GREEN -> COMPLETE` reached; completion gate passed with 0 failures

## What held

- Step 1 established the handoff: the checker passed on the untouched handoff, and the declared
  command failing with `ImportError: Start directory is not importable` matched the recorded
  `gap — test harness not created yet`, so the baseline was recorded `not yet runnable`.
- Step 2 selection order resolved without hesitation, and `contract-markers.py` output plus the two
  documents supplied every field the selection gate names.
- The seed-system checker passed at every lifecycle transition and at `--complete`.
- Step 5 proposal mapping worked as written: IP-001..003 mapped to code and test evidence, IP-004
  (`Status: deferred`) and IP-003's `Deferred values` were excluded without ambiguity.
- The `PREEXISTING_GREEN` procedure executed exactly as written. Mutating `Entry.is_read = False`
  to `True` inside an `mktemp -d` copy failed AC-003 at its intended `Then` assertion
  (`AssertionError: True is not false`); the working tree stayed untouched and reran GREEN after the
  scratch copy was discarded.

## Defects found

### D1 — the first slice has no legal path to RED

The first test fails with `ModuleNotFoundError: No module named 'readinglist.service'`. `SKILL.md`
classifies import failures as concrete gaps, and clearing the gap means creating the production
seam — but the same step ends with "Production implementation begins only after this criterion
holds". Read literally, slice 1 cannot leave `gap`.

### D2 — the RED definition forces throwaway production code, on every slice

"Reserve `red` for an executable assertion failure" excludes the honest greenfield failure. Observed
on the same test:

```
raise NotImplementedError      -> ERROR   NotImplementedError                  (not red, per rule)
return Entry(None, None)       -> FAIL    AssertionError: unexpectedly None    (red)
```

The rule rewards the second, which is production code written solely to convert an ERROR into a
FAIL, and which carries strictly less information about the missing behavior than the first.

This is not a bootstrap-only problem. AC-002 hit it again on an existing module:
`AttributeError: 'ReadingListService' object has no attribute 'mark_read'` is an ERROR, so a
do-nothing `mark_read` had to be written before RED could be recorded. Every new seam operation
repeats this.

Resolved by broadening RED (see Resolution below).

### D3 — "unmodified baseline" carries two meanings

Step 1 fixes it at handoff time. `references/test-quality.md` step 2 of `UNEXPECTED_GREEN` asks
whether the behavior "was already present in the unmodified baseline". After slice 1 these diverge:
AC-003's behavior did not exist at the handoff baseline, it arrived as a side effect of the AC-002
slice. The phrase needs to name the pre-slice tree, not the handoff baseline.

### D4 — the declared full suite is not runnable as declared

`SEED_SYSTEM_TESTS.md` declared `python3 -m unittest discover -s tests/acceptance`. Verbatim it
reports `FAILED (errors=3)`; the suite only runs as
`PYTHONPATH=src python3 -m unittest discover -s tests/acceptance -t .`. Step 5 says to run the
declared full suite, and Authority restricts `SEED_SYSTEM_TESTS.md` writes to lifecycle fields, so
`Test command:` cannot be corrected from inside seed-tdd. The skill needs a stated route for a
declared command that does not run.

## Resolution

All four were fixed the same day.

- **D2** — RED now means "the failure shows the selected behavior is absent", satisfied either by a
  `Then`-derived assertion failure or by the declared `Seam` itself being missing where the test
  reaches for it. Import failures *outside* the selected seam stay gaps. Both documents now forbid
  adding behavior-free production code to convert a missing seam into an assertion failure.
- **D1** — dissolved by D2. The first slice's `ModuleNotFoundError` on the seam is now RED, so no
  production code is needed before RED and the Step 3 ordering rule holds.
- **D3** — `UNEXPECTED_GREEN` step 2 now names the pre-slice tree and says outright that after the
  first slice this is no longer the handoff baseline.
- **D4** — Step 3 now requires building the harness so the declared command runs as written, and
  routes a command that cannot be made to run to `$seed-system` instead of amending it.

Replayed against the corrected rules, with the package at the project root so the declared command
runs verbatim:

```
slice 1  ModuleNotFoundError: No module named 'readinglist.service'   -> RED, no stub
         implement save()                                             -> OK
slice 2  AttributeError: ... has no attribute 'mark_read'             -> RED, no stub
         implement mark_read()/entry()                                -> OK
```

Zero throwaway stubs across both slices, which was the defect.

## Reproduction

The trace project was disposable. The sequence, in order:

```sh
python3 <seed-system-skill>/scripts/check-acceptance.py --docs docs        # Step 1 gate
python3 <seed-tdd-skill>/scripts/contract-markers.py --docs docs           # Step 2 markers
PYTHONPATH=src python3 -m unittest discover -s tests/acceptance -t .       # Step 3/4 suite
python3 <seed-system-skill>/scripts/check-acceptance.py --docs docs --complete   # Step 5 gate
```

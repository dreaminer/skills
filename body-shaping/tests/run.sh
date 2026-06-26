#!/usr/bin/env sh
# body-shaping: contract regression tests for the four shell scripts.
#
# Pins ONLY the public contract that SKILL.md depends on -- exit code, stdout,
# stderr -- exercised over small static docs fixtures under tests/fixtures/.
# It deliberately does NOT assert awk expressions, internal helpers, or line
# counts, so a script may be reimplemented in another language and still pass
# as long as its observable behaviour is unchanged.
#
# Usage: sh tests/run.sh        (exit 0 = all pass, 1 = at least one failure)
set -u

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SCRIPTS="$HERE/../scripts"
FIX="$HERE/fixtures"

pass=0
fail=0
ok()  { pass=$((pass + 1)); printf 'ok   - %s\n' "$1"; }
bad() { fail=$((fail + 1)); printf 'FAIL - %s\n' "$1"; }

# run <script> <docsdir>  ->  sets RC, OUT, ERR
run() {
  _errf="$HERE/.stderr.$$"
  OUT=$(sh "$SCRIPTS/$1" "$2" 2>"$_errf"); RC=$?
  ERR=$(cat "$_errf"); rm -f "$_errf"
}

# run_question <docsdir> <qid>
run_question() {
  _errf="$HERE/.stderr.$$"
  OUT=$(sh "$SCRIPTS/check-question.sh" "$1" "$2" 2>"$_errf"); RC=$?
  ERR=$(cat "$_errf"); rm -f "$_errf"
}

rc_is()   { if [ "$RC" = "$2" ];    then ok "$1"; else bad "$1 [exit=$RC want=$2 | out=<$OUT> err=<$ERR>]"; fi; }
out_eq()  { if [ "$OUT" = "$2" ];   then ok "$1"; else bad "$1 [out=<$OUT> want=<$2>]"; fi; }
out_has() { case "$OUT" in *"$2"*)  ok "$1";; *)   bad "$1 [out=<$OUT> missing=<$2>]";; esac; }
err_has() { case "$ERR" in *"$2"*)  ok "$1";; *)   bad "$1 [err=<$ERR> missing=<$2>]";; esac; }

echo "== check-body.sh =="
# clean body, exercising every allowed union target:
#   SD ref -> SD (self) and -> ED;  SU ref -> SD, ED, EU, SU.
# This also guards the over-correction direction: System->Essential must PASS.
run check-body.sh "$FIX/check_clean/docs"
rc_is   "clean body (incl. System->Essential refs) exits 0" 0
out_has "clean body reports OK" "OK"

# Recorded regression (DESIGN.md): Essential UseCase referencing a System Domain term.
run check-body.sh "$FIX/check_regression_eu_sd/docs"
rc_is   "EU->SD inversion (recorded regression) exits 1" 1
out_has "names the dangling ref" "[Member Row]"
out_has "names the required layer" "must resolve in ESSENTIAL_DOMAIN"
out_has "names the offending doc" "ESSENTIAL_USECASE.md"

# Additional inversion: Essential Domain referencing a System term.
run check-body.sh "$FIX/check_inversion_ed_sd/docs"
rc_is   "ED->SD inversion exits 1" 1
out_has "names the dangling ref" "[Member Row]"
out_has "names the required layer" "must resolve in ESSENTIAL_DOMAIN"

# Candidate notation must not leak into a canonical doc.
run check-body.sh "$FIX/check_stray/docs"
rc_is   "stray {candidate} exits 1" 1
out_has "flags STRAY" "STRAY"
out_has "names the stray candidate" "{Member Draft}"

# Backtick spans are stripped: these [x]/{x} would otherwise dangle / stray.
run check-body.sh "$FIX/check_backtick/docs"
rc_is   "backtick-wrapped [x]/{x} ignored -> exits 0" 0
out_has "still OK" "OK"

# A missing canonical doc is a setup error, distinct from a violation.
run check-body.sh "$FIX/check_missing/docs"
rc_is   "missing canonical doc exits 2" 2
err_has "names the missing file" "SYSTEM_USECASE.md"

echo "== check-question.sh =="
# A ready Q with only Essential Domain references is safe to show for Review.
run_question "$FIX/check_question_valid/docs" Q-001
rc_is   "structurally ready question exits 0" 0
out_has "structurally ready question reports OK" "OK"

# An Essential UseCase cannot name a System Domain term.
run_question "$FIX/check_question_invalid/docs" Q-001
rc_is   "invalid question exits 1" 1
out_has "invalid question names the ref" "[Member Row]"
out_has "invalid question names the required layer" "ESSENTIAL_DOMAIN"

echo "== next-question.sh =="
# Selection output carries Basis as the third token, so the gate-spawn decision
# is made from this one line. nq_priority exercises an `observed` selection;
# nq_lowest_q exercises a `proposed` selection.
#
# Essential preempts System; within a layer Domain precedes UseCase; layer/shape
# outrank the Q-number (so the lowest-numbered system-domain is NOT chosen).
run next-question.sh "$FIX/nq_priority/docs"
out_eq  "Essential>System, Domain>UseCase, priority beats low Q (+observed)" "Q-009 essential-domain observed"

# Same layer + shape -> lowest Q- wins. Selected candidate is `proposed`.
run next-question.sh "$FIX/nq_lowest_q/docs"
out_eq  "tie on layer+shape -> lowest Q (+proposed)" "Q-004 system-usecase proposed"

# A higher-priority but blocked candidate is skipped.
run next-question.sh "$FIX/nq_blocked_skip/docs"
out_eq  "blocked higher-priority candidate skipped" "Q-002 system-domain observed"

# Promote clears a now-confirmed dependency from Blocked by. The resulting
# use-case becomes ready and is selected ahead of lower-priority work.
run next-question.sh "$FIX/nq_unblocked_after_promote/docs"
out_eq  "cleared blocker makes its use-case ready" "Q-003 essential-usecase observed"

# An unrecognised Type is unorderable -> skipped (but still Basis-validated).
run next-question.sh "$FIX/nq_unknown_type/docs"
out_eq  "unknown Type skipped" "Q-002 system-usecase observed"

# Entries exist but all are blocked.
run next-question.sh "$FIX/nq_none_ready/docs"
out_eq  "entries exist, all blocked -> none-ready" "none-ready"

# Same sentinel for both empty conditions:
run next-question.sh "$FIX/nq_empty_noitems/docs"
out_eq  "file present, no Q- items -> queue-empty" "queue-empty"
run next-question.sh "$FIX/nq_empty_missing/docs"
out_eq  "queue file absent -> queue-empty" "queue-empty"

# Basis is a whole-queue structural invariant: a missing or unknown value is a
# malformed queue, surfaced loud (exit 3) rather than silently skipping the
# candidate. The offending Q- is named on stdout. This precedes selection, so a
# ready candidate with a bad Basis still fails instead of being asked.
run next-question.sh "$FIX/nq_basis_missing/docs"
out_eq  "missing Basis -> invalid-basis names the Q-" "invalid-basis Q-001"
rc_is   "missing Basis exits 3" 3
run next-question.sh "$FIX/nq_basis_invalid/docs"
out_eq  "unknown Basis value -> invalid-basis names the Q-" "invalid-basis Q-001"
rc_is   "unknown Basis value exits 3" 3

echo "== progress.sh =="
# Exact single line + derived arithmetic (resolved = confirmed + rejected;
# total = resolved + open). The line is pinned because SKILL.md relays it verbatim.
run progress.sh "$FIX/progress_counts/docs"
out_eq  "exact line, derived counts" "Progress: 4/6 resolved (3 confirmed + 1 rejected; 2 open)."

# Missing optional/canonical files count as 0 and never error.
run progress.sh "$FIX/progress_missing/docs"
out_eq  "missing files count as 0" "Progress: 1/1 resolved (1 confirmed + 0 rejected; 0 open)."
rc_is   "progress never errors on missing files" 0

echo
printf '%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]

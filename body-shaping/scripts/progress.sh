#!/usr/bin/env sh
# body-shaping: derive and print queue progress in one line, so the model
# never spends tokens counting headers by hand. Counting is mechanical;
# the model relays this one line into the Response Summary.
#
# Usage: progress.sh [DOCS_DIR]      (default: docs)
#
# All counts are derived from the current files, never stored:
#   confirmed = "## [..]" headers across the four canonical docs
#   rejected  = "## R-" entries in REJECTED.md
#   open      = "## Q-" entries in QUESTION_CANDIDATE.md
#   resolved  = confirmed + rejected
#   total     = resolved + open
#
# Missing optional files (REJECTED.md, QUESTION_CANDIDATE.md, or any canonical
# doc) count as 0 -- progress reports whatever exists and never errors out.
# This only counts; it never gates. The guard is check-body.sh.
#
# Counting is raw and line-anchored: a "## [..]" header inside a fenced code
# block in a canonical doc is counted too (check-body.sh strips such spans;
# this counter does not). Acceptable over-count for a progress indicator.
#
# Output is ASCII only, on a single line.
set -eu

DOCS="${1:-docs}"

# Count lines matching a BRE pattern across the given files; missing files
# and zero-match files both contribute 0.
count() {
  pat=$1; shift
  _sum=0
  for f in "$@"; do
    [ -f "$f" ] || continue
    c=$(grep -c -- "$pat" "$f" 2>/dev/null || true)
    c=${c:-0}
    _sum=$((_sum + c))
  done
  echo "$_sum"
}

confirmed=$(count '^## \[' \
  "$DOCS/ESSENTIAL_DOMAIN.md" "$DOCS/ESSENTIAL_USECASE.md" \
  "$DOCS/SYSTEM_DOMAIN.md" "$DOCS/SYSTEM_USECASE.md")
rejected=$(count '^## R-' "$DOCS/REJECTED.md")
open=$(count '^## Q-' "$DOCS/QUESTION_CANDIDATE.md")

resolved=$((confirmed + rejected))
total=$((resolved + open))

printf 'Progress: %d/%d resolved (%d confirmed + %d rejected; %d open).\n' \
  "$resolved" "$total" "$confirmed" "$rejected" "$open"

#!/usr/bin/env sh
# body-shaping: pick the next question to ask, deterministically, so the model
# never spends tokens reasoning out the order. The model runs this, then renders
# and Re-evaluates the chosen candidate.
#
# Usage: next-question.sh [DOCS_DIR]      (default: docs)
#
# Reads QUESTION_CANDIDATE.md and, over the READY candidates only (empty
# "Blocked by:"), prints the single next "Q-nnn <type> <basis>" in this priority:
#   1. layer  -- Essential before System
#   2. shape  -- Domain before UseCase
#   3. lowest Q- number
#
# It is STATELESS: it re-reads the whole queue every call and stores no cursor.
# So an Essential candidate discovered *after* System questions have begun is
# picked ahead of the remaining System ones automatically -- the questioning
# returns to Essential on its own, with nothing to go stale.
#
# A candidate is BLOCKED iff its "Blocked by:" section is NON-EMPTY -- any list
# item with content, or inline text after the label, regardless of notation
# ({term}, [term], or plain). A bare "-" or a blank section is ready. This is
# notation-agnostic on purpose: it matches SKILL.md's "non-empty Blocked by"
# contract and does NOT key on bracket style (an earlier version keyed on
# [brackets] and missed {candidate} / plain / inline blockers).
# Blocked candidates are skipped -- ask their blocking term first, it is itself a
# ready candidate. A candidate whose Type matches none of the four values is also
# skipped (unorderable). Ordering is mechanical; meaning-level Re-evaluate (same
# word, different meaning -> clash) stays the model's job on the chosen candidate.
#
# BASIS is validated structurally over the WHOLE queue on every call: every Q-
# candidate must carry "Basis:" with a value of exactly "observed" or "proposed".
# Basis is the claim's truth-maker source -- observed = a file path:line backs
# the claim, so the consistency gate runs; proposed = human confirmation is the
# truth-maker, so the gate is skipped and the candidate goes straight to Review.
# This check is a queue invariant, NOT a meaning judgment: the script only
# verifies the value is one of the two literals; WHICH one a candidate carries is
# Recover's call. A missing or unknown Basis on ANY candidate -- ready or blocked,
# orderable Type or not -- is a malformed queue, and the script fails loud rather
# than silently skipping, so a candidate can never be asked (or dropped) without a
# Basis. The selected candidate's Basis is emitted as the third output token, so
# the gate-spawn decision is made from this one line alone.
#
# Output (one line):
#   "Q-014 essential-domain observed"  -- the next candidate to ask, with its Basis
#   "none-ready"                       -- entries exist but all are blocked
#   "queue-empty"                      -- no Q- entries (file empty or missing)
#   "invalid-basis Q-014"              -- a candidate's Basis is missing or unknown
#
# Output is ASCII only. Exit status: 0 normally; 3 on invalid-basis. The printed
# token is the result.
set -eu

DOCS="${1:-docs}"
QUEUE="$DOCS/QUESTION_CANDIDATE.md"

[ -f "$QUEUE" ] || { echo "queue-empty"; exit 0; }

awk '
function capture_type(s) {
  if      (s ~ /essential-domain/)  type[n] = "essential-domain"
  else if (s ~ /essential-usecase/) type[n] = "essential-usecase"
  else if (s ~ /system-domain/)     type[n] = "system-domain"
  else if (s ~ /system-usecase/)    type[n] = "system-usecase"
}
function capture_basis(s) {
  gsub(/^[ \t]+|[ \t]+$/, "", s)
  if      (s == "observed") basis[n] = "observed"
  else if (s == "proposed") basis[n] = "proposed"
  else                      basis[n] = "BAD"      # present but not one of the two literals
}
function rank_layer(t) { return (t ~ /^essential/) ? 0 : 1 }
function rank_shape(t) { return (t ~ /usecase$/)   ? 1 : 0 }

/^## Q-/ {
  n++
  q = $0; sub(/^## +/, "", q); id[n] = q
  num = q; sub(/^Q-0*/, "", num); qnum[n] = (num == "" ? 0 : num + 0)
  type[n] = ""; basis[n] = ""; blocked[n] = 0; section = ""
  next
}
n > 0 && /^Type:/ {
  section = "type"
  rest = $0; sub(/^Type:[ \t]*/, "", rest)
  if (rest != "") capture_type(rest)
  next
}
n > 0 && /^Basis:/ {
  section = "basis"
  rest = $0; sub(/^Basis:[ \t]*/, "", rest)
  if (rest != "") capture_basis(rest)
  next
}
n > 0 && /^Blocked by:/ {
  section = "blocked"
  rest = $0; sub(/^Blocked by:[ \t]*/, "", rest); gsub(/[ \t]/, "", rest)
  if (rest != "" && rest != "-") blocked[n] = 1        # inline content after the label
  next
}
n > 0 && /^[A-Za-z].*:/ { section = "other";   next }
{
  if (section == "type"  && type[n]  == "" && $0 ~ /[a-z]/)    capture_type($0)
  if (section == "basis" && basis[n] == "" && $0 ~ /[^ \t]/)   capture_basis($0)
  if (section == "blocked") {
    bl = $0; gsub(/[ \t]/, "", bl)
    if (bl != "" && bl != "-") blocked[n] = 1          # any non-empty, non-bare-dash line
  }
}
END {
  if (n == 0) { print "queue-empty"; exit 0 }

  # Whole-queue Basis invariant: fail loud on the first malformed candidate, in
  # queue order, before any selection. Structural only -- the value must be one
  # of the two literals; which one a candidate carries is Recover s judgment.
  for (i = 1; i <= n; i++) {
    if (basis[i] != "observed" && basis[i] != "proposed") {
      print "invalid-basis " id[i]
      exit 3
    }
  }

  best = 0
  for (i = 1; i <= n; i++) {
    if (type[i] == "" || blocked[i]) continue
    L = rank_layer(type[i]); S = rank_shape(type[i]); Q = qnum[i]
    if (best == 0 || L < bL || (L == bL && S < bS) || (L == bL && S == bS && Q < bQ)) {
      best = i; bL = L; bS = S; bQ = Q
    }
  }
  if (best == 0) { print "none-ready"; exit 0 }
  print id[best] " " type[best] " " basis[best]
}
' "$QUEUE"

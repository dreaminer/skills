#!/usr/bin/env sh
# body-shaping: mechanical guard for the canonical body's [Term] discipline.
#
# Usage: check-body.sh [DOCS_DIR]      (default: docs)
#
# `[X]` vs `{X}` is a lookup, not a judgment: a term is canonical iff it is a
# "## [X]" header in the layer it belongs to. This script verifies that
# invariant so it never rests on prose discipline.
#
# Layer-aware checks over the four canonical docs. Dependency is DIRECTIONAL:
# the concrete layer may reference the abstract one, never the reverse. System
# may resolve refs in Essential (System "executes the Essential flow"); Essential
# may NOT resolve in System (an Essential doc naming a System term is the
# dependency inversion this guards against).
#   1. ESSENTIAL_DOMAIN refs   -> resolve in ESSENTIAL_DOMAIN
#   2. ESSENTIAL_USECASE refs  -> resolve in ESSENTIAL_DOMAIN
#   3. SYSTEM_DOMAIN refs      -> resolve in SYSTEM_DOMAIN or ESSENTIAL_DOMAIN
#   4. SYSTEM_USECASE refs     -> resolve in SYSTEM_DOMAIN or ESSENTIAL_DOMAIN,
#                                 or ESSENTIAL_USECASE (Related Essential Use Case),
#                                 or SYSTEM_USECASE (cross-flow self-reference)
#   5. no candidate notation {X} leaked into any canonical doc
#
# Inline code (backtick spans) is ignored, so a placeholder like `[Term]` or
# example code like `messages:{groupId}` does NOT trigger a false positive.
# Header lines (## [...]) are excluded from ref scanning so a header is not
# treated as a reference to itself.
#
# Output uses ASCII only, so POSIX awks without \xNN escape support behave
# identically to GNU awk.
#
# Exit status: 0 = clean, 1 = violation(s) found, 2 = missing file.
set -eu

DOCS="${1:-docs}"

missing=0
for f in ESSENTIAL_DOMAIN.md ESSENTIAL_USECASE.md SYSTEM_DOMAIN.md SYSTEM_USECASE.md; do
  [ -f "$DOCS/$f" ] || { echo "missing: $DOCS/$f" >&2; missing=1; }
done
[ "$missing" -eq 0 ] || exit 2

awk '
FNR==1 {
  if      (FILENAME ~ /ESSENTIAL_DOMAIN\.md$/)  ftype="ED"
  else if (FILENAME ~ /ESSENTIAL_USECASE\.md$/) ftype="EU"
  else if (FILENAME ~ /SYSTEM_DOMAIN\.md$/)     ftype="SD"
  else if (FILENAME ~ /SYSTEM_USECASE\.md$/)    ftype="SU"
}
{
  line=$0
  gsub(/`[^`]*`/, "", line)

  if (match(line, /^## \[[^]]+\]/)) {
    # capture the text between the brackets, matching how refs are keyed
    term = substr(line, 5, RLENGTH-5)
    confirmed[ftype, term] = 1
    next
  }

  s=line
  while (match(s, /\[[^]]+\]/)) {
    rname = substr(s, RSTART+1, RLENGTH-2)
    n_refs++
    ref_type[n_refs] = ftype
    ref_name[n_refs] = rname
    ref_loc[n_refs]  = FILENAME ":" FNR
    s = substr(s, RSTART+RLENGTH)
  }

  t=line
  while (match(t, /\{[^}]+\}/)) {
    cand = substr(t, RSTART, RLENGTH)
    if (!(cand in strayseen)) strayseen[cand] = FILENAME ":" FNR
    t = substr(t, RSTART+RLENGTH)
  }
}
END {
  bad=0
  for (i=1; i<=n_refs; i++) {
    src=ref_type[i]; rname=ref_name[i]; loc=ref_loc[i]
    valid=0; expected=""
    if (src == "ED") {
      if (("ED", rname) in confirmed) valid=1
      expected="ESSENTIAL_DOMAIN"
    } else if (src == "EU") {
      if (("ED", rname) in confirmed) valid=1
      expected="ESSENTIAL_DOMAIN"
    } else if (src == "SD") {
      if (("SD", rname) in confirmed) valid=1
      else if (("ED", rname) in confirmed) valid=1
      expected="SYSTEM_DOMAIN or ESSENTIAL_DOMAIN"
    } else if (src == "SU") {
      if (("SD", rname) in confirmed) valid=1
      else if (("ED", rname) in confirmed) valid=1
      else if (("EU", rname) in confirmed) valid=1
      else if (("SU", rname) in confirmed) valid=1
      expected="SYSTEM_DOMAIN, ESSENTIAL_DOMAIN, ESSENTIAL_USECASE, or SYSTEM_USECASE"
    }
    if (!valid) {
      print "DANGLING [" rname "] at " loc " -- must resolve in " expected
      bad++
    }
  }
  for (c in strayseen) {
    print "STRAY {..} in canonical doc: " c " (" strayseen[c] ")"
    bad++
  }
  nc=0; for (k in confirmed) nc++
  if (bad==0) printf "OK -- %d confirmed term(s); refs resolve to the correct layer; no stray {candidate}.\n", nc
  else        printf "FAIL -- %d violation(s).\n", bad
  exit (bad==0 ? 0 : 1)
}
' "$DOCS/ESSENTIAL_DOMAIN.md" "$DOCS/ESSENTIAL_USECASE.md" "$DOCS/SYSTEM_DOMAIN.md" "$DOCS/SYSTEM_USECASE.md"

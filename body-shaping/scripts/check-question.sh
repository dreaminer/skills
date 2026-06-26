#!/usr/bin/env sh
# body-shaping: mechanical pre-Review check for one queued question.
#
# Usage: check-question.sh <DOCS_DIR> <Q-ID>
#
# Reads only the selected queue entry and the four canonical documents. It
# verifies the queue shape needed to ask the question: an exact Type, Subject,
# and Basis; non-empty Content; an empty Blocked by section; no {candidate}
# notation in Content; and [Term] references resolvable in the layers allowed
# by Type. It does not judge evidence, wording, classification meaning, or
# same-name meaning clashes; those belong to the consistency gate and
# Re-evaluate.
#
# Subject is the canonical header that a Yes will create. It is virtual only
# where that header's layer may reference itself (Essential Domain, System
# Domain, System UseCase). An Essential UseCase name is not a domain reference,
# matching check-body.sh's canonical resolution rules.
#
# Exit status: 0 = ready to ask; 1 = question violation(s); 2 = missing input;
# 64 = invalid invocation or unknown Q-ID.
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: check-question.sh <DOCS_DIR> <Q-ID>" >&2
  exit 64
fi

DOCS=$1
QID=$2
QUEUE="$DOCS/QUESTION_CANDIDATE.md"

case "$QID" in
  Q-[0-9][0-9][0-9]*) ;;
  *)
    echo "invalid Q-ID: $QID" >&2
    exit 64
    ;;
esac

missing=0
for f in ESSENTIAL_DOMAIN.md ESSENTIAL_USECASE.md SYSTEM_DOMAIN.md SYSTEM_USECASE.md; do
  [ -f "$DOCS/$f" ] || { echo "missing: $DOCS/$f" >&2; missing=1; }
done
[ -f "$QUEUE" ] || { echo "missing: $QUEUE" >&2; missing=1; }
[ "$missing" -eq 0 ] || exit 2

awk -v qid="$QID" -v queue="$QUEUE" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function capture_type(s) {
  s=trim(s)
  if (type == "") type=s
  else if (type != s) type="BAD"
}
function capture_basis(s) {
  s=trim(s)
  if (basis == "") basis=s
  else if (basis != s) basis="BAD"
}
function capture_subject(s) {
  s=trim(s)
  if (s == "") return
  if (subject == "") subject=s
  else if (subject != s) subject="BAD"
}
function canonical_type() {
  if      (FILENAME ~ /ESSENTIAL_DOMAIN\.md$/)  return "ED"
  else if (FILENAME ~ /ESSENTIAL_USECASE\.md$/) return "EU"
  else if (FILENAME ~ /SYSTEM_DOMAIN\.md$/)     return "SD"
  else if (FILENAME ~ /SYSTEM_USECASE\.md$/)    return "SU"
  return ""
}
function bad(msg) { print msg; violations++ }
function valid_ref(src, name) {
  if (src == "ED") return (("ED", name) in confirmed) || name == subject
  if (src == "EU") return (("ED", name) in confirmed)
  if (src == "SD") return (("SD", name) in confirmed) || (("ED", name) in confirmed) || name == subject
  if (src == "SU") return (("SD", name) in confirmed) || (("ED", name) in confirmed) || (("EU", name) in confirmed) || (("SU", name) in confirmed) || name == subject
  return 0
}
function expected_ref(src) {
  if (src == "ED") return "ESSENTIAL_DOMAIN"
  if (src == "EU") return "ESSENTIAL_DOMAIN"
  if (src == "SD") return "SYSTEM_DOMAIN or ESSENTIAL_DOMAIN"
  if (src == "SU") return "SYSTEM_DOMAIN, ESSENTIAL_DOMAIN, ESSENTIAL_USECASE, or SYSTEM_USECASE"
  return "a valid canonical layer"
}

FILENAME != queue {
  ftype=canonical_type()
  if (match($0, /^## \[[^]]+\]/)) {
    term=substr($0, 5, RLENGTH-5)
    confirmed[ftype, term]=1
  }
  next
}

/^## Q-/ {
  current=$0; sub(/^## +/, "", current)
  selected=(current == qid)
  if (selected) { found=1; section=""; type=""; basis=""; subject=""; blocked=0; content_nonblank=0; ncontent=0 }
  next
}

!selected { next }

/^Type:/ {
  section="type"; rest=$0; sub(/^Type:[ \t]*/, "", rest); if (rest != "") capture_type(rest); next
}
/^Subject:/ {
  section="subject"; rest=$0; sub(/^Subject:[ \t]*/, "", rest); capture_subject(rest); next
}
/^Basis:/ {
  section="basis"; rest=$0; sub(/^Basis:[ \t]*/, "", rest); if (rest != "") capture_basis(rest); next
}
/^Content:/ {
  section="content"; rest=$0; sub(/^Content:[ \t]*/, "", rest); if (rest != "") content[++ncontent]=rest; if (trim(rest) != "") content_nonblank=1; next
}
/^Blocked by:/ {
  section="blocked"; rest=$0; sub(/^Blocked by:[ \t]*/, "", rest); rest=trim(rest); if (rest != "" && rest != "-") blocked=1; next
}
/^[A-Za-z][A-Za-z ]*:/ {
  if (section == "content") { content[++ncontent]=$0; if (trim($0) != "") content_nonblank=1 }
  else section="other"
  next
}

{
  if (section == "type" && trim($0) != "") capture_type($0)
  else if (section == "subject") capture_subject($0)
  else if (section == "basis" && trim($0) != "") capture_basis($0)
  else if (section == "content") { content[++ncontent]=$0; if (trim($0) != "") content_nonblank=1 }
  else if (section == "blocked") { line=trim($0); if (line != "" && line != "-") blocked=1 }
}

END {
  if (!found) { print "unknown question: " qid > "/dev/stderr"; exit 64 }

  if (type != "essential-domain" && type != "essential-usecase" && type != "system-domain" && type != "system-usecase") bad("INVALID Type for " qid ": " type)
  if (basis != "observed" && basis != "proposed") bad("INVALID Basis for " qid ": " basis)
  if (subject == "" || subject == "BAD" || subject ~ /[\[\]{}]/) bad("INVALID Subject for " qid ": " subject)
  if (!content_nonblank) bad("MISSING Content for " qid)
  if (blocked) bad("BLOCKED " qid " -- Blocked by must be empty before Review")

  src=""
  if      (type == "essential-domain")  src="ED"
  else if (type == "essential-usecase") src="EU"
  else if (type == "system-domain")     src="SD"
  else if (type == "system-usecase")    src="SU"

  if (src != "" && ((src == "ED" && (("ED", subject) in confirmed)) || (src == "EU" && (("EU", subject) in confirmed)) || (src == "SD" && (("SD", subject) in confirmed)) || (src == "SU" && (("SU", subject) in confirmed)))) {
    bad("SUBJECT [" subject "] already canonical in its target layer")
  }

  for (i=1; i<=ncontent; i++) {
    line=content[i]
    gsub(/`[^`]*`/, "", line)

    t=line
    while (match(t, /\{[^}]+\}/)) {
      bad("CANDIDATE " substr(t, RSTART, RLENGTH) " in Content of " qid)
      t=substr(t, RSTART+RLENGTH)
    }

    s=line
    while (match(s, /\[[^]]+\]/)) {
      name=substr(s, RSTART+1, RLENGTH-2)
      if (src != "" && !valid_ref(src, name)) bad("DANGLING [" name "] in Content of " qid " -- must resolve in " expected_ref(src))
      s=substr(s, RSTART+RLENGTH)
    }
  }

  if (violations == 0) {
    print "OK -- " qid " is structurally ready for Review."
    exit 0
  }
  print "FAIL -- " violations " question violation(s)."
  exit 1
}
' "$DOCS/ESSENTIAL_DOMAIN.md" "$DOCS/ESSENTIAL_USECASE.md" "$DOCS/SYSTEM_DOMAIN.md" "$DOCS/SYSTEM_USECASE.md" "$QUEUE"

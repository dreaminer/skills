#!/usr/bin/env sh
# Make Body: mechanically validate one selected candidate before human Review.
# Usage: check-question.sh <DOCS_DIR> <MB-ID>
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: check-question.sh <DOCS_DIR> <MB-ID>" >&2
  exit 64
fi

DOCS=$1
MBID=$2
QUEUE="$DOCS/MAKE_BODY_CANDIDATES.md"

case "$MBID" in MB-[0-9][0-9][0-9]*) ;; *) echo "invalid MB-ID: $MBID" >&2; exit 64 ;; esac

missing=0
for f in ESSENTIAL_DOMAIN.md ESSENTIAL_USECASE.md SYSTEM_DOMAIN.md SYSTEM_USECASE.md; do
  [ -f "$DOCS/$f" ] || { echo "missing: $DOCS/$f" >&2; missing=1; }
done
[ -f "$QUEUE" ] || { echo "missing: $QUEUE" >&2; missing=1; }
[ "$missing" -eq 0 ] || exit 2

awk -v mbid="$MBID" -v queue="$QUEUE" '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function once(name, value) { value=trim(value); if (value == "") return; if (field[name] == "") field[name]=value; else if (field[name] != value) field[name]="BAD" }
function doc_type() { if (FILENAME ~ /ESSENTIAL_DOMAIN\.md$/) return "ED"; if (FILENAME ~ /ESSENTIAL_USECASE\.md$/) return "EU"; if (FILENAME ~ /SYSTEM_DOMAIN\.md$/) return "SD"; if (FILENAME ~ /SYSTEM_USECASE\.md$/) return "SU"; return "" }
function bad(s) { print s; failures++ }
function expected(src) { if (src == "ED" || src == "EU") return "ESSENTIAL_DOMAIN"; if (src == "SD") return "SYSTEM_DOMAIN or ESSENTIAL_DOMAIN"; return "SYSTEM_DOMAIN, ESSENTIAL_DOMAIN, ESSENTIAL_USECASE, or SYSTEM_USECASE" }
function resolves(src, name) { if (src == "ED") return (("ED",name) in term) || name == field["subject"]; if (src == "EU") return (("ED",name) in term); if (src == "SD") return (("SD",name) in term) || (("ED",name) in term) || name == field["subject"]; if (src == "SU") return (("SD",name) in term) || (("ED",name) in term) || (("EU",name) in term) || (("SU",name) in term) || name == field["subject"]; return 0 }

FILENAME != queue { t=doc_type(); if (match($0, /^## \[[^]]+\]/)) term[t,substr($0,5,RLENGTH-5)]=1; next }
/^## MB-/ { id=$0; sub(/^## +/,"",id); selected=(id == mbid); if (selected) { found=1; section=""; delete field; delete content; ncontent=0; blocked=0 }; next }
!selected { next }
/^Type:/ { section="type"; v=$0; sub(/^Type:[ \t]*/,"",v); once("type",v); next }
/^Subject:/ { section="subject"; v=$0; sub(/^Subject:[ \t]*/,"",v); once("subject",v); next }
/^Content:/ { section="content"; v=$0; sub(/^Content:[ \t]*/,"",v); if (v != "") content[++ncontent]=v; next }
/^Blocked by:/ { section="blocked"; v=$0; sub(/^Blocked by:[ \t]*/,"",v); v=trim(v); if (v != "" && v != "-") blocked=1; next }
/^Evidence:/ { section="other"; next }
{
  if (section == "type") once("type",$0)
  else if (section == "subject") once("subject",$0)
  else if (section == "content") content[++ncontent]=$0
  else if (section == "blocked") { v=trim($0); if (v != "" && v != "-") blocked=1 }
}
END {
  if (!found) { print "unknown candidate: " mbid > "/dev/stderr"; exit 64 }
  type=field["type"]; subject=field["subject"]
  if (type != "essential-domain" && type != "essential-usecase" && type != "system-domain" && type != "system-usecase") bad("INVALID Type for " mbid)
  if (subject == "" || subject == "BAD" || subject ~ /[\[\]{}]/) bad("INVALID Subject for " mbid)
  if (ncontent == 0) bad("MISSING Content for " mbid)
  if (blocked) bad("BLOCKED " mbid)
  if (type == "essential-domain") src="ED"; else if (type == "essential-usecase") src="EU"; else if (type == "system-domain") src="SD"; else if (type == "system-usecase") src="SU"; else src=""
  if (src != "" && ((src == "ED" && (("ED",subject) in term)) || (src == "EU" && (("EU",subject) in term)) || (src == "SD" && (("SD",subject) in term)) || (src == "SU" && (("SU",subject) in term)))) bad("SUBJECT [" subject "] already canonical in its target layer")
  for (i=1;i<=ncontent;i++) { line=content[i]; gsub(/`[^`]*`/,"",line); x=line; while (match(x,/\{[^}]+\}/)) { bad("CANDIDATE " substr(x,RSTART,RLENGTH) " in Content of " mbid); x=substr(x,RSTART+RLENGTH) }; x=line; while (match(x,/\[[^]]+\]/)) { name=substr(x,RSTART+1,RLENGTH-2); if (src != "" && !resolves(src,name)) bad("DANGLING [" name "] in Content of " mbid " -- must resolve in " expected(src)); x=substr(x,RSTART+RLENGTH) } }
  if (failures == 0) { print "OK -- " mbid " is structurally ready for Review."; exit 0 }
  print "FAIL -- " failures " question violation(s)."; exit 1
}
' "$DOCS/ESSENTIAL_DOMAIN.md" "$DOCS/ESSENTIAL_USECASE.md" "$DOCS/SYSTEM_DOMAIN.md" "$DOCS/SYSTEM_USECASE.md" "$QUEUE"

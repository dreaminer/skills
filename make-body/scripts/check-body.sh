#!/usr/bin/env sh
# Make Body: mechanically validate canonical documents after Promote.
# Usage: check-body.sh <DOCS_DIR>
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: check-body.sh <DOCS_DIR>" >&2
  exit 64
fi

DOCS=$1
missing=0
for f in ESSENTIAL_DOMAIN.md ESSENTIAL_USECASE.md SYSTEM_DOMAIN.md SYSTEM_USECASE.md; do
  if [ ! -s "$DOCS/$f" ]; then
    echo "missing or empty: $DOCS/$f" >&2
    missing=1
  fi
done
[ "$missing" -eq 0 ] || exit 2

awk '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function type_for_file() { if (FILENAME ~ /ESSENTIAL_DOMAIN\.md$/) return "ED"; if (FILENAME ~ /ESSENTIAL_USECASE\.md$/) return "EU"; if (FILENAME ~ /SYSTEM_DOMAIN\.md$/) return "SD"; if (FILENAME ~ /SYSTEM_USECASE\.md$/) return "SU"; return "" }
function title(t) { if (t == "ED") return "ESSENTIAL_DOMAIN"; if (t == "EU") return "ESSENTIAL_USECASE"; if (t == "SD") return "SYSTEM_DOMAIN"; return "SYSTEM_USECASE" }
function expected(t) { if (t == "ED" || t == "EU") return "ESSENTIAL_DOMAIN"; if (t == "SD") return "SYSTEM_DOMAIN or ESSENTIAL_DOMAIN"; return "SYSTEM_DOMAIN, ESSENTIAL_DOMAIN, ESSENTIAL_USECASE, or SYSTEM_USECASE" }
function resolves(t, name) { if (t == "ED") return (("ED",name) in term); if (t == "EU") return (("ED",name) in term); if (t == "SD") return (("SD",name) in term) || (("ED",name) in term); return (("SD",name) in term) || (("ED",name) in term) || (("EU",name) in term) || (("SU",name) in term) }
function bad(message) { print message; failures++ }
function key() { return current_type SUBSEP current_subject }
function evidence_value(value, k) { value=trim(value); if (value == "" || value == "-") return; if (value !~ /^- `[^`]+:[0-9]+` — .+/) bad("INVALID Evidence for [" current_subject "] in " title(current_type)); else evidence[k]++ }
function content_value(value, k) { value=trim(value); if (value == "" || value == "-") return; content[k,section]++ }
function finish_subject(  k) {
  if (current_subject == "") return
  k=key()
  if (current_type == "ED" || current_type == "SD") {
    if (content[k,"meaning"] == 0) bad("MISSING Meaning for [" current_subject "] in " title(current_type))
  } else {
    if (content[k,"given"] == 0) bad("MISSING Given for [" current_subject "] in " title(current_type))
    if (content[k,"when"] == 0) bad("MISSING When for [" current_subject "] in " title(current_type))
    if (content[k,"then"] == 0) bad("MISSING Then for [" current_subject "] in " title(current_type))
  }
  if (evidence[k] == 0) bad("MISSING Evidence for [" current_subject "] in " title(current_type))
  current_subject=""; section=""
}
function finish_document() { finish_subject(); if (started && title_count != 1) bad("INVALID title count for " title(current_type)) }
function record_text(value,  n) { if (current_subject != "") { text_type[++ntext]=current_type; text[ntext]=value } }

FNR == 1 {
  if (started) finish_document()
  started=1; current_type=type_for_file(); current_subject=""; section=""; title_count=1
  if ($0 != "# " title(current_type)) bad("INVALID title for " title(current_type))
  next
}

/^# / { bad("INVALID title count for " title(current_type)); next }

/^## / {
  finish_subject()
  header=$0
  if (header !~ /^## \[[^][{}]+\]$/) {
    bad("INVALID canonical header in " title(current_type) ": " header)
    next
  }
  current_subject=header; sub(/^## \[/, "", current_subject); sub(/\]$/, "", current_subject)
  if ((current_type,current_subject) in term) bad("DUPLICATE Subject [" current_subject "] in " title(current_type))
  term[current_type,current_subject]=1
  section=""
  next
}

{
  line=$0
  if (current_subject == "") { if (trim(line) != "") bad("CONTENT before canonical header in " title(current_type)); next }
  record_text(line)
  if (line ~ /^Meaning:/) { section="meaning"; value=line; sub(/^Meaning:[ \t]*/, "", value); content_value(value, key()); next }
  if (line ~ /^Given:/) { section="given"; value=line; sub(/^Given:[ \t]*/, "", value); content_value(value, key()); next }
  if (line ~ /^When:/) { section="when"; value=line; sub(/^When:[ \t]*/, "", value); content_value(value, key()); next }
  if (line ~ /^Then:/) { section="then"; value=line; sub(/^Then:[ \t]*/, "", value); content_value(value, key()); next }
  if (line ~ /^Evidence:/) { section="evidence"; value=line; sub(/^Evidence:[ \t]*/, "", value); evidence_value(value, key()); next }
  if (section == "evidence") evidence_value(line, key()); else content_value(line, key())
}

END {
  if (started) finish_document()
  for (i=1; i<=ntext; i++) {
    line=text[i]; gsub(/`[^`]*`/, "", line)
    candidate=line
    while (match(candidate, /\{[^}]+\}/)) {
      bad("CANDIDATE " substr(candidate, RSTART, RLENGTH) " leaked into canonical " title(text_type[i]))
      candidate=substr(candidate, RSTART + RLENGTH)
    }
    reference=line
    while (match(reference, /\[[^]]+\]/)) {
      name=substr(reference, RSTART + 1, RLENGTH - 2)
      if (!resolves(text_type[i], name)) bad("DANGLING [" name "] in " title(text_type[i]) " -- must resolve in " expected(text_type[i]))
      reference=substr(reference, RSTART + RLENGTH)
    }
  }
  if (failures == 0) { print "OK -- canonical body is structurally valid."; exit 0 }
  print "FAIL -- " failures " body violation(s)."; exit 1
}
' "$DOCS/ESSENTIAL_DOMAIN.md" "$DOCS/ESSENTIAL_USECASE.md" "$DOCS/SYSTEM_DOMAIN.md" "$DOCS/SYSTEM_USECASE.md"

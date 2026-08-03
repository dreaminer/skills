#!/usr/bin/env sh
# Validate the human-ratified R6 Essential body.
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: check-body.sh <DOCS_DIR>" >&2
  exit 64
fi

DOCS=$1
for file in ESSENTIAL_DOMAIN.md ESSENTIAL_USECASE.md; do
  if [ ! -s "$DOCS/$file" ]; then
    echo "missing or empty: $DOCS/$file" >&2
    exit 2
  fi
done

awk '
function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
function dtype() { return FILENAME ~ /ESSENTIAL_DOMAIN\.md$/ ? "ED" : "EU" }
function title(t) { return t == "ED" ? "ESSENTIAL_DOMAIN" : "ESSENTIAL_USECASE" }
function bad(message) { print message; failures++ }
function key() { return current_type SUBSEP current_subject }
function value(line, k) { line=trim(line); if (line != "" && line != "-") content[k,section]++ }
function evidence(line, k) {
  line=trim(line); if (line == "" || line == "-") return
  evidence_count[k]++
  if (line ~ /^- Human-ratified: .+/) ratified[k]++
}
function finish_subject(  k) {
  if (current_subject == "") return
  k=key()
  if (current_type == "ED") {
    if (content[k,"meaning"] == 0) bad("MISSING Meaning for [" current_subject "] in ESSENTIAL_DOMAIN")
  } else {
    if (content[k,"given"] == 0) bad("MISSING Given for [" current_subject "] in ESSENTIAL_USECASE")
    if (content[k,"when"] == 0) bad("MISSING When for [" current_subject "] in ESSENTIAL_USECASE")
    if (content[k,"then"] == 0) bad("MISSING Then for [" current_subject "] in ESSENTIAL_USECASE")
  }
  if (evidence_count[k] == 0) bad("MISSING Evidence for [" current_subject "] in " title(current_type))
  if (ratified[k] == 0) bad("MISSING Human-ratified Evidence for [" current_subject "] in " title(current_type))
  current_subject=""; section=""
}
function finish_document() { finish_subject() }

FNR == 1 {
  if (started) finish_document()
  started=1; current_type=dtype(); current_subject=""; section=""
  if ($0 != "# " title(current_type)) bad("INVALID title for " title(current_type))
  next
}

/^# / { bad("INVALID extra title in " title(current_type)); next }

/^## / {
  finish_subject()
  if ($0 !~ /^## \[[^][{}]+\]$/) { bad("INVALID canonical header in " title(current_type) ": " $0); next }
  current_subject=$0; sub(/^## \[/,"",current_subject); sub(/\]$/,"",current_subject)
  if ((current_type,current_subject) in subject) bad("DUPLICATE Subject [" current_subject "] in " title(current_type))
  subject[current_type,current_subject]=1
  next
}

{
  line=$0
  if (current_subject == "") { if (trim(line) != "") bad("CONTENT before canonical header in " title(current_type)); next }
  text_type[++ntext]=current_type; text[ntext]=line; k=key()
  if (line ~ /^Meaning:/) { section="meaning"; sub(/^Meaning:[ \t]*/,"",line); value(line,k); next }
  if (line ~ /^Given:/) { section="given"; sub(/^Given:[ \t]*/,"",line); value(line,k); next }
  if (line ~ /^When:/) { section="when"; sub(/^When:[ \t]*/,"",line); value(line,k); next }
  if (line ~ /^Then:/) { section="then"; sub(/^Then:[ \t]*/,"",line); value(line,k); next }
  if (line ~ /^Evidence:/) { section="evidence"; sub(/^Evidence:[ \t]*/,"",line); evidence(line,k); next }
  if (section == "evidence") evidence(line,k); else value(line,k)
}

END {
  if (started) finish_document()
  for (i=1; i<=ntext; i++) {
    line=text[i]; gsub(/`[^`]*`/,"",line)
    candidate=line
    while (match(candidate,/\{[^}]+\}/)) {
      bad("CANDIDATE " substr(candidate,RSTART,RLENGTH) " leaked into canonical " title(text_type[i]))
      candidate=substr(candidate,RSTART+RLENGTH)
    }
    if (text_type[i] == "EU") {
      reference=line
      while (match(reference,/\[[^]]+\]/)) {
        name=substr(reference,RSTART+1,RLENGTH-2)
        if (!("ED",name) in subject) bad("DANGLING [" name "] in ESSENTIAL_USECASE -- must resolve in ESSENTIAL_DOMAIN")
        reference=substr(reference,RSTART+RLENGTH)
      }
    }
  }
  if (failures == 0) { print "OK -- Essential body is structurally valid."; exit 0 }
  print "FAIL -- " failures " body violation(s)."; exit 1
}
' "$DOCS/ESSENTIAL_DOMAIN.md" "$DOCS/ESSENTIAL_USECASE.md"

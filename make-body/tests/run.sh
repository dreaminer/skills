#!/usr/bin/env sh
set -u
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SCRIPT="$HERE/../scripts/check-question.sh"
BODY="$HERE/../scripts/check-body.sh"
CANONICAL_EVIDENCE="$HERE/../scripts/check-canonical-evidence.py"
FACTS="$HERE/../scripts/collect-typescript-facts.py"
EXTRACT="$HERE/../scripts/extract-typescript-candidates.py"
PY_FACTS="$HERE/../scripts/collect-python-facts.py"
PY_EXTRACT="$HERE/../scripts/extract-python-candidates.py"
COMBINED_FACTS="$HERE/../scripts/collect-code-facts.py"
COMBINED_EXTRACT="$HERE/../scripts/extract-code-facts-candidates.py"
CHECK_FACTS="$HERE/../scripts/check-code-facts.py"
FACT_COVERAGE="$HERE/../scripts/report-fact-coverage.py"
BOOTSTRAP="$HERE/../scripts/bootstrap-make-body.py"
SHOW_EVIDENCE="$HERE/../scripts/show-evidence.py"
TRACE="$HERE/../scripts/trace-system-flows.py"
REVIEW="$HERE/../scripts/review-candidate.py"
REVIEW_NEXT="$HERE/../scripts/review-next-candidate.py"
SYMBOL_USES="$HERE/../scripts/find-symbol-uses.py"
EVIDENCE="$HERE/../scripts/check-evidence.py"
NEXT="$HERE/../scripts/next-candidate.py"
INIT="$HERE/../scripts/init-docs.py"
STATUS="$HERE/../scripts/report-status.py"
CONFLICTS="$HERE/../scripts/check-conflicts.py"
CHECK_REJECTED="$HERE/../scripts/check-rejected.py"
DUPLICATES="$HERE/../scripts/check-candidate-duplicates.py"
WORKSPACE="$HERE/../scripts/check-workspace.py"
PREPARE="$HERE/../scripts/prepare-promotion.py"
PREPARE_NEXT="$HERE/../scripts/prepare-next-promotion.py"
PROMOTE_NEXT_SYSTEM="$HERE/../scripts/promote-next-system.py"
PREVIEW_REVIEW="$HERE/../scripts/review-promotion-preview.py"
APPLY="$HERE/../scripts/apply-promotion.py"
PREFLIGHT="$HERE/../scripts/preflight.py"
FIX="$HERE/fixtures"
pass=0; fail=0
ok() { pass=$((pass + 1)); printf 'ok   - %s\n' "$1"; }
bad() { fail=$((fail + 1)); printf 'FAIL - %s\n' "$1"; }
run() { ERRF="$HERE/.stderr.$$"; OUT=$(sh "$SCRIPT" "$1" "${2:-MB-001}" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_body() { ERRF="$HERE/.stderr.$$"; OUT=$(sh "$BODY" "$1" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_canonical_evidence() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$CANONICAL_EVIDENCE" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_evidence() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$EVIDENCE" "$1" "$2" MB-001 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_next() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$NEXT" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_status() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$STATUS" "$1" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_conflicts() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$CONFLICTS" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_check_rejected() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$CHECK_REJECTED" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_apply() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$APPLY" "$1" "$2" "$3" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_duplicates() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$DUPLICATES" "$1" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_workspace() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$WORKSPACE" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_workspace_full_coverage() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$WORKSPACE" "$1" "$2" --require-full-coverage 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_show_evidence() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$SHOW_EVIDENCE" "$1" "$2" --radius 1 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_trace() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$TRACE" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_review() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$REVIEW" "$1" "$2" MB-001 --radius 1 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_review_next() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$REVIEW_NEXT" "$1" "$2" --radius 1 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_symbol_uses() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$SYMBOL_USES" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_check_facts() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$CHECK_FACTS" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_fact_coverage() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$FACT_COVERAGE" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_bootstrap() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$BOOTSTRAP" "$1" "$2" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_bootstrap_dry() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$BOOTSTRAP" "$1" "$2" --dry-run 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_bootstrap_adapter() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$BOOTSTRAP" "$1" "$2" --adapter "$3" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_bootstrap_full_coverage() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$BOOTSTRAP" "$1" "$2" --require-full-coverage 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_prepare_next() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$PREPARE_NEXT" "$1" "$2" "$3" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_promote_next_system() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$PROMOTE_NEXT_SYSTEM" "$1" "$2" "$3" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
run_preview_review() { ERRF="$HERE/.stderr.$$"; OUT=$(python3 "$PREVIEW_REVIEW" "$1" "$2" "$3" 2>"$ERRF"); RC=$?; ERR=$(sed -n '1,$p' "$ERRF"); rm -f "$ERRF"; }
assert_rc() { [ "$RC" = "$2" ] && ok "$1" || bad "$1 [exit=$RC out=<$OUT> err=<$ERR>]"; }
assert_has() { case "$OUT" in *"$2"*) ok "$1";; *) bad "$1 [out=<$OUT>]";; esac; }
assert_file_eq() {
  if cmp -s "$1" "$2"; then
    ok "$3"
  else
    bad "$3 [expected=$1 actual=$2]"
  fi
}
assert_has_file() { grep -F "$2" "$1" >/dev/null && ok "$3" || bad "$3 [file=$1 expected=<$2>]"; }

OUT=$(python3 "$PREFLIGHT" 2>&1)
RC=$?
assert_rc "Preflight accepts current runtime" 0
assert_has "Preflight reports Python runtime" "OK python3"
assert_has "Preflight reports no package install needed" "OK no third-party Python packages required"

INIT_DOCS=$(mktemp -d)
python3 "$INIT" "$INIT_DOCS"
for f in ESSENTIAL_DOMAIN ESSENTIAL_USECASE SYSTEM_DOMAIN SYSTEM_USECASE MAKE_BODY_CODE_FACTS MAKE_BODY_COVERAGE_IGNORE MAKE_BODY_CANDIDATES MAKE_BODY_CONFLICTS MAKE_BODY_REJECTED; do
  [ -f "$INIT_DOCS/$f.md" ] && ok "Initializer creates $f" || bad "Initializer creates $f"
done
run_body "$INIT_DOCS"
assert_rc "Initialized canonical body is valid" 0
printf '# preserved\n' > "$INIT_DOCS/MAKE_BODY_CONFLICTS.md"
python3 "$INIT" "$INIT_DOCS" >/dev/null
assert_has_file "$INIT_DOCS/MAKE_BODY_CONFLICTS.md" "# preserved" "Initializer preserves existing file"
rm -rf "$INIT_DOCS"

STATUS_DOCS=$(mktemp -d)
python3 "$INIT" "$STATUS_DOCS" >/dev/null
cp "$FIX/selection/docs/MAKE_BODY_CANDIDATES.md" "$STATUS_DOCS/MAKE_BODY_CANDIDATES.md"
printf '\n## MC-001\n\nSubject:\n- Plan\n' >> "$STATUS_DOCS/MAKE_BODY_CONFLICTS.md"
printf '\n## MR-001\n\nSubject:\n- Legacy Sessions Table\n' >> "$STATUS_DOCS/MAKE_BODY_REJECTED.md"
run_status "$STATUS_DOCS"
assert_rc "Status report succeeds for initialized documents" 0
assert_has "Status report counts open candidates" "CANDIDATES_OPEN=4"
assert_has "Status report counts ready candidates" "CANDIDATES_READY=3"
assert_has "Status report counts blocked candidates" "CANDIDATES_BLOCKED=1"
assert_has "Status report counts conflicts" "CONFLICTS_UNRESOLVED=1"
assert_has "Status report counts rejected records" "REJECTED_RECORDED=1"
assert_has "Status report lists coverage ignore path" "MAKE_BODY_COVERAGE_IGNORE.md"
assert_has "Status report lists rejected archive path" "MAKE_BODY_REJECTED.md"
rm -rf "$STATUS_DOCS"

run_conflicts "$FIX/conflict-valid" "$FIX/conflict-valid/docs"
assert_rc "Complete conflict record is valid" 0
assert_has "Conflict validator reports OK" "OK"
run_conflicts "$FIX/conflict-invalid" "$FIX/conflict-invalid/docs"
assert_rc "Incomplete conflict record fails" 1
assert_has "Conflict validator names missing rationale" "MISSING Why unresolved"

run_check_rejected "$FIX/rejected-valid" "$FIX/rejected-valid/docs"
assert_rc "Complete rejected record is valid" 0
assert_has "Rejected validator reports OK" "OK"
assert_has "Rejected validator accepts Python evidence" "2 rejected record(s)"
run_check_rejected "$FIX/rejected-invalid" "$FIX/rejected-invalid/docs"
assert_rc "Rejected record missing a field fails" 1
assert_has "Rejected validator names missing field" "MISSING Reason"
run_check_rejected "$FIX/rejected-resurrected" "$FIX/rejected-resurrected/docs"
assert_rc "Queued candidate matching a rejected record fails" 1
assert_has "Rejected validator flags resurrection" "RESURRECTED MB-001"
NOARCHIVE_DOCS=$(mktemp -d)
run_check_rejected "$FIX/rejected-valid" "$NOARCHIVE_DOCS"
assert_rc "Absent rejected archive is valid" 0
rm -rf "$NOARCHIVE_DOCS"

run_duplicates "$FIX/candidate-duplicates/docs"
assert_rc "Source-equivalent candidates fail duplicate check" 1
assert_has "Duplicate check reports both candidate IDs" "MB-002, MB-004"

AUDIT_DOCS=$(mktemp -d)
python3 "$INIT" "$AUDIT_DOCS" >/dev/null
cp "$FIX/selection/docs"/*.md "$AUDIT_DOCS/"
run_workspace "$FIX/selection" "$AUDIT_DOCS"
assert_rc "Workspace audit accepts valid canonical and unblocked candidates" 0
assert_has "Workspace audit reports skipped blocked candidate" "SKIPPED_BLOCKED=1"
assert_has "Workspace audit reports success" "OK WORKSPACE"
rm -rf "$AUDIT_DOCS"

COVERAGE_AUDIT_DOCS=$(mktemp -d)
python3 "$INIT" "$COVERAGE_AUDIT_DOCS" >/dev/null
python3 "$COMBINED_FACTS" "$FIX/mixed-facts/project" "$COVERAGE_AUDIT_DOCS/MAKE_BODY_CODE_FACTS.md"
run_workspace_full_coverage "$FIX/mixed-facts/project" "$COVERAGE_AUDIT_DOCS"
assert_rc "Strict workspace audit rejects unrepresented source" 1
case "$ERR" in *"UNREPRESENTED src/helper.ts"*) ok "Strict workspace audit names unrepresented source";; *) bad "Strict workspace audit names unrepresented source [err=<$ERR>]";; esac
printf '# MAKE_BODY_COVERAGE_IGNORE\n\n- `src/helper.ts` — helper has no supported lexical entry\n' > "$COVERAGE_AUDIT_DOCS/MAKE_BODY_COVERAGE_IGNORE.md"
run_workspace_full_coverage "$FIX/mixed-facts/project" "$COVERAGE_AUDIT_DOCS"
assert_rc "Strict workspace audit accepts documented coverage exception" 0
rm -rf "$COVERAGE_AUDIT_DOCS"

run "$FIX/essential-domain/docs"
assert_rc "Essential Domain golden candidate is ready" 0
assert_has "Essential Domain golden candidate reports OK" "OK"

run "$FIX/system-domain/docs"
assert_rc "System Domain golden candidate is ready" 0
assert_has "System Domain golden candidate reports OK" "OK"

run "$FIX/essential-system-inversion/docs"
assert_rc "Essential candidate naming System term fails" 1
assert_has "Inversion names System term" "[Order Row]"
assert_has "Inversion requires Essential Domain" "ESSENTIAL_DOMAIN"

run_evidence "$FIX/essential-domain" "$FIX/essential-domain/docs"
assert_rc "Candidate evidence points to in-scope source" 0
assert_has "Candidate evidence reports OK" "OK"

run_evidence "$FIX/evidence-invalid" "$FIX/evidence-invalid/docs"
assert_rc "Out-of-range Evidence line fails" 1
assert_has "Evidence failure names out-of-range line" "line out of range"

run_show_evidence "$FIX/python-facts/project" "src/orders.py:3"
assert_rc "Evidence context prints an in-scope code window" 0
assert_has "Evidence context highlights requested line" ">    3 |     order = await repository.insert(request)"

run_review "$FIX/essential-domain" "$FIX/essential-domain/docs"
assert_rc "Candidate review renders validated candidate" 0
assert_has "Candidate review includes code context" "# Evidence Context: source/member.ts:2"

ESSENTIAL_REVIEW_OUT="$HERE/.essential-review.$$"
python3 "$REVIEW" "$FIX/essential-review" "$FIX/essential-review/docs" MB-001 --radius 1 > "$ESSENTIAL_REVIEW_OUT"
assert_file_eq "$FIX/essential-review/expected/REVIEW.md" "$ESSENTIAL_REVIEW_OUT" "Essential candidate review renders a deterministic judgment frame"
rm -f "$ESSENTIAL_REVIEW_OUT"
run_review "$FIX/essential-review" "$FIX/essential-review/docs"
assert_rc "Essential candidate review succeeds" 0
assert_has "Essential review surfaces lexically co-located System term" "- [Order Row]"
assert_has "Essential review renders the fixed reviewer checklist" "## Reviewer checklist"
assert_has "Essential review points to the judgment protocol" "references/essential-review.md"

run_symbol_uses "$FIX/symbol-uses/project" createOrder
assert_rc "Symbol use finder scans in-scope code" 0
assert_has "Symbol use finder finds direct caller" "src/orders.ts:6"

run_next "$FIX/selection" "$FIX/selection/docs"
assert_rc "Selector chooses ready System candidates before Essential candidates" 0
assert_has "Selector reports the selected candidate" "NEXT MB-004 system-usecase Submit Member Handler"

run_review_next "$FIX/selection" "$FIX/selection/docs"
assert_rc "Next review renders the selected candidate" 0
assert_has "Next review reports deterministic selection" "NEXT MB-004 system-usecase Submit Member Handler"
assert_has "Next review includes selected evidence context" "# Evidence Context: source/member.ts:2"
case "$OUT" in *"# Essential Review:"*) bad "System review stays free of the Essential frame [out=<$OUT>]";; *) ok "System review stays free of the Essential frame";; esac

NEXT_PREVIEW="$HERE/.next-preview.$$"
run_prepare_next "$FIX/selection" "$FIX/selection/docs" "$NEXT_PREVIEW"
assert_rc "Next promotion creates a preview" 0
assert_has "Next promotion reports deterministic selection" "NEXT MB-004 system-usecase Submit Member Handler"
assert_has_file "$NEXT_PREVIEW/MAKE_BODY_PROMOTION_MANIFEST" "candidate MB-004" "Next promotion preview records selected candidate"
rm -rf "$NEXT_PREVIEW"

AUTO_DOCS=$(mktemp -d)
python3 "$INIT" "$AUTO_DOCS" >/dev/null
cp "$FIX/selection/docs"/*.md "$AUTO_DOCS/"
AUTO_PREVIEW="$HERE/.auto-preview.$$"
run_promote_next_system "$FIX/selection" "$AUTO_DOCS" "$AUTO_PREVIEW"
assert_rc "System auto-promotion stops at the consistency gate" 0
assert_has "System auto-promotion reports selected candidate" "NEXT MB-004 system-usecase Submit Member Handler"
assert_has "System auto-promotion uses gate-neutral preview readiness" "PREVIEW_READY_FOR_APPROVAL_GATE"
assert_has "System auto-promotion hands off to the gate" "AWAIT_GATE -- MB-004 system-usecase Submit Member Handler"
assert_has_file "$AUTO_PREVIEW/MAKE_BODY_PROMOTION_MANIFEST" "candidate MB-004" "System auto-promotion records preview manifest"
if grep -qF "Submit Member Handler" "$AUTO_DOCS/SYSTEM_USECASE.md"; then bad "System auto-promotion does not apply before the gate"; else ok "System auto-promotion does not apply before the gate"; fi
# After the gate returns READY, the agent applies the prepared preview.
run_apply "$AUTO_PREVIEW" "$FIX/selection" "$AUTO_DOCS"
assert_rc "Applying the gated preview promotes the System candidate" 0
assert_has_file "$AUTO_DOCS/SYSTEM_USECASE.md" "## [Submit Member Handler]" "Gated apply writes canonical System UseCase"
rm -rf "$AUTO_DOCS" "$AUTO_PREVIEW"

HUMAN_DOCS=$(mktemp -d)
python3 "$INIT" "$HUMAN_DOCS" >/dev/null
cp "$FIX/essential-domain/docs"/*.md "$HUMAN_DOCS/"
HUMAN_PREVIEW="$HERE/.human-preview.$$"
run_promote_next_system "$FIX/essential-domain" "$HUMAN_DOCS" "$HUMAN_PREVIEW"
assert_rc "System auto-promotion refuses an Essential candidate" 3
assert_has "System auto-promotion names human gate" "NEEDS_HUMAN -- next candidate is essential-domain: MB-001 Member"
[ ! -e "$HUMAN_PREVIEW" ] && ok "Essential refusal creates no preview" || bad "Essential refusal creates no preview"
rm -rf "$HUMAN_DOCS" "$HUMAN_PREVIEW"

run_body "$FIX/canonical-valid/docs"
assert_rc "Canonical body with allowed directional references is valid" 0
assert_has "Canonical body reports OK" "OK"

run_body "$FIX/canonical-invalid/docs"
assert_rc "Candidate notation and Essential-to-System reference fail" 1
assert_has "Canonical body rejects candidate notation" "CANDIDATE {Order}"
assert_has "Canonical body rejects Essential-to-System reference" "DANGLING [Order Row]"

run_canonical_evidence "$FIX/canonical-invalid" "$FIX/canonical-invalid/docs"
assert_rc "Missing canonical Evidence source fails" 1
assert_has "Canonical Evidence failure names pointer" "INVALID canonical Evidence pointer"

run_check_facts "$FIX/code-facts/project" "$FIX/code-facts/expected/MAKE_BODY_CODE_FACTS.md"
assert_rc "Generated TypeScript fact index is fresh" 0
FACTS_COPY="$HERE/.facts-copy.$$"
cp "$FIX/code-facts/expected/MAKE_BODY_CODE_FACTS.md" "$FACTS_COPY"
printf '\n' >> "$FACTS_COPY"
run_check_facts "$FIX/code-facts/project" "$FACTS_COPY"
assert_rc "Modified fact index is stale" 1
assert_has "Fact freshness reports stale index" "STALE"
rm -f "$FACTS_COPY"

FACTS_OUT="$HERE/.facts.$$"
python3 "$FACTS" "$FIX/code-facts/project" "$FACTS_OUT"
assert_file_eq "$FIX/code-facts/expected/MAKE_BODY_CODE_FACTS.md" "$FACTS_OUT" "TypeScript adapter golden facts are stable"
TRACE_OUT="$HERE/.trace.$$"
python3 "$TRACE" "$FIX/code-facts/project" "$FIX/code-facts/expected/MAKE_BODY_CODE_FACTS.md" > "$TRACE_OUT"
assert_file_eq "$FIX/code-facts/expected/MAKE_BODY_FLOW_TRACES.md" "$TRACE_OUT" "TypeScript flow traces are stable"
rm -f "$TRACE_OUT"
UNRESOLVED_FACTS="$HERE/.unresolved-facts.$$"
printf '# MAKE_BODY_CODE_FACTS\n\nAdapter: typescript-node-lexical-v1\n\n## http-entry\n\n- `src/orders.ts:7` — router.post("/missing", missingHandler);\n' > "$UNRESOLVED_FACTS"
run_trace "$FIX/code-facts/project" "$UNRESOLVED_FACTS"
assert_rc "Flow trace accepts an unresolved handler" 0
assert_has "Flow trace marks unresolved handler" "unresolved: missingHandler"
rm -f "$UNRESOLVED_FACTS"
rm -f "$FACTS_OUT"

PY_FACTS_OUT="$HERE/.python-facts.$$"
PY_CANDIDATES_OUT="$HERE/.python-candidates.$$"
python3 "$PY_FACTS" "$FIX/python-facts/project" "$PY_FACTS_OUT"
assert_file_eq "$FIX/python-facts/expected/MAKE_BODY_CODE_FACTS.md" "$PY_FACTS_OUT" "Python adapter golden facts are stable"
PY_TRACE_OUT="$HERE/.python-trace.$$"
python3 "$TRACE" "$FIX/python-facts/project" "$FIX/python-facts/expected/MAKE_BODY_CODE_FACTS.md" > "$PY_TRACE_OUT"
assert_file_eq "$FIX/python-facts/expected/MAKE_BODY_FLOW_TRACES.md" "$PY_TRACE_OUT" "Python flow traces are stable"
rm -f "$PY_TRACE_OUT"
python3 "$PY_EXTRACT" "$PY_FACTS_OUT" "$PY_CANDIDATES_OUT"
assert_file_eq "$FIX/python-facts/expected/MAKE_BODY_CANDIDATES.md" "$PY_CANDIDATES_OUT" "Python System candidate scaffolds are stable"
rm -f "$PY_FACTS_OUT" "$PY_CANDIDATES_OUT"

MIXED_FACTS_OUT="$HERE/.mixed-facts.$$"
MIXED_CANDIDATES_OUT="$HERE/.mixed-candidates.$$"
python3 "$COMBINED_FACTS" "$FIX/mixed-facts/project" "$MIXED_FACTS_OUT"
assert_has_file "$MIXED_FACTS_OUT" "typescript-node-lexical-v1, python-lexical-v1" "Combined collector retains both adapter facts"
assert_has_file "$MIXED_FACTS_OUT" "@app.task -> send_order" "Combined collector retains Python task"
assert_has_file "$MIXED_FACTS_OUT" "router.post(\"/orders\", createOrder);" "Combined collector retains TypeScript route"
run_fact_coverage "$FIX/mixed-facts/project" "$MIXED_FACTS_OUT"
assert_rc "Fact coverage report succeeds" 0
assert_has "Fact coverage reports unrepresented source" "UNREPRESENTED src/helper.ts"
python3 "$COMBINED_EXTRACT" "$MIXED_FACTS_OUT" "$MIXED_CANDIDATES_OUT"
assert_has_file "$MIXED_CANDIDATES_OUT" "POST /orders Route" "Combined extractor creates TypeScript route candidate"
assert_has_file "$MIXED_CANDIDATES_OUT" "Send Order Task" "Combined extractor creates Python task candidate"
rm -f "$MIXED_FACTS_OUT" "$MIXED_CANDIDATES_OUT"

BOOTSTRAP_DOCS=$(mktemp -d)
run_bootstrap "$FIX/mixed-facts/project" "$BOOTSTRAP_DOCS"
assert_rc "Bootstrap initializes mixed project body" 0
assert_has "Bootstrap selects combined adapter" "OK BOOTSTRAP adapter=combined"
assert_has "Bootstrap reports generated candidates" "CREATED MAKE_BODY_CANDIDATES.md"
assert_has_file "$BOOTSTRAP_DOCS/MAKE_BODY_CANDIDATES.md" "Send Order Task" "Bootstrap seeds mixed System candidates"
assert_has "Bootstrap creates the rejected archive" "CREATED MAKE_BODY_REJECTED.md"
rm -rf "$BOOTSTRAP_DOCS"

# A pre-existing rejected archive is staged so extractor suppression holds on the
# bootstrap path, and its Python Evidence pointer validates through the staged
# check-rejected. Without the staging fix the rejected scaffold is re-seeded;
# without the .py fix the staged check fails.
BOOTSTRAP_REJECTED_DOCS=$(mktemp -d)
printf '# MAKE_BODY_REJECTED\n\n## MR-001\n\nType:\nsystem-usecase\n\nSubject:\nSend Order Task\n\nReason:\n- Not a domain use case.\n\nEvidence:\n- `workers/send_order.py:1` — @app.task -> send_order\n\nReplacement:\n-\n' > "$BOOTSTRAP_REJECTED_DOCS/MAKE_BODY_REJECTED.md"
run_bootstrap "$FIX/mixed-facts/project" "$BOOTSTRAP_REJECTED_DOCS"
assert_rc "Bootstrap accepts a staged Python rejected record" 0
assert_has_file "$BOOTSTRAP_REJECTED_DOCS/MAKE_BODY_REJECTED.md" "Send Order Task" "Bootstrap preserves the staged rejected archive"
assert_has_file "$BOOTSTRAP_REJECTED_DOCS/MAKE_BODY_CANDIDATES.md" "POST /orders Route" "Bootstrap still seeds non-rejected candidates"
grep -qF "Send Order Task" "$BOOTSTRAP_REJECTED_DOCS/MAKE_BODY_CANDIDATES.md" && bad "Bootstrap suppresses a staged rejected candidate" || ok "Bootstrap suppresses a staged rejected candidate"
rm -rf "$BOOTSTRAP_REJECTED_DOCS"

BOOTSTRAP_DRY_DOCS=$(mktemp -d)
rmdir "$BOOTSTRAP_DRY_DOCS"
run_bootstrap_dry "$FIX/mixed-facts/project" "$BOOTSTRAP_DRY_DOCS"
assert_rc "Bootstrap dry-run succeeds for mixed project" 0
assert_has "Bootstrap dry-run selects combined adapter" "PLAN BOOTSTRAP adapter=combined"
[ ! -e "$BOOTSTRAP_DRY_DOCS" ] && ok "Bootstrap dry-run writes no documents" || bad "Bootstrap dry-run writes no documents"

BOOTSTRAP_COVERAGE_DOCS=$(mktemp -d)
rmdir "$BOOTSTRAP_COVERAGE_DOCS"
run_bootstrap_full_coverage "$FIX/mixed-facts/project" "$BOOTSTRAP_COVERAGE_DOCS"
assert_rc "Strict bootstrap rejects unrepresented source" 1
assert_has "Strict bootstrap names unrepresented source" "UNREPRESENTED src/helper.ts"
[ ! -e "$BOOTSTRAP_COVERAGE_DOCS" ] && ok "Strict coverage failure writes no documents" || bad "Strict coverage failure writes no documents"

BOOTSTRAP_EXEMPT_DOCS=$(mktemp -d)
python3 "$INIT" "$BOOTSTRAP_EXEMPT_DOCS" >/dev/null
printf '# MAKE_BODY_COVERAGE_IGNORE\n\n- `src/helper.ts` — helper has no supported lexical entry\n' > "$BOOTSTRAP_EXEMPT_DOCS/MAKE_BODY_COVERAGE_IGNORE.md"
run_bootstrap_full_coverage "$FIX/mixed-facts/project" "$BOOTSTRAP_EXEMPT_DOCS"
assert_rc "Strict bootstrap accepts documented coverage exception" 0
assert_has_file "$BOOTSTRAP_EXEMPT_DOCS/MAKE_BODY_CANDIDATES.md" "Send Order Task" "Documented coverage exception permits candidate seeding"
rm -rf "$BOOTSTRAP_EXEMPT_DOCS"

BOOTSTRAP_STALE_EXEMPT_DOCS=$(mktemp -d)
python3 "$INIT" "$BOOTSTRAP_STALE_EXEMPT_DOCS" >/dev/null
printf '# MAKE_BODY_COVERAGE_IGNORE\n\n- `src/api.ts` — stale exception\n' > "$BOOTSTRAP_STALE_EXEMPT_DOCS/MAKE_BODY_COVERAGE_IGNORE.md"
run_bootstrap_full_coverage "$FIX/mixed-facts/project" "$BOOTSTRAP_STALE_EXEMPT_DOCS"
assert_rc "Strict bootstrap rejects coverage exception with facts" 2
assert_has_file "$BOOTSTRAP_STALE_EXEMPT_DOCS/MAKE_BODY_CANDIDATES.md" "# MAKE_BODY_CANDIDATES" "Stale coverage exception does not seed candidates"
rm -rf "$BOOTSTRAP_STALE_EXEMPT_DOCS"

BOOTSTRAP_DUPLICATE_EXEMPT_DOCS=$(mktemp -d)
python3 "$INIT" "$BOOTSTRAP_DUPLICATE_EXEMPT_DOCS" >/dev/null
printf '# MAKE_BODY_COVERAGE_IGNORE\n\n- `src/helper.ts` — first reason\n- `src/helper.ts` — second reason\n' > "$BOOTSTRAP_DUPLICATE_EXEMPT_DOCS/MAKE_BODY_COVERAGE_IGNORE.md"
run_bootstrap_full_coverage "$FIX/mixed-facts/project" "$BOOTSTRAP_DUPLICATE_EXEMPT_DOCS"
assert_rc "Strict bootstrap rejects duplicate coverage exception" 2
assert_has_file "$BOOTSTRAP_DUPLICATE_EXEMPT_DOCS/MAKE_BODY_CANDIDATES.md" "# MAKE_BODY_CANDIDATES" "Duplicate coverage exception does not seed candidates"
rm -rf "$BOOTSTRAP_DUPLICATE_EXEMPT_DOCS"

BOOTSTRAP_MISMATCH_DOCS=$(mktemp -d)
rmdir "$BOOTSTRAP_MISMATCH_DOCS"
run_bootstrap_adapter "$FIX/code-facts/project" "$BOOTSTRAP_MISMATCH_DOCS" python
assert_rc "Bootstrap rejects Python adapter without Python source" 2
[ ! -e "$BOOTSTRAP_MISMATCH_DOCS" ] && ok "Adapter mismatch writes no documents" || bad "Adapter mismatch writes no documents"
rm -rf "$BOOTSTRAP_MISMATCH_DOCS"

BOOTSTRAP_COMBINED_DOCS=$(mktemp -d)
rmdir "$BOOTSTRAP_COMBINED_DOCS"
run_bootstrap_adapter "$FIX/code-facts/project" "$BOOTSTRAP_COMBINED_DOCS" combined
assert_rc "Bootstrap rejects combined adapter without mixed source" 2
[ ! -e "$BOOTSTRAP_COMBINED_DOCS" ] && ok "Combined adapter mismatch writes no documents" || bad "Combined adapter mismatch writes no documents"
rm -rf "$BOOTSTRAP_COMBINED_DOCS"

BOOTSTRAP_REJECT_DOCS=$(mktemp -d)
python3 "$INIT" "$BOOTSTRAP_REJECT_DOCS" >/dev/null
printf '# preserved facts\n' > "$BOOTSTRAP_REJECT_DOCS/MAKE_BODY_CODE_FACTS.md"
printf '# MAKE_BODY_CANDIDATES\n\n## MB-001\n' > "$BOOTSTRAP_REJECT_DOCS/MAKE_BODY_CANDIDATES.md"
run_bootstrap "$FIX/mixed-facts/project" "$BOOTSTRAP_REJECT_DOCS"
assert_rc "Bootstrap rejects non-empty queue before writes" 2
assert_has_file "$BOOTSTRAP_REJECT_DOCS/MAKE_BODY_CODE_FACTS.md" "# preserved facts" "Bootstrap preserves facts after preflight rejection"
rm -rf "$BOOTSTRAP_REJECT_DOCS"

BOOTSTRAP_AUDIT_FAIL_DOCS=$(mktemp -d)
python3 "$INIT" "$BOOTSTRAP_AUDIT_FAIL_DOCS" >/dev/null
printf '# preserved facts\n' > "$BOOTSTRAP_AUDIT_FAIL_DOCS/MAKE_BODY_CODE_FACTS.md"
printf '# invalid essential domain\n' > "$BOOTSTRAP_AUDIT_FAIL_DOCS/ESSENTIAL_DOMAIN.md"
run_bootstrap "$FIX/mixed-facts/project" "$BOOTSTRAP_AUDIT_FAIL_DOCS"
assert_rc "Bootstrap rejects an invalid staged workspace" 1
assert_has_file "$BOOTSTRAP_AUDIT_FAIL_DOCS/MAKE_BODY_CODE_FACTS.md" "# preserved facts" "Bootstrap preserves facts after staged audit failure"
rm -rf "$BOOTSTRAP_AUDIT_FAIL_DOCS"

ERRF="$HERE/.stderr.$$"
OUT=$(python3 "$HERE/test-bootstrap-rollback.py" "$BOOTSTRAP" 2>"$ERRF")
RC=$?
ERR=$(sed -n '1,$p' "$ERRF")
rm -f "$ERRF"
assert_rc "Bootstrap rolls back after a staged write failure" 0
assert_has "Bootstrap rollback restores baseline" "OK bootstrap rollback restores the baseline"

ERRF="$HERE/.stderr.$$"
OUT=$(python3 "$HERE/test-bootstrap-lock.py" "$BOOTSTRAP" 2>"$ERRF")
RC=$?
ERR=$(sed -n '1,$p' "$ERRF")
rm -f "$ERRF"
assert_rc "Bootstrap rejects a concurrent lock holder" 0
assert_has "Bootstrap lock reports concurrent rejection" "OK bootstrap lock rejects concurrent execution"

ERRF="$HERE/.stderr.$$"
OUT=$(python3 "$HERE/test-bootstrap-source-change.py" "$BOOTSTRAP" "$FIX/mixed-facts/project" 2>"$ERRF")
RC=$?
ERR=$(sed -n '1,$p' "$ERRF")
rm -f "$ERRF"
assert_rc "Bootstrap rejects source changes during staging" 0
assert_has "Bootstrap source change leaves docs unchanged" "OK bootstrap rejects staged source changes"

CANDIDATES_OUT="$HERE/.candidates.$$"
python3 "$EXTRACT" "$FIX/code-facts/expected/MAKE_BODY_CODE_FACTS.md" "$CANDIDATES_OUT"
assert_file_eq "$FIX/candidate-extraction/expected/MAKE_BODY_CANDIDATES.md" "$CANDIDATES_OUT" "System candidate scaffolds are stable"

SUPPRESS_DOCS=$(mktemp -d)
printf '# MAKE_BODY_REJECTED\n\n## MR-001\n\nType:\nsystem-domain\n\nSubject:\nOrders Table\n\nReason:\n- Table is legacy.\n\nEvidence:\n- `migrations/001_orders.sql:1` — CREATE TABLE orders\n\nReplacement:\n-\n' > "$SUPPRESS_DOCS/MAKE_BODY_REJECTED.md"
python3 "$EXTRACT" "$FIX/code-facts/expected/MAKE_BODY_CODE_FACTS.md" "$SUPPRESS_DOCS/MAKE_BODY_CANDIDATES.md"
if grep -qF "Orders Queue Process" "$SUPPRESS_DOCS/MAKE_BODY_CANDIDATES.md" && ! grep -qF "Orders Table" "$SUPPRESS_DOCS/MAKE_BODY_CANDIDATES.md"; then
  ok "Extractor suppresses a rejected scaffold and keeps others"
else
  bad "Extractor suppresses a rejected scaffold and keeps others [out=$(cat "$SUPPRESS_DOCS/MAKE_BODY_CANDIDATES.md")]"
fi
rm -rf "$SUPPRESS_DOCS"
TMP_DOCS=$(mktemp -d)
for f in ESSENTIAL_DOMAIN ESSENTIAL_USECASE SYSTEM_DOMAIN SYSTEM_USECASE; do
  printf '# %s\n' "$f" > "$TMP_DOCS/$f.md"
done
cp "$CANDIDATES_OUT" "$TMP_DOCS/MAKE_BODY_CANDIDATES.md"
run "$TMP_DOCS" MB-001
assert_rc "Generated System Domain candidate is structurally ready" 0
run "$TMP_DOCS" MB-002
assert_rc "Generated queue System UseCase candidate is structurally ready" 0
run "$TMP_DOCS" MB-003
assert_rc "Generated route System UseCase candidate is structurally ready" 0
rm -rf "$TMP_DOCS"
printf 'existing candidate\n' > "$CANDIDATES_OUT"
ERRF="$HERE/.stderr.$$"
python3 "$EXTRACT" "$FIX/code-facts/expected/MAKE_BODY_CODE_FACTS.md" "$CANDIDATES_OUT" 2>"$ERRF"
RC=$?
ERR=$(sed -n '1,$p' "$ERRF")
rm -f "$ERRF" "$CANDIDATES_OUT"
assert_rc "Candidate extractor preserves non-empty queue" 2
case "$ERR" in *"refusing to replace"*) ok "Candidate extractor explains preservation";; *) bad "Candidate extractor explains preservation [err=<$ERR>]";; esac

PROMOTE_PREVIEW="$HERE/.preview.$$"
python3 "$PREPARE" "$FIX/essential-domain" "$FIX/essential-domain/docs" MB-001 "$PROMOTE_PREVIEW"
assert_file_eq "$FIX/essential-domain/expected/ESSENTIAL_DOMAIN.md" "$PROMOTE_PREVIEW/ESSENTIAL_DOMAIN.md" "Promotion preview writes the expected canonical bytes"
assert_has_file "$PROMOTE_PREVIEW/MAKE_BODY_CANDIDATES.md" "# MAKE_BODY_CANDIDATES" "Promotion preview retains candidate queue header"
run_preview_review "$FIX/essential-domain" "$FIX/essential-domain/docs" "$PROMOTE_PREVIEW"
assert_rc "Promotion preview review succeeds" 0
assert_has "Promotion preview review names candidate" "PREVIEW MB-001"
assert_has "Promotion preview review renders canonical diff" "+++ preview/ESSENTIAL_DOMAIN.md"
run_canonical_evidence "$FIX/essential-domain" "$PROMOTE_PREVIEW"
assert_rc "Promoted canonical Evidence is valid" 0
TMP_DOCS=$(mktemp -d)
cp "$FIX/essential-domain/docs"/*.md "$TMP_DOCS/"
python3 "$APPLY" "$PROMOTE_PREVIEW" "$FIX/essential-domain" "$TMP_DOCS"
assert_file_eq "$PROMOTE_PREVIEW/ESSENTIAL_DOMAIN.md" "$TMP_DOCS/ESSENTIAL_DOMAIN.md" "Promotion apply records preview bytes"
printf '\n' >> "$TMP_DOCS/SYSTEM_DOMAIN.md"
ERRF="$HERE/.stderr.$$"
python3 "$APPLY" "$PROMOTE_PREVIEW" "$FIX/essential-domain" "$TMP_DOCS" 2>"$ERRF"
RC=$?
ERR=$(sed -n '1,$p' "$ERRF")
rm -rf "$TMP_DOCS" "$PROMOTE_PREVIEW"; rm -f "$ERRF"
assert_rc "Promotion apply rejects a changed source" 2
case "$ERR" in *"source changed since preview"*) ok "Promotion apply explains stale preview";; *) bad "Promotion apply explains stale preview [err=<$ERR>]";; esac

EVIDENCE_ROOT=$(mktemp -d)
mkdir -p "$EVIDENCE_ROOT/docs" "$EVIDENCE_ROOT/source"
cp "$FIX/essential-domain/docs"/*.md "$EVIDENCE_ROOT/docs/"
cp "$FIX/essential-domain/source/member.ts" "$EVIDENCE_ROOT/source/"
EVIDENCE_PREVIEW="$HERE/.evidence-preview.$$"
python3 "$PREPARE" "$EVIDENCE_ROOT" "$EVIDENCE_ROOT/docs" MB-001 "$EVIDENCE_PREVIEW"
printf '\n// changed after review\n' >> "$EVIDENCE_ROOT/source/member.ts"
ERRF="$HERE/.stderr.$$"
python3 "$APPLY" "$EVIDENCE_PREVIEW" "$EVIDENCE_ROOT" "$EVIDENCE_ROOT/docs" 2>"$ERRF"
RC=$?
ERR=$(sed -n '1,$p' "$ERRF")
rm -rf "$EVIDENCE_ROOT" "$EVIDENCE_PREVIEW"; rm -f "$ERRF"
assert_rc "Promotion apply rejects changed Evidence source" 2
case "$ERR" in *"evidence source changed since preview"*) ok "Promotion apply explains stale Evidence";; *) bad "Promotion apply explains stale Evidence [err=<$ERR>]";; esac

printf '%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]

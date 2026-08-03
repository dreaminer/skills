#!/usr/bin/env sh
set -u

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SCRIPTS="$HERE/../scripts"
pass=0
fail=0

ok() { pass=$((pass + 1)); printf 'ok   - %s\n' "$1"; }
bad() { fail=$((fail + 1)); printf 'FAIL - %s\n' "$1"; }
has() { grep -F "$2" "$1" >/dev/null 2>&1 && ok "$3" || bad "$3"; }

OUT=$(python3 "$SCRIPTS/preflight.py" 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "preflight accepts runtime" || bad "preflight accepts runtime"
printf '%s\n' "$OUT" | grep -F "OK python3" >/dev/null && ok "preflight reports Python" || bad "preflight reports Python"

ROOT=$(mktemp -d)
DOCS="$ROOT/docs"
python3 "$SCRIPTS/init-docs.py" "$DOCS" > "$ROOT/init.out"
for file in ESSENTIAL_DOMAIN ESSENTIAL_USECASE MAKE_BODY_ESSENTIAL_HYPOTHESES MAKE_BODY_CONFLICTS MAKE_BODY_REJECTED; do
  [ -f "$DOCS/$file.md" ] && ok "initializer creates $file" || bad "initializer creates $file"
done
for file in ACCEPTANCE SYSTEM_DOMAIN SYSTEM_USECASE MAKE_BODY_TESTS MAKE_BODY_LOCKS; do
  [ ! -e "$DOCS/$file.md" ] && ok "initializer omits $file" || bad "initializer omits $file"
done

sh "$SCRIPTS/check-body.sh" "$DOCS" > "$ROOT/body.out" 2>&1; RC=$?
[ "$RC" -eq 0 ] && ok "empty Essential body is valid" || bad "empty Essential body is valid"

cat > "$DOCS/ESSENTIAL_DOMAIN.md" <<'EOF'
# ESSENTIAL_DOMAIN

## [Order]

Meaning:
- A customer's confirmed request.

Evidence:
- Human-ratified: this is the business meaning of the observed order behavior.
- Flow evidence: `tests/create-order.test.ts` — a stored order is returned.
EOF

cat > "$DOCS/ESSENTIAL_USECASE.md" <<'EOF'
# ESSENTIAL_USECASE

## [Create Order]

Given:
- A customer has a valid request.

When:
- The customer creates an [Order].

Then:
- The [Order] becomes the customer's confirmed request.

Evidence:
- Human-ratified: the observed behavior represents order creation.
- Flow evidence: `tests/create-order.test.ts` — a stored order is returned.
EOF

sh "$SCRIPTS/check-body.sh" "$DOCS" > "$ROOT/body.out" 2>&1; RC=$?
[ "$RC" -eq 0 ] && ok "ratified Essential body is valid" || bad "ratified Essential body is valid"

sed 's/\[Order\]/[Unknown]/' "$DOCS/ESSENTIAL_USECASE.md" > "$ROOT/bad-usecase.md"
mv "$ROOT/bad-usecase.md" "$DOCS/ESSENTIAL_USECASE.md"
sh "$SCRIPTS/check-body.sh" "$DOCS" > "$ROOT/body.out" 2>&1; RC=$?
[ "$RC" -eq 1 ] && ok "dangling Essential term fails" || bad "dangling Essential term fails"
has "$ROOT/body.out" "DANGLING [Unknown]" "dangling failure names term"

sed 's/\[Unknown\]/[Order]/' "$DOCS/ESSENTIAL_USECASE.md" | grep -v 'Human-ratified:' > "$ROOT/bad-usecase.md"
mv "$ROOT/bad-usecase.md" "$DOCS/ESSENTIAL_USECASE.md"
sh "$SCRIPTS/check-body.sh" "$DOCS" > "$ROOT/body.out" 2>&1; RC=$?
[ "$RC" -eq 1 ] && ok "missing human ratification fails" || bad "missing human ratification fails"
has "$ROOT/body.out" "MISSING Human-ratified Evidence" "ratification failure is explicit"

sed '/Evidence:/a - Human-ratified: corrected and confirmed.' "$DOCS/ESSENTIAL_USECASE.md" > "$ROOT/good-usecase.md"
mv "$ROOT/good-usecase.md" "$DOCS/ESSENTIAL_USECASE.md"
python3 "$SCRIPTS/check-workspace.py" "$ROOT" "$DOCS" > "$ROOT/workspace.out" 2>&1; RC=$?
[ "$RC" -eq 0 ] && ok "workspace audit accepts valid artifacts" || bad "workspace audit accepts valid artifacts"

cat >> "$DOCS/MAKE_BODY_ESSENTIAL_HYPOTHESES.md" <<'EOF'

## EH-001

Status:
- awaiting-human
EOF
cat >> "$DOCS/MAKE_BODY_CONFLICTS.md" <<'EOF'

## MC-001
EOF
cat >> "$DOCS/MAKE_BODY_REJECTED.md" <<'EOF'

## MR-001
EOF

python3 "$SCRIPTS/report-status.py" "$DOCS" > "$ROOT/status.out" 2>&1; RC=$?
[ "$RC" -eq 0 ] && ok "status report succeeds" || bad "status report succeeds"
has "$ROOT/status.out" "ESSENTIAL_DOMAIN=1" "status counts Domain"
has "$ROOT/status.out" "ESSENTIAL_USECASE=1" "status counts UseCase"
has "$ROOT/status.out" "HYPOTHESES_AWAITING_HUMAN=1" "status counts hypotheses"
has "$ROOT/status.out" "CONFLICTS=1" "status counts conflicts"
has "$ROOT/status.out" "REJECTED=1" "status counts rejections"

printf '# preserved\n' > "$DOCS/MAKE_BODY_CONFLICTS.md"
python3 "$SCRIPTS/init-docs.py" "$DOCS" >/dev/null
has "$DOCS/MAKE_BODY_CONFLICTS.md" "# preserved" "initializer preserves existing files"

rm -rf "$ROOT"
printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]

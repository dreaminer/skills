#!/bin/sh
# Regression tests for check-acceptance.py gates that seed-tdd's suite does not reach.
set -eu
export PYTHONDONTWRITEBYTECODE=1

skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
checker="$skill_dir/scripts/check-acceptance.py"
fixture="$skill_dir/../seed-tdd/tests/fixtures/project"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
cp -R "$fixture/." "$scratch/"

# Two inherited use cases: one covered by AC-001, one deliberately held out of v1.
printf '%s\n' '# ESSENTIAL_USECASE' '' '## [Create Order]' '' 'Outcome:' '- ok' \
  '' '## [Cancel Order]' '' 'Outcome:' '- deferred from v1' \
  > "$scratch/docs/ESSENTIAL_USECASE.md"
# Appended to AC-001's Evidence, which is the last field. Evidence is outside the
# contract hash, so the fixture's marker must stay current through this edit.
printf '%s\n' '- ESSENTIAL_USECASE #1 (Create Order)' >> "$scratch/docs/ACCEPTANCE.md"

rc=0
out=$(cd "$scratch" && python3 "$checker" --docs docs 2>&1) || rc=$?
if [ "$rc" -ne 0 ]; then
  printf '%s\n' "a deferred use case must not fail the design-time run (exit $rc)" "$out" >&2
  exit 1
fi
if ! printf '%s' "$out" | grep -q "WARN \[coverage\].*Cancel Order"; then
  printf '%s\n' "deferred use case did not surface as a coverage warning" "$out" >&2
  exit 1
fi
if printf '%s' "$out" | grep -q "Create Order"; then
  printf '%s\n' "a covered use case was reported" "$out" >&2
  exit 1
fi

rc=0
out=$(cd "$scratch" && python3 "$checker" --docs docs --complete 2>&1) || rc=$?
if [ "$rc" -ne 1 ]; then
  printf '%s\n' "completion audit must fail on an uncovered use case (exit $rc)" "$out" >&2
  exit 1
fi
if ! printf '%s' "$out" | grep -q "FAIL \[coverage\].*Cancel Order"; then
  printf '%s\n' "completion audit did not report the uncovered use case" "$out" >&2
  exit 1
fi
if printf '%s' "$out" | grep -q "marker hash is stale"; then
  printf '%s\n' "appending Evidence staled the contract hash" "$out" >&2
  exit 1
fi

# Structural gates, each asserted against a single deliberate corruption.
assert_fails() {
  label=$1
  expect=$2
  rc=0
  out=$(cd "$scratch" && python3 "$checker" --docs docs 2>&1) || rc=$?
  if [ "$rc" -ne 1 ]; then
    printf '%s\n' "$label: expected exit 1, got $rc" "$out" >&2
    exit 1
  fi
  if ! printf '%s' "$out" | grep -q "$expect"; then
    printf '%s\n' "$label: expected '$expect'" "$out" >&2
    exit 1
  fi
}

cp "$scratch/docs/ACCEPTANCE.md" "$scratch/ACCEPTANCE.orig"

sed 's/^- proposed$/- assumed/' "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
assert_fails "invalid Basis" "Basis 'assumed' not in"
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

sed 's/^- integration$/- smoke/' "$scratch/docs/SEED_SYSTEM_TESTS.md" > "$scratch/tests.next"
cp "$scratch/docs/SEED_SYSTEM_TESTS.md" "$scratch/TESTS.orig"
mv "$scratch/tests.next" "$scratch/docs/SEED_SYSTEM_TESTS.md"
assert_fails "invalid Layer" "Layer 'smoke' not in"
cp "$scratch/TESTS.orig" "$scratch/docs/SEED_SYSTEM_TESTS.md"

printf '%s\n' '# SYSTEM_DOMAIN' > "$scratch/docs/SYSTEM_DOMAIN.md"
assert_fails "mixed mode" "SYSTEM_DOMAIN.md coexists"
rm "$scratch/docs/SYSTEM_DOMAIN.md"

rc=0
(cd "$scratch" && python3 "$checker" --docs docs >/dev/null 2>&1) || rc=$?
if [ "$rc" -ne 0 ]; then
  printf '%s\n' "restored fixture should pass again, exited $rc" >&2
  exit 1
fi

printf '%s\n' \
  "OK: a deferred use case warns at design time and fails only the completion audit" \
  "OK: Basis, Layer, and mixed-mode gates each reject their corruption"

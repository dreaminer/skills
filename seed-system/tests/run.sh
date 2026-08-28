#!/bin/sh
# Regression tests for check-acceptance.py gates that seed-tdd's suite does not reach.
set -eu
export PYTHONDONTWRITEBYTECODE=1

skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
checker="$skill_dir/scripts/check-acceptance.py"
fixture="$skill_dir/../seed-tdd/tests/fixtures/project"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM

# Body-only packages can validate definition links before ACCEPTANCE.md exists.
mkdir -p "$scratch/body-only"
printf '%s\n' '# ESSENTIAL USECASE' '' '## [Create Order]' '' 'Outcome:' '- Order exists.' \
  > "$scratch/body-only/ESSENTIAL_USECASE.md"
printf '%s\n' '# SEED BODY CRITERIA' '' \
  '- [x] Q1 → [ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)' \
  > "$scratch/body-only/SEED_BODY_CRITERIA.md"

rc=0
out=$(python3 "$checker" --docs "$scratch/body-only" --links-only 2>&1) || rc=$?
if [ "$rc" -ne 0 ]; then
  printf '%s\n' "body-only link check must pass without ACCEPTANCE.md (exit $rc)" "$out" >&2
  exit 1
fi

sed 's/#create-order/#missing-use-case/' \
  "$scratch/body-only/SEED_BODY_CRITERIA.md" > "$scratch/body-only/CRITERIA.next"
mv "$scratch/body-only/CRITERIA.next" "$scratch/body-only/SEED_BODY_CRITERIA.md"
rc=0
out=$(python3 "$checker" --docs "$scratch/body-only" --links-only 2>&1) || rc=$?
if [ "$rc" -ne 1 ]; then
  printf '%s\n' "broken body-only link must fail (exit $rc)" "$out" >&2
  exit 1
fi
if ! printf '%s' "$out" | grep -q "## fragment '#missing-use-case' not found"; then
  printf '%s\n' "broken body-only link did not report missing fragment" "$out" >&2
  exit 1
fi

cp -R "$fixture/." "$scratch/"

# Two inherited use cases: one covered by AC-001, one deliberately held out of v1.
printf '%s\n' '# ESSENTIAL_USECASE' '' '## [Create Order]' '' 'Outcome:' '- ok' \
  '' '## [Cancel Order]' '' 'Outcome:' '- deferred from v1' \
  > "$scratch/docs/ESSENTIAL_USECASE.md"
# Appended to AC-001's Evidence, which is the last field. Evidence is outside the
# contract hash, so the fixture's marker must stay current through this edit.
printf '%s\n' \
  '- [ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)' \
  >> "$scratch/docs/ACCEPTANCE.md"
printf '%s\n' '# SEED SYSTEM IMPLEMENTATION PROPOSAL' '' '## IP-001' '' \
  'Why:' \
  '- [AC-001 · Return Created Order ID](ACCEPTANCE.md#return-created-order-id) requires an observable result.' \
  > "$scratch/docs/SEED_SYSTEM_IMPL_PROPOSAL.md"

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

sed 's/#create-order/#missing-use-case/' \
  "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
assert_fails "broken artifact link" "## fragment '#missing-use-case' not found"
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

sed 's/ESSENTIAL_USECASE.md#create-order/ESSENTIAL_USECASE.md/' \
  "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
assert_fails "fragmentless artifact link" "definition link has no ## fragment"
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

sed 's/ESSENTIAL_USECASE.md#create-order/SEED_BODY_LATER.md#missing/' \
  "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
assert_fails "missing artifact file" "materialized target not found"
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

sed 's/ESSENTIAL_USECASE.md#create-order/ESSENTIAL_USECAS.md#create-order/' \
  "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
assert_fails "misspelled artifact file" "materialized target not found"
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

sed 's/ESSENTIAL_USECASE.md#create-order/ESSENTIAL_USECASE%FF.md#create-order/' \
  "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
assert_fails "malformed encoded artifact path" "invalid encoded destination"
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

cp "$scratch/docs/SEED_SYSTEM_IMPL_PROPOSAL.md" "$scratch/PROPOSAL.orig"
sed 's/#return-created-order-id/#missing-acceptance/' \
  "$scratch/PROPOSAL.orig" > "$scratch/docs/SEED_SYSTEM_IMPL_PROPOSAL.md"
assert_fails "broken implementation Why link" "## fragment '#missing-acceptance' not found"
cp "$scratch/PROPOSAL.orig" "$scratch/docs/SEED_SYSTEM_IMPL_PROPOSAL.md"

sed 's/ESSENTIAL_USECASE.md#create-order/..\/ESSENTIAL_USECASE.md#create-order/' \
  "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
assert_fails "artifact link escaping docs" "target escapes docs"
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

sed 's/\[ESSENTIAL_USECASE #1 (Create Order)\](ESSENTIAL_USECASE.md#create-order)/ESSENTIAL_USECASE #1 (Create Order)/' \
  "$scratch/ACCEPTANCE.orig" > "$scratch/docs/ACCEPTANCE.md"
rc=0
out=$(cd "$scratch" && python3 "$checker" --docs docs 2>&1) || rc=$?
if [ "$rc" -ne 0 ]; then
  printf '%s\n' "bare pointer warning should not fail (exit $rc)" "$out" >&2
  exit 1
fi
if ! printf '%s' "$out" | grep -q "WARN \[link-format\].*ESSENTIAL_USECASE #1 (Create Order)"; then
  printf '%s\n' "bare pointer did not surface link-format warning" "$out" >&2
  exit 1
fi
cp "$scratch/ACCEPTANCE.orig" "$scratch/docs/ACCEPTANCE.md"

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

# GFM duplicate suffixes and percent-decoded Hangul fragments resolve. A
# broken example inside a fenced block is documentation, not a live pointer.
printf '%s\n' '# SEED_BODY_LATER' '' '## [포인트 사용]' '' '첫 번째' \
  '' '## [포인트 사용]' '' '두 번째' \
  > "$scratch/docs/SEED_BODY_LATER.md"
printf '%s\n' '# SEED_BODY_CRITERIA' '' \
  '- [x] Q1 →' \
  '  [두 번째 정의](SEED_BODY_LATER.md#%ED%8F%AC%EC%9D%B8%ED%8A%B8-%EC%82%AC%EC%9A%A9-1)' \
  '' '```md' \
  '- 예시 → [깨진 예시](ESSENTIAL_USECASE.md#not-a-live-link)' \
  '```' \
  > "$scratch/docs/SEED_BODY_CRITERIA.md"
printf '%s\n' '# SEED_BODY_SYSTEM_PARKING' '' '## SF-001 공지 전달' '' \
  'Trace:' \
  '- [ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order) (scratch: EF-001)' \
  '' 'Evidence:' '- T4 "푸시로 보내면 돼"' \
  > "$scratch/docs/SEED_BODY_SYSTEM_PARKING.md"
rc=0
out=$(cd "$scratch" && python3 "$checker" --docs docs 2>&1) || rc=$?
if [ "$rc" -ne 0 ]; then
  printf '%s\n' "encoded duplicate anchor should resolve (exit $rc)" "$out" >&2
  exit 1
fi
if printf '%s' "$out" | grep -q "WARN \[link-format\].*EF-001"; then
  printf '%s\n' "scratch provenance was treated as a bare definition pointer" "$out" >&2
  exit 1
fi
cp "$scratch/docs/SEED_BODY_CRITERIA.md" "$scratch/CRITERIA.orig"
sed 's/%EC%82%AC%EC%9A%A9-1/%EC%82%AC%EC%9A%A9-missing/' \
  "$scratch/CRITERIA.orig" > "$scratch/docs/SEED_BODY_CRITERIA.md"
assert_fails "continued CRITERIA link" "## fragment '#포인트-사용-missing' not found"
cp "$scratch/CRITERIA.orig" "$scratch/docs/SEED_BODY_CRITERIA.md"

rc=0
(cd "$scratch" && python3 "$checker" --docs docs >/dev/null 2>&1) || rc=$?
if [ "$rc" -ne 0 ]; then
  printf '%s\n' "restored fixture should pass again, exited $rc" >&2
  exit 1
fi

printf '%s\n' \
  "OK: a deferred use case warns at design time and fails only the completion audit" \
  "OK: Basis, Layer, and mixed-mode gates each reject their corruption" \
  "OK: valid artifact links resolve, broken links fail, and bare pointers warn"

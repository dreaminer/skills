#!/bin/sh
set -eu
export PYTHONDONTWRITEBYTECODE=1

skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
checker="$skill_dir/../seed-system/scripts/check-acceptance.py"
fixture="$skill_dir/tests/fixtures/project"
actual=$(python3 "$skill_dir/scripts/contract-markers.py" --docs "$fixture/docs")
expected='AC-001 | @acceptance: AC-001 sha256:29ad8f62a4dbb81a46918997ff29d7c64555818ed709262ee3249662f7b6caf5 | [Return Created Order ID]'

if [ "$actual" != "$expected" ]; then
  printf '%s\n' "unexpected marker output" "expected: $expected" "actual:   $actual" >&2
  exit 1
fi

(cd "$fixture" && python3 "$checker" --docs docs --complete acceptance >/dev/null)

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
cp -R "$fixture/." "$scratch/"

sed '/^Closes:$/,/^Evidence:$/ { /^Evidence:$/!d; }' \
  "$fixture/docs/ACCEPTANCE.md" > "$scratch/docs/ACCEPTANCE.md"
legacy=$(python3 "$skill_dir/scripts/contract-markers.py" --docs "$scratch/docs")
legacy_expected='AC-001 | @acceptance: AC-001 sha256:9840a2ed8f1336ed74e4986b47f09fbd570ddf44c68f8ead5d77e5b63797d2bd | [Return Created Order ID]'
if [ "$legacy" != "$legacy_expected" ]; then
  printf '%s\n' "an AC without Closes changed its legacy hash" \
    "expected: $legacy_expected" "actual: $legacy" >&2
  exit 1
fi
cp "$fixture/docs/ACCEPTANCE.md" "$scratch/docs/ACCEPTANCE.md"

sed -e 's/- proposed/- inherited/' -e 's/T4 (ratified)/T9 (ratified)/' \
  "$scratch/docs/ACCEPTANCE.md" > "$scratch/docs/ACCEPTANCE.md.next"
mv "$scratch/docs/ACCEPTANCE.md.next" "$scratch/docs/ACCEPTANCE.md"
(cd "$scratch" && python3 "$checker" --docs docs --complete acceptance >/dev/null)

sed 's/A valid order request/A priority order request/' \
  "$scratch/docs/ACCEPTANCE.md" > "$scratch/docs/ACCEPTANCE.md.next"
mv "$scratch/docs/ACCEPTANCE.md.next" "$scratch/docs/ACCEPTANCE.md"

if (cd "$scratch" && python3 "$checker" --docs docs --complete acceptance >checker.out 2>&1); then
  printf '%s\n' "stale marker unexpectedly passed completion validation" >&2
  exit 1
fi

if ! grep -q "marker hash is stale" "$scratch/checker.out"; then
  printf '%s\n' "stale marker failure was not reported" >&2
  exit 1
fi

markers="$skill_dir/scripts/contract-markers.py"

empty_docs="$scratch/empty-docs"
mkdir "$empty_docs"
rc=0
python3 "$markers" --docs "$empty_docs" >/dev/null 2>&1 || rc=$?
if [ "$rc" -ne 2 ]; then
  printf '%s\n' "missing ACCEPTANCE.md should exit 2, exited $rc" >&2
  exit 1
fi

rc=0
python3 "$markers" --docs "$fixture/docs" --checker "$scratch/absent-checker.py" >/dev/null 2>&1 \
  || rc=$?
if [ "$rc" -ne 2 ]; then
  printf '%s\n' "missing canonical checker should exit 2, exited $rc" >&2
  exit 1
fi

bad_docs="$scratch/bad-docs"
mkdir "$bad_docs"
printf '%s\n' '# ACCEPTANCE' '' '## not-bracket-form' '' 'ID:' 'BAD' > "$bad_docs/ACCEPTANCE.md"
rc=0
emitted=$(python3 "$markers" --docs "$bad_docs" 2>/dev/null) || rc=$?
if [ "$rc" -ne 1 ]; then
  printf '%s\n' "invalid contract should exit 1, exited $rc" >&2
  exit 1
fi
if [ -n "$emitted" ]; then
  printf '%s\n' "invalid contract emitted a marker: $emitted" >&2
  exit 1
fi

printf '%s\n' \
  "OK: optional Closes preserves legacy hashes; proof or behavioral edits stale markers" \
  "OK: unreadable inputs exit 2, an invalid contract exits 1 and emits no marker"

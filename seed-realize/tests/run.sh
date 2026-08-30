#!/bin/sh
set -eu

export PYTHONDONTWRITEBYTECODE=1
skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
fixture="$skill_dir/../seed-tdd/tests/fixtures/project"

actual=$(python3 "$skill_dir/scripts/realization-markers.py" --docs "$fixture/docs")
expected='IP-001 | @realization: IP-001 sha256:c78f804d34cb7110aee769d7e676097113ba2214ae93c3c8b5d2af762bdc3991 | Exercise the Order creation API through the project acceptance suite.'
if [ "$actual" != "$expected" ]; then
  printf '%s\n' "unexpected realization marker" "expected: $expected" "actual: $actual" >&2
  exit 1
fi

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT HUP INT TERM
mkdir -p "$scratch/docs"
printf '%s\n' '# SEED SYSTEM IMPLEMENTATION PROPOSAL' '' '## not-an-ip' > "$scratch/docs/SEED_SYSTEM_IMPL_PROPOSAL.md"

rc=0
python3 "$skill_dir/scripts/realization-markers.py" --docs "$scratch/docs" >/dev/null 2>&1 || rc=$?
if [ "$rc" -ne 1 ]; then
  printf '%s\n' "invalid proposal must exit 1, got $rc" >&2
  exit 1
fi

rc=0
python3 "$skill_dir/scripts/realization-markers.py" --docs "$scratch/missing" >/dev/null 2>&1 || rc=$?
if [ "$rc" -ne 2 ]; then
  printf '%s\n' "missing proposal must exit 2, got $rc" >&2
  exit 1
fi

printf '%s\n' "OK: realization markers use the canonical proposal hash and reject invalid inputs"

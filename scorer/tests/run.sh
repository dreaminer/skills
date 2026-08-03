#!/bin/sh
set -eu

TEST_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v bun >/dev/null 2>&1; then
  bun test "$TEST_DIR/compare-results.test.mjs"
else
  node --test "$TEST_DIR/compare-results.test.mjs"
fi

node "$TEST_DIR/validate-fixtures.mjs" "$TEST_DIR/fixtures"

if [ "$#" -eq 0 ]; then
  exit 0
fi

if [ "$#" -ne 2 ]; then
  echo "usage: scorer/tests/run.sh [<baseline-results-dir> <candidate-results-dir>]" >&2
  exit 2
fi

node "$TEST_DIR/compare-results.mjs" \
  --fixtures "$TEST_DIR/fixtures" \
  --contract "$TEST_DIR/comparison-contract.json" \
  --baseline "$1" \
  --candidate "$2"

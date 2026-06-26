# SYSTEM_USECASE

## [Persist Order]

Given:
- An [Order] is submitted.

When:
- The system starts [Persist Order].

Then:
- An [Order Row] is written.

Evidence:
- `src/persist-order.ts:12` — database write

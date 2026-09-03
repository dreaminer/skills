# SEED SYSTEM TESTS

Test command:
- project acceptance suite

Test directory:
- tests/acceptance

## MT-001

Acceptance:
- AC-001

Risk:
- The creation response can point the consumer at the wrong [Order], causing follow-up work to
  target another order.

Layer:
- integration

Status:
- green

Test:
- tests/acceptance/order-create.test.txt

Marker:
- @acceptance: AC-001 sha256:29ad8f62a4dbb81a46918997ff29d7c64555818ed709262ee3249662f7b6caf5

Notes:
- Structural fixture for current-hash GREEN validation.

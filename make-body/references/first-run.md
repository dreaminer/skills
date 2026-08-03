# First run

Assume an existing project has a passing process test:

```text
tests/orders/create-order.test.ts
Given a valid request, when the public create command runs, then an order is stored and returned.
```

The current `docs/TEST_FLOWS_RESULT.md` lists that test, records its maintained command, and has an
exact `Status` section containing `- FLOW_TESTS_READY`. Test Flows obtained the regression-fitness
proof before writing that status.

## 1. Preflight and apply the input gate

```sh
python3 scripts/preflight.py
```

Read the result, run its maintained final test-verification command, and inspect the listed test and
reached production decision. If the result is missing or not ready, the test is missing, or the
command fails, stop:

```text
NEEDS_FLOW_EVIDENCE
- Behavior: create order
- Needed observation: the public action produces the stored and returned result
```

Do not author the test inside Make Body.

## 2. Initialize after evidence passes

```sh
python3 scripts/init-docs.py <project>/docs
```

## 3. Draft hypotheses

The observed write-and-return behavior may suggest that a customer creates an Order, but the code
cannot establish whether storage means confirmation, temporary receipt, or something else. Write the
hypothesis and uncertainty to `MAKE_BODY_ESSENTIAL_HYPOTHESES.md`.

Do not create a candidate for a retry test whose behavior is only technical recovery unless a human
recognizes separate business meaning.

## 4. Batch review

Present the proposed Order meaning and Create Order flow together with the test and source evidence.
If the human confirms that storage represents a customer's confirmed request, materialize the
ratified Domain and UseCase entries with `Human-ratified:` Evidence.

## 5. Verify

```sh
python3 scripts/check-workspace.py <project> <project>/docs
python3 scripts/report-status.py <project>/docs
```

Return `ESSENTIAL_READY`. The project tests and `QUICK_UNDERSTANDING.md`, if present, remain
unchanged, as does `TEST_FLOWS_RESULT.md`.

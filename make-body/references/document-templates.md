# Make Body document templates

## Managed paths

```text
docs/ESSENTIAL_DOMAIN.md
docs/ESSENTIAL_USECASE.md
docs/MAKE_BODY_ESSENTIAL_HYPOTHESES.md
docs/MAKE_BODY_CONFLICTS.md
docs/MAKE_BODY_REJECTED.md
```

Preserve all existing files. Files such as `ACCEPTANCE.md`, `SYSTEM_DOMAIN.md`,
`SYSTEM_USECASE.md`, `MAKE_BODY_TESTS.md`, and `MAKE_BODY_LOCKS.md` are not managed by R6.

## ESSENTIAL_DOMAIN.md

```md
# ESSENTIAL_DOMAIN

## [Order]

Meaning:
- A customer's confirmed request to obtain goods.

Evidence:
- Human-ratified: this is the business meaning of the observed order behavior.
- Flow evidence: `tests/orders/create-order.test.ts` — a created order is persisted and returned.
```

## ESSENTIAL_USECASE.md

```md
# ESSENTIAL_USECASE

## [Create Order]

Given:
- A customer has a valid request.

When:
- The customer creates an [Order].

Then:
- The [Order] is available as the customer's confirmed request.

Evidence:
- Human-ratified: the observed behavior represents order creation.
- Flow evidence: `tests/orders/create-order.test.ts` — the request produces a stored order.
```

Every `[Term]` in an Essential UseCase must resolve in `ESSENTIAL_DOMAIN.md`. Canonical entries
require at least one `Human-ratified:` line. `Flow evidence:` is provenance, not ratification.

## MAKE_BODY_ESSENTIAL_HYPOTHESES.md

Keep hypotheses noncanonical until the whole batch is reviewed.

```md
# MAKE_BODY_ESSENTIAL_HYPOTHESES

## EH-001

Type:
- essential-usecase

Subject:
- Create Order

Hypothesis:
Given:
- A customer has a valid request.
When:
- The customer creates an {order}.
Then:
- The {order} becomes the customer's confirmed request.

Observed from:
- `tests/orders/create-order.test.ts` — passing process evidence.
- `src/orders/create.ts:42` — the reached production decision.

Uncertainty:
- Whether persistence represents confirmation or only temporary receipt.

Status:
- awaiting-human
```

Allowed `Type`: `essential-domain | essential-usecase`. Allowed `Status`:
`awaiting-human | ratified | rejected | conflicted`.

Use `{term}` only inside hypotheses. Rewrite ratified hypotheses with canonical `[Term]` references
when materializing them.

## MAKE_BODY_CONFLICTS.md

```md
# MAKE_BODY_CONFLICTS

## MC-001

Subject:
- Order confirmation meaning

Competing meanings:
- Persistence means the order is confirmed.
- Persistence means the order was only received.

Flow evidence:
- `tests/orders/create-order.test.ts`

Why unresolved:
- The executable behavior cannot establish the business interpretation.
```

## MAKE_BODY_REJECTED.md

```md
# MAKE_BODY_REJECTED

## MR-001

Subject:
- Retry Delivery

Reason:
- Human confirmed this is technical recovery, not a separate business UseCase.

Evidence:
- Human-ratified rejection: retry is only an implementation mechanism.
```

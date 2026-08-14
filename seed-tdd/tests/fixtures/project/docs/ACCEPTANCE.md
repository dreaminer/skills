# ACCEPTANCE

## [Return Created Order ID]

ID:
AC-001

Basis:
- proposed

Seam:
- Order creation API

Given:
- A valid order request.

When:
- The customer creates an [Order].

Then:
- The response includes the created [Order] ID.

Evidence:
- T4 (ratified) "return the created order ID from the order creation API"

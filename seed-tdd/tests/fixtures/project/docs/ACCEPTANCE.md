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

Closes:
- [ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)

Evidence:
- T4 (ratified) "return the created order ID from the order creation API"
- [ESSENTIAL_USECASE #1 (Create Order)](ESSENTIAL_USECASE.md#create-order)

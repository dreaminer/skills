# MAKE_BODY_REJECTED

## MR-001

Type:
system-domain

Subject:
Legacy Sessions Table

Reason:
- Table is dead code; no live caller reads or writes it.

Evidence:
- `source/db.ts:1` — orphaned table definition

Replacement:
-

## MR-002

Type:
system-usecase

Subject:
Create Order Handler

Reason:
- Not a domain use case; thin pass-through with no business rule.

Evidence:
- `source/orders.py:1` — pass-through handler

Replacement:
-

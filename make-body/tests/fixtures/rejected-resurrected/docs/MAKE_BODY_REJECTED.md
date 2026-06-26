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

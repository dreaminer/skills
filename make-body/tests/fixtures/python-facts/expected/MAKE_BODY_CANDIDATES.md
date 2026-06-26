# MAKE_BODY_CANDIDATES

## MB-001

Type:
system-domain

Subject:
Orders Table

Content:
- [Orders Table] is created by `CREATE TABLE orders`.

Evidence:
- `migrations/001_orders.sql:1` — CREATE TABLE orders

Blocked by:
-

## MB-002

Type:
system-usecase

Subject:
POST /orders Route

Content:
Given:
- The `POST /orders` route is registered.

When:
- The route dispatches `create_order`.

Then:
- The registered handler is invoked.

Evidence:
- `src/orders.py:1` — @router.post("/orders") -> create_order

Blocked by:
-

## MB-003

Type:
system-usecase

Subject:
Send Order Task

Content:
Given:
- The `send_order` task is registered.

When:
- The task is dispatched.

Then:
- The registered handler is invoked.

Evidence:
- `src/orders.py:7` — @app.task -> send_order

Blocked by:
-

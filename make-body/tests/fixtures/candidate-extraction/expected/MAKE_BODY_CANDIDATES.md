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
Orders Queue Process

Content:
Given:
- The `orders` queue process is registered.

When:
- The process dispatches `createOrder`.

Then:
- The registered handler is invoked.

Evidence:
- `src/orders.ts:8` — queue.process("orders", createOrder);

Blocked by:
-

## MB-003

Type:
system-usecase

Subject:
POST /orders Route

Content:
Given:
- The `POST /orders` route is registered.

When:
- The route dispatches `createOrder`.

Then:
- The registered handler is invoked.

Evidence:
- `src/orders.ts:7` — router.post("/orders", createOrder);

Blocked by:
-

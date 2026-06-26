# MAKE_BODY_CODE_FACTS

Adapter: python-lexical-v1

## direct-call

- `src/orders.py:3` — repository.insert
- `src/orders.py:4` — event_bus.emit
- `src/orders.py:9` — queue.enqueue

## effect-call

- `src/orders.py:3` — order = await repository.insert(request)
- `src/orders.py:4` — await event_bus.emit("order.created", order)
- `src/orders.py:9` — queue.enqueue(order_id)

## exported-symbol

- `src/orders.py:2` — create_order
- `src/orders.py:8` — send_order

## http-entry

- `src/orders.py:1` — @router.post("/orders") -> create_order

## schema-constraint

- `migrations/001_orders.sql:2` — id TEXT PRIMARY KEY,
- `migrations/001_orders.sql:3` — customer_id TEXT NOT NULL,
- `migrations/001_orders.sql:4` — FOREIGN KEY (customer_id) REFERENCES customers(id)

## schema-table

- `migrations/001_orders.sql:1` — orders

## worker-entry

- `src/orders.py:7` — @app.task -> send_order

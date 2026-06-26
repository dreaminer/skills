# MAKE_BODY_FLOW_TRACES

Generated from: MAKE_BODY_CODE_FACTS.md

Trace limits:
- lexical entrypoint trace only
- handler symbol resolution uses exported-symbol facts
- direct/effect calls are limited to the resolved handler body
- not a call graph proof
- not a Make Body candidate

Project schema facts:
- `migrations/001_orders.sql:1` — orders
- `migrations/001_orders.sql:2` — id TEXT PRIMARY KEY,
- `migrations/001_orders.sql:3` — customer_id TEXT NOT NULL,
- `migrations/001_orders.sql:4` — FOREIGN KEY (customer_id) REFERENCES customers(id)

## FT-001 POST /orders -> create_order

Entry:
- `src/orders.py:1` — @router.post("/orders") -> create_order

Handler:
- `src/orders.py:2` — async def create_order(request):

Calls:
- `src/orders.py:3` — repository.insert — order = await repository.insert(request)
- `src/orders.py:4` — event_bus.emit — await event_bus.emit("order.created", order)

Effects:
- `src/orders.py:3` — order = await repository.insert(request)
- `src/orders.py:4` — await event_bus.emit("order.created", order)

Trace limits:
- handler body: `src/orders.py:2-6`
- lexical 1-hop only
- not a System UseCase candidate

## FT-002 task -> send_order

Entry:
- `src/orders.py:7` — @app.task -> send_order

Handler:
- `src/orders.py:8` — def send_order(order_id):

Calls:
- `src/orders.py:9` — queue.enqueue — queue.enqueue(order_id)

Effects:
- `src/orders.py:9` — queue.enqueue(order_id)

Trace limits:
- handler body: `src/orders.py:8-9`
- lexical 1-hop only
- not a System UseCase candidate

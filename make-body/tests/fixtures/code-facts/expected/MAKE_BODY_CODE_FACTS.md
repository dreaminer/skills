# MAKE_BODY_CODE_FACTS

Adapter: typescript-node-lexical-v1

## direct-call

- `src/orders.ts:2` — orderRepository.insert
- `src/orders.ts:3` — eventBus.emit
- `src/orders.ts:7` — router.post
- `src/orders.ts:8` — queue.process

## effect-call

- `src/orders.ts:2` — const order = await orderRepository.insert(request);
- `src/orders.ts:3` — await eventBus.emit("order.created", order);

## exported-symbol

- `src/orders.ts:1` — createOrder

## http-entry

- `src/orders.ts:7` — router.post("/orders", createOrder);

## schema-constraint

- `migrations/001_orders.sql:2` — id TEXT PRIMARY KEY,
- `migrations/001_orders.sql:3` — customer_id TEXT NOT NULL,
- `migrations/001_orders.sql:4` — FOREIGN KEY (customer_id) REFERENCES customers(id)

## schema-table

- `migrations/001_orders.sql:1` — orders

## worker-entry

- `src/orders.ts:8` — queue.process("orders", createOrder);

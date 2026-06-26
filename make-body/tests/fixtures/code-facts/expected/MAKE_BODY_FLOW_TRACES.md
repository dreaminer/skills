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

## FT-001 POST /orders -> createOrder

Entry:
- `src/orders.ts:7` — router.post("/orders", createOrder);

Handler:
- `src/orders.ts:1` — export async function createOrder(request: { id: string }) {

Calls:
- `src/orders.ts:2` — orderRepository.insert — const order = await orderRepository.insert(request);
- `src/orders.ts:3` — eventBus.emit — await eventBus.emit("order.created", order);

Effects:
- `src/orders.ts:2` — const order = await orderRepository.insert(request);
- `src/orders.ts:3` — await eventBus.emit("order.created", order);

Trace limits:
- handler body: `src/orders.ts:1-5`
- lexical 1-hop only
- not a System UseCase candidate

## FT-002 queue orders -> createOrder

Entry:
- `src/orders.ts:8` — queue.process("orders", createOrder);

Handler:
- `src/orders.ts:1` — export async function createOrder(request: { id: string }) {

Calls:
- `src/orders.ts:2` — orderRepository.insert — const order = await orderRepository.insert(request);
- `src/orders.ts:3` — eventBus.emit — await eventBus.emit("order.created", order);

Effects:
- `src/orders.ts:2` — const order = await orderRepository.insert(request);
- `src/orders.ts:3` — await eventBus.emit("order.created", order);

Trace limits:
- handler body: `src/orders.ts:1-5`
- lexical 1-hop only
- not a System UseCase candidate

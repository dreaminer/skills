export async function createOrder(request: { id: string }) {
  const order = await orderRepository.insert(request);
  await eventBus.emit("order.created", order);
  return order;
}

router.post("/orders", createOrder);
queue.process("orders", createOrder);

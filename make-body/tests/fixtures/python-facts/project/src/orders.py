@router.post("/orders")
async def create_order(request):
    order = await repository.insert(request)
    await event_bus.emit("order.created", order)
    return order

@app.task
def send_order(order_id):
    queue.enqueue(order_id)

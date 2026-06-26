@app.task
def send_order(order_id):
    queue.enqueue(order_id)

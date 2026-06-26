export type Order = { id: string };
export type OrderRow = { id: string; payload: string };
export function persist(order: Order): OrderRow {
  return { id: order.id, payload: JSON.stringify(order) };
}

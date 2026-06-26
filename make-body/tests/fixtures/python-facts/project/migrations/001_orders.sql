CREATE TABLE orders (
  id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

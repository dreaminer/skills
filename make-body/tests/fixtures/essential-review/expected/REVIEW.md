# Candidate Review: MB-001

## MB-001
Type: essential-domain
Subject: Customer Order
Content:
- [Customer Order] is what a buyer places; it is recorded as an order row.
Evidence:
- `source/order.ts:2` — order row field
Blocked by:
-

# Evidence Context: source/order.ts:2
     1 | export class Order {
>    2 |   constructor(readonly orderRow: string) {}
     3 | }

# Essential Review: MB-001

This candidate asserts business meaning that code alone cannot confirm. It is never
auto-promoted; promotion requires explicit human confirmation. Judge it with the protocol
in `references/essential-review.md`.

## Co-located canonical System terms (lexical)
- [Order Row]

## Reviewer checklist
- [ ] Subject names a business concept, not a System artifact (endpoint, table, queue, protocol).
- [ ] Every claim in Content is meaning a human can confirm, not an inference the code forces.
- [ ] The cited Evidence is consistent with the asserted meaning.
- [ ] Meaning the code cannot establish (intent, policy, ownership, cardinality, lifecycle) is named, not assumed.
- [ ] Verdict recorded as approve / revise / reject per references/essential-review.md.

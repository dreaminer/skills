# Essential recovery

## Qualify flow evidence

Accept a flow as input only when all are available and current:

- a `TEST_FLOWS_RESULT.md` whose exact `Status` section contains `- FLOW_TESTS_READY`;
- a project-owned evidence-test path listed by that result;
- a maintained final test-verification command from the result that passes in the current project;
- observed starting facts, trigger, and outcome;
- the production decision reached.

If any item is absent, report `NEEDS_FLOW_EVIDENCE`. Treat the ready result as Test Flows'
regression-fitness receipt. Do not reproduce `test-flows`, rerun mutations, or require its internal
red-proof trace inside Make Body.

## Read the optional guide

Use `QUICK_UNDERSTANDING.md` only to order and navigate candidate flows. Re-open the qualified test
and relevant production source before drafting each hypothesis. A guide line without qualified test
evidence cannot support recovery.

## Translate without copying

For each qualified flow:

1. state the observed System behavior literally;
2. remove route, storage, queue, retry, transaction, framework, and protocol machinery;
3. ask what business identity, responsibility, policy, invariant, or outcome might remain;
4. draft it as a hypothesis, including what executable behavior cannot establish;
5. produce no candidate when only a vocabulary substitution remains.

Do not force one-to-one mapping. Group tests that implement the same possible business flow. Keep
technical behaviors such as retry, serialization, caching, and transaction mechanics out of
Essential unless a human confirms their business significance.

## Evidence direction

Tests and source justify only the observed side of a hypothesis. They may show that a value is stored,
returned, rejected, retried, or emitted. They cannot by themselves establish intent, ownership,
permission, obligation, finality, or product policy.

Canonical Evidence therefore contains both:

- `Flow evidence:` for the observed behavior; and
- `Human-ratified:` for the confirmed meaning.

## Existing Essential body

Prefer augmentation or correction over duplication. When a new hypothesis overlaps an existing
entry, present the exact merge or replacement in the batch review. Preserve the existing entry until
the human ratifies the change.

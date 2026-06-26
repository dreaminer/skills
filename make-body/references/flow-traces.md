# Flow Traces

`trace-system-flows.py <project-root> <facts-file>` renders a deterministic observation report from
`MAKE_BODY_CODE_FACTS.md`. It is a navigation aid for writing System candidates, not a candidate
generator and not canonical documentation.

## Contract

- Reads only the fact index plus cited project source.
- Starts from `http-entry` and `worker-entry` facts.
- Resolves handler symbols through `exported-symbol` facts.
- Prints direct calls and effect calls inside the resolved handler body.
- Prints project schema facts once for nearby persistence context.
- Marks missing handlers as `unresolved` instead of failing.

## Limits

- Lexical 1-hop trace only.
- No runtime dispatch, framework middleware, DI container, import graph, type resolution, or full call
  graph proof.
- No Essential inference, System UseCase wording, candidate approval, or promotion.
- Treat every trace line as an investigation pointer; inspect cited source before queueing a
  candidate.

# Candidate Extraction

Generate a candidate only when its Type, Subject, Content, and every Evidence pointer can be stated
without product intent that is absent from code. Keep one claim or execution registration per
candidate. A candidate is a proposal, never a canonical fact until its approval gate passes.
System proposals are approved by direct code evidence plus mechanical gates; Essential proposals are
approved by a human.

## Mechanical seed scope

`extract-typescript-candidates.py` consumes `MAKE_BODY_CODE_FACTS.md` and emits only these System
candidates:

| Fact | Type | Claim boundary |
|---|---|---|
| `schema-table` | System Domain | the named SQL table is created |
| `http-entry` | System UseCase | the registered method/path dispatches its named handler |
| `worker-entry` | System UseCase | the named queue process dispatches its named handler |

The script preserves the literal SQL name, method/path, queue name, handler identifier, and evidence
line. It refuses to replace a queue with candidates unless `--replace` is supplied. A generated
candidate with no exact supported shape is omitted rather than guessed.

## Reviewed extraction

Read each evidence pointer plus direct callers/callees before adding a candidate. Use observed state
writes, constraints, conditions, and effects to decide whether a code fact supports a claim. Use
plain-text `Subject`; cite every supporting location. Do not turn names such as `save`, `member`, or
`status` into business policy merely because they appear in code.

Start reviewed extraction from System UseCases. Use `trace-system-flows.py` to get a lexical
entrypoint-to-handler observation map, then inspect the cited source. Split and block on the System
Domain terms needed by those flows. Promote the System Domain terms before their dependent System
UseCases.
Generate an Essential candidate only when its statement survives removal of endpoint, table, queue,
transaction, protocol, and framework details. If two plausible meanings remain, create a conflict
record with both evidence sets instead of choosing one.

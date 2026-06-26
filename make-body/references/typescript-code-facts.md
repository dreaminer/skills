# TypeScript Code-Fact Adapter

`collect-typescript-facts.py` is the first Make Body adapter. It reads only `.ts`, `.tsx`, `.js`,
`.jsx`, and `.sql` files and writes a stable `MAKE_BODY_CODE_FACTS.md` index. It excludes generated
declarations/minified/generated files and `.git`, `node_modules`, `vendor`, build, distribution,
coverage, cache, and Next output directories.

## Fact kinds

| Kind | Lexical signal |
|---|---|
| `http-entry` | `app`, `router`, or `server` HTTP method registration |
| `worker-entry` | worker, queue processing, consumer, schedule, cron, or message registration |
| `exported-symbol` | exported function, class, or variable declaration |
| `direct-call` | dotted or simple call expression, excluding function declarations |
| `effect-call` | save, insert, update, delete, emit, publish, enqueue, send, commit, or rollback call |
| `schema-table` | SQL `CREATE TABLE` |
| `schema-constraint` | SQL primary/foreign key, unique, or not-null constraint |

## Limits

This adapter is lexical, not a TypeScript compiler or a semantic analyser. It does not resolve type
aliases, imports, overloads, decorators, dynamic dispatch, reflection, generated runtime code, or
calls assembled at runtime. A matching line is an investigation pointer only. Make Body must read
the cited code and its direct callers/callees, and must record uncertainty as a conflict rather than
turning a weak lexical match into a domain claim.

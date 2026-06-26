# Python Code-Fact Adapter

`collect-python-facts.py` reads only `.py` and `.sql` files and writes a stable
`MAKE_BODY_CODE_FACTS.md` index. It excludes `.git`, `node_modules`, `vendor`, build, distribution,
coverage, cache, virtualenv, and `__pycache__` directories.

## Fact kinds

| Kind | Lexical signal |
|---|---|
| `http-entry` | `@app` or `@router` HTTP method decorator immediately followed by a function |
| `worker-entry` | `@app.task`, `@celery.task`, or `@task` decorator immediately followed by a function |
| `exported-symbol` | public function, method, or class declaration |
| `direct-call` | dotted or simple call expression, excluding basic control-flow keywords |
| `effect-call` | save, insert, update, delete, emit, publish, enqueue, send, commit, or rollback method call |
| `schema-table` | SQL `CREATE TABLE` |
| `schema-constraint` | SQL primary/foreign key, unique, or not-null constraint |

## Combined indexes

`collect-code-facts.py` runs the supported TypeScript/JavaScript and Python adapters that match the
project's in-scope source files, then merges facts by kind into one deterministic index. Use
`extract-code-facts-candidates.py` for that combined index so TypeScript and Python route, worker,
and table scaffolds are seeded without one adapter overwriting the other.

## Limits

This adapter is lexical, not a Python interpreter or import resolver. It does not resolve imports,
decorator factories, framework routing tables assembled elsewhere, dependency injection, dynamic
dispatch, reflection, inheritance, runtime registration, or calls assembled at runtime. A matching
line is an investigation pointer only. Make Body must read the cited code and its direct
callers/callees, and must record uncertainty as a conflict rather than turning a weak lexical match
into a domain claim.

# Evidence Contract

Every candidate Evidence entry has this exact form:

```md
- `relative/path.ts:12` — concise observation
```

`check-evidence.py` requires the pointer to be under the supplied project root, in Make Body input
scope, a readable source file, and a non-empty existing line. It validates provenance only. It cannot
establish that the observation text proves the candidate claim; inspect code and callers/callees for
that decision.

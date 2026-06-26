# Adapter Contract

The contract a new language fact adapter (Rust, Go, Java, …) must satisfy before it is added. It is
the abstract version of the two shipped adapters — [TypeScript](typescript-code-facts.md) and
[Python](python-code-facts.md) — which are its only worked instances. This document adds **no** new
behavior; it fixes the boundary so a future adapter cannot quietly widen make-body's scope.

A new adapter is a documentation + script + fixture change only. It never touches classification,
promotion, the consistency gate, or any Essential path.

## What an adapter is

A `collect-<lang>-facts.py` script that reads in-scope source for one language and writes a stable
`MAKE_BODY_CODE_FACTS.md` index. It observes; it never decides meaning. Everything below is an
obligation, not a suggestion.

## 1. Lexical and non-semantic

The adapter is a lexical scanner, not a compiler, interpreter, type checker, or import/DI resolver.
It must not resolve imports, type aliases, overloads, decorator factories, dynamic dispatch,
reflection, inheritance, routing tables assembled elsewhere, runtime registration, or calls assembled
at runtime. A matched line is an **investigation pointer only**. This is the principle the whole skill
rests on; an adapter that breaks it (e.g. by building a real call graph) is rejected outright — see
`DESIGN.md`.

## 2. Fact index format

Append facts to the shared `MAKE_BODY_CODE_FACTS.md` under per-kind sections, byte-stably (same input
→ identical bytes, deterministic ordering). The combined collector (`collect-code-facts.py`) merges
adapters by kind without one overwriting another, so a new adapter must slot into the existing kind
sections rather than invent a parallel layout. Declare the adapter's version tag in the index header
(e.g. `typescript-node-lexical-v1`).

## 3. Evidence pointer format

Every fact cites source with the single Evidence pointer form defined once in
[`evidence.md`](evidence.md): `` `relative/path.ext:line` — concise observation ``. Do **not** restate
or vary that format here or in the adapter doc — link `evidence.md`. The pointer must be under the
project root, in Make Body input scope, a readable file, and a non-empty existing line, exactly as
`check-evidence.py` enforces.

## 4. Supported fact kinds

Reuse the shared kinds; do not introduce a kind a downstream consumer does not understand. The current
set, identical across adapters:

`http-entry`, `worker-entry`, `exported-symbol`, `direct-call`, `effect-call`, `schema-table`,
`schema-constraint`.

Each new adapter maps its language's lexical signals onto these kinds (see the two adapter docs for
how TypeScript and Python do it). Adding a new kind is a skill-wide change, not an adapter-local one,
and must be justified the same way any new rule is (`DESIGN.md`, "How to use this when expanding").

## 5. Exclusion rules

Read only the language's source extensions (plus `.sql` where the adapter owns schema facts). Exclude
generated/minified/declaration files and `.git`, `node_modules`, `vendor`, build, distribution,
coverage, cache, virtualenv, and framework-output directories — matching the shipped adapters so scope
stays consistent across languages.

## 6. Coverage wiring

Every in-scope source file the adapter recognizes must be reachable by `report-fact-coverage.py`: a
file with no fact surfaces as `UNREPRESENTED` so it gets deliberate review, and is cleared only by a
real fact or a documented `MAKE_BODY_COVERAGE_IGNORE.md` entry. The adapter must not silently drop a
supported file.

## 7. Extractor scope (what candidates an adapter may seed)

A paired `extract-<lang>-candidates.py` may turn selected lexical facts into **conservative,
code-literal, System-only** candidate scaffolds — never Essential meaning, never a promotion. It must
honor rejection suppression: skip any scaffold whose `(Type, Subject, Evidence pointer)` matches a
record in `MAKE_BODY_REJECTED.md` (via `rejected_index.py`). It must refuse to overwrite a non-empty
queue.

## 8. Golden fixtures and tests

A new adapter is not done until `tests/run.sh` covers it with golden fixtures: a sample project plus
expected `MAKE_BODY_CODE_FACTS.md` (and expected candidate scaffolds) compared byte-for-byte, the same
way the TypeScript and Python adapters are pinned. Determinism is a test obligation, not a hope.

## Checklist for a new adapter

- [ ] Lexical only — no compiler/resolver/semantic step (§1)
- [ ] Writes the shared, byte-stable fact index with a version tag (§2)
- [ ] Cites Evidence in the `evidence.md` form, validated by `check-evidence.py` (§3)
- [ ] Maps signals onto the existing fact kinds; no private kinds (§4)
- [ ] Applies the shared exclusion rules (§5)
- [ ] Recognized files are visible to coverage; none silently dropped (§6)
- [ ] Extractor seeds only conservative System scaffolds, rejection-suppressed, non-overwriting (§7)
- [ ] Golden fixtures + `tests/run.sh` cases pin determinism (§8)

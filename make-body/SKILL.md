---
name: make-body
description: Reconstructs a code-only project by building a code-observed System Domain/UseCase body first, then deriving human-confirmed Essential Domain/UseCase language. Use only when the user explicitly invokes `$make-body`, `/make-body`, or asks to run the `make-body` skill by name.
---

# Make Body

## Purpose

Recover the behavior implemented by code into a body with separate truth-makers:

```text
code facts → System UseCase/System Domain → Essential hypotheses → Essential confirmation
```

This is reconstruction, not product design. Never invent policy, actor, permission, cardinality,
lifecycle, or outcome that code does not directly support.

## Requirements

- Requires `python3` 3.10+ and POSIX `sh`; no third-party Python packages are required.
- Before the first command in a new environment, run `python3 scripts/preflight.py`.
- If preflight fails, report the missing requirement and stop before changing project files. Do not
  install Python or packages unless the user explicitly asks.

## Input scope

Read production source, schemas, migrations, route/controller/command/worker registrations, and their
direct callers and callees. Tests may corroborate a candidate but never provide its only evidence.
Exclude README/product documents, user conversation, generated code, vendor code, lockfiles, build
output, and caches.

Every candidate starts code-observed. Code that does not directly support a claim produces no
candidate. System canonical entries may be promoted from direct code evidence after the mechanical
gates pass. Essential entries are business meaning hypotheses until a human confirms them. When code
conflicts or cannot establish a distinction, record the conflict; do not propose a new business rule
to fill the gap.

## Canonical body

Use exactly these files under the target project's `docs/` directory:

- `ESSENTIAL_DOMAIN.md`
- `ESSENTIAL_USECASE.md`
- `SYSTEM_DOMAIN.md`
- `SYSTEM_USECASE.md`

Working files:

- `MAKE_BODY_CODE_FACTS.md`
- `MAKE_BODY_COVERAGE_IGNORE.md`
- `MAKE_BODY_CANDIDATES.md`
- `MAKE_BODY_CONFLICTS.md`
- `MAKE_BODY_REJECTED.md`

Create missing files from [document templates](references/document-templates.md). Replace an existing
file only when it is clearly a prior Make Body output; otherwise ask how to preserve it.

System documents record code-observed execution facts. Essential documents record human-confirmed
domain meaning derived from code-observed behavior. Do not represent Essential content as canonical
only because code appears to imply it.

## Classification

Classify every candidate with one layer and one shape.

- **Essential Domain** — business identity, state, relationship, eligibility, ownership, permission,
  invariant, or outcome that remains meaningful without implementation machinery.
- **Essential UseCase** — Given/When/Then business flow connecting Essential Domain terms.
- **System Domain** — row, transaction, endpoint, protocol, worker, queue, cache, retry, storage, or
  other execution concept required to run the behavior.
- **System UseCase** — Given/When/Then execution flow connecting System concepts.

Do not classify by identifier spelling alone. If technical machinery is required to state the claim,
keep it System. If the layer is genuinely ambiguous, record a conflict rather than promoting it to
Essential.

References are directional:

| Source | May reference |
|---|---|
| Essential Domain | Essential Domain |
| Essential UseCase | Essential Domain |
| System Domain | System Domain, Essential Domain |
| System UseCase | System Domain, Essential Domain, Essential UseCase, System UseCase |

## Candidate contract

Queue one atomic claim per `MB-{nnn}` entry. `Subject` is plain text: it is the sole source for the
Review subject and the canonical `## [Subject]` header created on Yes. Do not infer it from Content.

```md
## MB-001

Type:
essential-usecase

Subject:
Approve Order

Content:
Given:
- [Order] is pending.

When:
- An approval is submitted.

Then:
- [Order] becomes approved.

Evidence:
- `src/orders/approve.ts:42` — state transition
- `src/http/orders.ts:18` — entry point

Blocked by:
-
```

Use `Blocked by` only for unconfirmed Domain subjects required by Content. A candidate is ready iff
that section is empty or a bare `-`.

Ready System candidates can be auto-approved only when their Content is a direct execution fact
bounded by their Evidence and no conflict or stale input exists. Ready Essential candidates always
need human confirmation before Promote.

## Workflow

New to this skill? Read [first run — a worked trace](references/first-run.md) once before your first
real run: one small session end to end, so the `AWAIT_GATE → consistency gate → READY → apply`
hand-off and the stop conditions are seen connected. It adds no rules.

1. **Initialize documents.** Create missing Make Body files without replacing any existing project
   file:

   ```sh
   python3 scripts/init-docs.py <docs-dir>
   ```

   To run initialization, supported-adapter fact collection, safe System candidate seeding, and the
   workspace audit in one command, use
   `python3 scripts/bootstrap-make-body.py <project-root> <docs-dir>`. It refuses a non-empty
   candidate queue before creating or changing any workspace file. Add `--dry-run` to print the
   selected adapter and exact command plan without creating or changing files. A forced
   `--adapter` must match the source: `typescript` accepts TypeScript/JavaScript/SQL, `python`
   accepts Python, and `combined` requires both TypeScript/JavaScript and Python.
   The actual run stages every generated document and completes the workspace audit before it
   applies the changed documents; a failed stage leaves the workspace unchanged. On success it
   prints each managed document as `CREATED` or `UPDATED` for immediate review. If applying a
   staged file fails, bootstrap restores the already-applied managed documents to their baseline.
   Concurrent bootstrap runs for the same document directory are rejected; `--dry-run` remains
   read-only and does not acquire that lock. Bootstrap also rejects the staged result if supported
   source files change before it applies the documents.
   Use `--require-full-coverage` when every in-scope supported source file must produce at least
   one fact; it rejects the staged result rather than treating an unrepresented file as complete.
   To document a deliberate exception, add one line to `MAKE_BODY_COVERAGE_IGNORE.md`:
   `- \`relative/path.ts\` — concrete reason`. The path must be an existing in-scope
   supported source and must currently have no facts; unreasoned, out-of-scope, or stale
   exclusions, including duplicate paths, fail the gate.

2. **Map code facts.** For a mixed TypeScript/Python project, prefer:

   ```sh
   python3 scripts/collect-code-facts.py <project-root> <docs-dir>/MAKE_BODY_CODE_FACTS.md
   ```

   It combines supported adapters without one overwriting the other. For a single TypeScript/Node
   project, run:

   ```sh
   python3 scripts/collect-typescript-facts.py <project-root> <docs-dir>/MAKE_BODY_CODE_FACTS.md
   ```

   The generated index records lexical entry points, direct calls, effects, and schema facts with
   `path:line` pointers. It is not domain language or candidate evidence by itself: inspect cited
   code, direct callers, and direct callees before deriving a claim. See
   [TypeScript code-fact adapter](references/typescript-code-facts.md).
   For a Python project, use `collect-python-facts.py` with the same arguments. It recognizes
   route and task decorators, calls, effects, and SQL facts; it remains lexical and non-semantic.
   See [Python and combined code-fact adapters](references/python-code-facts.md). Adding a new
   language (Rust, Go, Java, …) means writing an adapter to the
   [adapter contract](references/adapter-contract.md), not extending an existing one.
   Run `python3 scripts/report-fact-coverage.py <project-root> <facts-file>` and inspect every
   `UNREPRESENTED` file before deciding that it has no recoverable domain meaning.
3. **Seed mechanical System candidates.** Generate only code-literal System candidates from the
   index. Use System UseCase seeds as the map of executable behavior; SQL/table seeds are System
   Domain terms needed by those flows. The command refuses to replace a non-empty queue without
   `--replace`:

   ```sh
   python3 scripts/extract-typescript-candidates.py \
     <docs-dir>/MAKE_BODY_CODE_FACTS.md <docs-dir>/MAKE_BODY_CANDIDATES.md
   ```

   It creates candidates for SQL tables, HTTP route registrations, and queue-process registrations.
   It never generates Essential candidates. See
   [candidate extraction](references/candidate-extraction.md).
   Use `extract-python-candidates.py` for a Python fact index, or
   `extract-code-facts-candidates.py` for a mixed fact index.
4. **Extract the System body first.** Read the cited source and its direct callers/callees. Start
   discovery from System UseCases: routes, commands, workers, cron jobs, event consumers,
   transactions, and other executable triggers. Trace conditions, state changes, persistence,
   messages, and observable effects. Split the System Domain terms required by each flow, and block
   the UseCase candidate on those terms. Discovery is UseCase-first; canonical promotion remains
   Domain-before-dependent-UseCase.

   Generate a deterministic trace report before writing reviewed candidates:

   ```sh
   python3 scripts/trace-system-flows.py <project-root> <docs-dir>/MAKE_BODY_CODE_FACTS.md
   ```

   The trace report is an observation map, not a candidate queue and not canonical documentation.
   Use it to find entrypoint handlers, direct calls, effect calls, and nearby schema facts; inspect
   the cited source before queueing any candidate. See [flow traces](references/flow-traces.md).

   ```sh
   python3 scripts/show-evidence.py <project-root> <relative-path:line> --radius 3
   ```

   Use `python3 scripts/find-symbol-uses.py <project-root> <symbol>` to locate lexical caller and
   callee references before turning an observation into a candidate. It is a navigation aid, not a
   call-graph proof.
5. **Derive Essential hypotheses.** After the directly evidenced System behavior is understood,
   remove endpoint, table, queue, transaction, protocol, framework, storage, retry, and cache
   language. Queue an Essential candidate only when a business meaning remains. Ask a human whether
   that meaning is real; code can suggest it but does not confirm it.
6. **Classify and compare.** Assign Type and Subject. Merge only source-equivalent duplicates. Record
   unresolved contradictions in `MAKE_BODY_CONFLICTS.md` and keep them out of canonical files. Run:

   ```sh
   python3 scripts/check-conflicts.py <project-root> <docs-dir>
   ```

   It validates conflict record structure and evidence provenance, but never chooses between claims.
   Run `python3 scripts/check-candidate-duplicates.py <docs-dir>` to reject source-equivalent
   duplicates before review; it does not consider merely similar candidates duplicates.
7. **Audit the workspace.** Run:

   ```sh
   python3 scripts/check-workspace.py <project-root> <docs-dir>
   ```

   It checks canonical documents, conflict records, and every unblocked candidate, then prints status.
   Blocked candidates are reported but not treated as malformed. Add `--require-full-coverage` to
   fail on an in-scope supported source without a fact or documented coverage exception.
8. **Select the next candidate.** Run:

   ```sh
   python3 scripts/next-candidate.py <project-root> <docs-dir>
   ```

   It selects only unblocked candidates that pass the checks below, ordering assigned Types as
   System Domain, System UseCase, Essential Domain, then Essential UseCase. It does not classify or
   approve. See [candidate selection](references/selection.md).
9. **Check the selected candidate.** Run both structural and provenance checks:

   ```sh
   sh scripts/check-question.sh <docs-dir> <MB-id>
   python3 scripts/check-evidence.py <project-root> <docs-dir> <MB-id>
   ```

   The latter requires every Evidence pointer to name an in-scope source file and non-empty source
   line. It does not judge whether the cited code proves the claim. See
   [evidence contract](references/evidence.md).
   Render the candidate and all of its code contexts with
   `python3 scripts/review-candidate.py <project-root> <docs-dir> <MB-id>` when a human or maintainer
   must inspect the evidence. To select and render the next ready candidate in one read-only command,
   use
   `python3 scripts/review-next-candidate.py <project-root> <docs-dir>`.
   For an `essential-domain`/`essential-usecase` candidate the renderer adds, only for that Type, a
   deterministic review frame — a fixed reviewer checklist and the canonical System terms lexically
   co-located with the candidate. The frame is an aid, not a verdict: it never authors the
   candidate's questions or decides what code cannot establish. Judge an Essential candidate with the
   [essential review protocol](references/essential-review.md); it is never auto-promoted.
10. **Prepare a promotion preview.** Run:

   ```sh
   python3 scripts/prepare-promotion.py <project-root> <docs-dir> <MB-id> <preview-dir>
   ```

   This first runs `check-question.sh`, then creates a complete staged body and runs `check-body.sh`.
   Review the staged target file and staged candidate queue, not a regenerated textual summary.
   To select the next ready candidate and create its preview without changing the documents, use
   `python3 scripts/prepare-next-promotion.py <project-root> <docs-dir> <preview-dir>`.
11. **Approve and apply.** Apply exactly the staged bytes only after the right approval gate.
   Essential candidates always require human confirmation. A direct System candidate may be
   auto-approved only after it passes the deterministic gates (evidence, conflict, duplicate,
   stale-input, preview) **and** the consistency gate below. If the agent judges a System candidate
   ambiguous, do not call the auto-promotion script; send it to maintainer review.

   To select the next ready System candidate, audit the workspace, and prepare a reviewed preview,
   run:

   ```sh
   python3 scripts/promote-next-system.py <project-root> <docs-dir> <preview-dir>
   ```

   It refuses an Essential next candidate with `NEEDS_HUMAN` (exit 3) and applies nothing. For a
   System candidate it prepares and reviews a byte-stable preview, then prints
   `AWAIT_GATE -- <MB-id> ...` and exits 0 **without applying** — the consistency gate is a
   coordinator (LLM) step that cannot run inside this deterministic script. Exit 0 here means
   "proceed to the gate", never "applied" (this script never applies). To inspect the staged
   diffs first, run `python3 scripts/review-promotion-preview.py <project-root> <docs-dir>
   <preview-dir>` (it never applies anything).

   On `AWAIT_GATE`, run the **consistency gate** on that candidate before applying — see
   [consistency gate](references/consistency-gate.md). It is one-hop and keyed to the P0 contract:

   - `READY` → apply exactly the prepared preview:

     ```sh
     python3 scripts/apply-promotion.py <preview-dir> <project-root> <docs-dir>
     ```

     Apply refuses if any source canonical file, candidate queue, or cited Evidence source changed
     after preparation; it verifies the written digests and runs `check-body.sh` again after the write.
   - Anything else (evidence mismatch, an unbounded claim, or any uncertain check, `UNKNOWN`) →
     `NEEDS_HUMAN`. Discard the preview and **do not apply**; the candidate stays in
     `MAKE_BODY_CANDIDATES.md` for human review. `READY` is additive — it never replaces the
     deterministic gates, and the gate never rewrites-then-reapplies on its own (deferred; see
     `DESIGN.md`).

   When a human **explicitly rejects** a candidate (legacy, accidental, wrong implementation, or not
   the business meaning), append an `## MR-{nnn}` record to `MAKE_BODY_REJECTED.md` and delete the
   candidate from the queue; a candidate merely awaiting review is not rejected. On any other
   correction, discard the preview, update only from code-backed evidence, and prepare a new one.
   Record an unresolved conflict when no code resolves it. See
   [promotion contract](references/promotion.md).
12. **Report state.** Run `python3 scripts/report-status.py <docs-dir>` before returning. Report its
    counts and paths without treating a count as a domain decision.

## Mechanical contracts

Every script is deterministic provenance, never a domain decision: it checks, selects, renders,
hashes, collects, or stages, but never classifies, infers, resolves a conflict, or approves meaning.
The per-script contract — inputs, guarantees, and the explicit "it never …" boundary for each — lives
in [script contracts](references/script-contracts.md). Future progress scripts may count candidates
but must not decide domain meaning.

Before returning, use `report-status.py` to report canonical counts by the four Types, open candidate
count, unresolved conflict count, and all output paths.

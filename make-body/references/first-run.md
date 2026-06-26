# First Run — A Worked Trace

One small session, end to end, so the loop's steps are seen connected rather than as separate rules.
This adds **no** new rules — every step here is governed by `SKILL.md` and the references. It exists
to reduce drift on the part that is easy to miss in prose: the
`AWAIT_GATE → consistency gate → READY → apply` hand-off, and where the loop **stops** instead of
applying. Read it once before your first real run.

The example project is tiny — a mixed TypeScript/Python service:

```text
project/
  migrations/001_orders.sql   CREATE TABLE orders (id TEXT PRIMARY KEY);
  src/api.ts                  router.post("/orders", createOrder);
  src/helper.ts               (utility — no lexical entry point)
  workers/send_order.py       @app.task def send_order(order_id): ...
```

Commands below write only under `project/docs/` and a throwaway `<preview>` dir; the source tree is
read-only. Paths in the output are illustrative — yours will differ.

---

## 0. Preflight — check the environment before touching files

```console
$ python3 scripts/preflight.py
OK python3 3.10.12
OK sh /usr/bin/sh
OK no third-party Python packages required
```

If preflight fails, report the missing requirement and **stop** before changing project files. Do not
install anything unless the user asks.

---

## 1. Bootstrap — initialize, collect facts, seed safe System candidates, audit

One command does init + supported-adapter fact collection + code-literal System seeding + workspace
audit, staging everything through the audit before it writes:

```console
$ python3 scripts/bootstrap-make-body.py project project/docs
OK BOOTSTRAP adapter=combined docs=project/docs
CREATED ESSENTIAL_DOMAIN.md
CREATED ESSENTIAL_USECASE.md
CREATED SYSTEM_DOMAIN.md
CREATED SYSTEM_USECASE.md
CREATED MAKE_BODY_CODE_FACTS.md
CREATED MAKE_BODY_COVERAGE_IGNORE.md
CREATED MAKE_BODY_CANDIDATES.md
CREATED MAKE_BODY_CONFLICTS.md
CREATED MAKE_BODY_REJECTED.md
```

The adapter is auto-detected (`combined` here, because the tree has both TypeScript and Python).
Seeding is **code-literal and System-only** — it never invents Essential meaning. Three scaffolds are
queued: one System Domain (the table) and two System UseCases (the route and the task). Use
`--dry-run` first to see the plan without writing, and `--require-full-coverage` to fail on any
in-scope supported file with no fact (here `src/helper.ts` would need a one-line entry in
`MAKE_BODY_COVERAGE_IGNORE.md`).

`MAKE_BODY_REJECTED.md` is a managed file: bootstrap stages any existing archive so a prior rejection
is still suppressed on a re-run (see step 7).

---

## 1.5. Trace executable flows — inspect the map before writing reviewed candidates

Bootstrap seeds only conservative scaffolds. Before enriching or adding System candidates, render the
lexical flow map and inspect the cited source:

```console
$ python3 scripts/trace-system-flows.py project project/docs/MAKE_BODY_CODE_FACTS.md
# MAKE_BODY_FLOW_TRACES

## HTTP route POST /orders
- handler: createOrder
- entry: `src/api.ts:1`
...
```

The trace is an observation map, not canonical documentation and not a candidate queue. Use it to
choose what source to read next; do not promote from the trace alone.

---

## 2. See what is queued — status, then read the next candidate with its code

```console
$ python3 scripts/report-status.py project/docs
ESSENTIAL_DOMAIN=0
ESSENTIAL_USECASE=0
SYSTEM_DOMAIN=0
SYSTEM_USECASE=0
CANDIDATES_OPEN=3
CANDIDATES_READY=3
CANDIDATES_BLOCKED=0
CONFLICTS_UNRESOLVED=0
REJECTED_RECORDED=0
...
```

`review-next-candidate.py` selects the next ready candidate **and** renders each Evidence pointer's
source window in one read-only command — this is what a human or the gate reads, never a paraphrase:

```console
$ python3 scripts/review-next-candidate.py project project/docs
# Candidate Review: MB-001

## MB-001
Type:
system-domain
Subject:
Orders Table
Content:
- [Orders Table] is created by `CREATE TABLE orders`.
Evidence:
- `migrations/001_orders.sql:1` — CREATE TABLE orders
Blocked by:
-

# Evidence Context: migrations/001_orders.sql:1
>    1 | CREATE TABLE orders (id TEXT PRIMARY KEY);
NEXT MB-001 system-domain Orders Table
```

Selection order is System Domain → System UseCase → Essential Domain → Essential UseCase, lowest
`MB-` among ready candidates. So `MB-001 Orders Table` (a System Domain term) comes first.

---

## 3. Promote the next System candidate — stops at `AWAIT_GATE`, applies nothing

```console
$ python3 scripts/promote-next-system.py project project/docs <preview>
OK code-facts
OK canonical-body
OK canonical-evidence
OK conflicts
OK rejected
OK candidate-duplicates
OK candidate-MB-001
OK candidate-MB-002
OK candidate-MB-003
...
OK WORKSPACE
NEXT MB-001 system-domain Orders Table
OK -- preview for MB-001: <preview>
PREVIEW MB-001
--- current/SYSTEM_DOMAIN.md
+++ preview/SYSTEM_DOMAIN.md
@@ -1 +1,9 @@
 # SYSTEM_DOMAIN
+
+## [Orders Table]
+
+Meaning:
+- [Orders Table] is created by `CREATE TABLE orders`.
+
+Evidence:
+- `migrations/001_orders.sql:1` — CREATE TABLE orders
... (also removes MB-001 from the candidate queue)
PREVIEW_READY_FOR_APPROVAL_GATE
AWAIT_GATE -- MB-001 system-domain Orders Table preview=<preview>
```

This script audits the workspace, picks the next ready candidate, and prepares a **byte-stable
preview** — then stops. `AWAIT_GATE` with **exit 0 means "proceed to the gate," never "applied."**
This script never applies. If the next candidate is Essential, the script refuses with
`NEEDS_HUMAN`, exit 3, and no preview — see step 7. If the agent judges a System candidate
ambiguous, it does not call this script; it sends the candidate to maintainer review instead. To
inspect the staged diffs again without applying, run `review-promotion-preview.py`.

---

## 4. The consistency gate — the one LLM hop the script cannot do

`promote-next-system.py` is deterministic, so it cannot judge **fidelity** — whether the `Content`
claims more than the cited code shows. That is the consistency gate's only job
(protocol: `references/consistency-gate.md`). Spawn **one** sub-agent in a **separate context** and
give it **only** the candidate's `Content` and its `Evidence` pointers — withhold the Type, the
canonical docs, and the preview/diffs. It reads `migrations/001_orders.sql:1` directly with
`show-evidence.py`:

```text
Content:  - [Orders Table] is created by `CREATE TABLE orders`.
Evidence: - `migrations/001_orders.sql:1` — CREATE TABLE orders
Source read: CREATE TABLE orders (id TEXT PRIMARY KEY);
```

The claim adds no cardinality, lifecycle, ownership, or policy beyond what the line states → it is
bounded by its evidence → verdict **`READY`**. `READY` is **additive**: the candidate already passed
the deterministic gates in step 3; the consistency gate never replaces them.

---

## 5. Apply — only on `READY`, exactly the prepared bytes

```console
$ python3 scripts/apply-promotion.py <preview> project project/docs
OK -- applied approved preview for MB-001.

$ cat project/docs/SYSTEM_DOMAIN.md
# SYSTEM_DOMAIN

## [Orders Table]

Meaning:
- [Orders Table] is created by `CREATE TABLE orders`.

Evidence:
- `migrations/001_orders.sql:1` — CREATE TABLE orders
```

`apply-promotion.py` refuses if any source canonical file, the candidate queue, or a cited Evidence
source changed after preparation; it verifies the written digests and re-runs `check-body.sh` after
the write. Status now shows the term promoted and the queue shrunk:

```console
$ python3 scripts/report-status.py project/docs
SYSTEM_DOMAIN=1
CANDIDATES_OPEN=2
CANDIDATES_READY=2
...
```

---

## 6. The loop continues — run the same command for the next candidate

```console
$ python3 scripts/promote-next-system.py project project/docs <preview2>
...
OK WORKSPACE
NEXT MB-002 system-usecase POST /orders Route
AWAIT_GATE -- MB-002 ...
```

Repeat steps 3–5 for `MB-002` (the route), then `MB-003` (the task), until no ready System candidate
remains. Essential terms are **not** auto-promoted: they surface as `NEEDS_HUMAN` and require human
confirmation before Promote.

---

## 7. Where the loop stops instead of applying

Three real stop conditions — none of them silently apply:

- **Gate verdict is anything but `READY`** (evidence mismatch, an unbounded claim, or any check the
  sub-agent cannot resolve) → `NEEDS_HUMAN`. **Discard the preview, apply nothing**; the candidate
  stays in `MAKE_BODY_CANDIDATES.md` for human review. In P0 the gate does not rewrite-then-reapply.

- **Next candidate is Essential, or a System candidate is ambiguous** → Essential candidates are
  refused by `promote-next-system.py` with `NEEDS_HUMAN` (exit 3) **before** any preview is built.
  For an ambiguous System candidate, the agent does not call the script; it sends the candidate to
  maintainer review instead.

- **A human explicitly rejects a candidate** (legacy, accidental, wrong implementation, or not the
  business meaning). This is a **two-step** action — append the record *and* delete the candidate.
  Doing only the first is caught:

  ```console
  # appended an MR-001 record for "Send Order Task" but MB-003 is still in the queue:
  $ python3 scripts/check-rejected.py project project/docs
  RESURRECTED MB-003 matches a rejected record: system-usecase Send Order Task
  FAIL -- 1 rejected violation(s).
  ```

  Delete `MB-003` from the queue, and the check passes:

  ```console
  $ python3 scripts/check-rejected.py project project/docs
  OK -- 1 rejected record(s) are structurally valid.
  ```

  The rejection key is per pointer — any queued candidate that re-cites a rejected
  `(Type, Subject, Evidence pointer)` triple is flagged, even alongside new evidence. This is what
  keeps a rejected scaffold from being re-seeded (the extractors read the archive and skip it) or
  hand-re-queued. A merely *awaiting-review* candidate is **not** rejected — it stays queued.

---

## 8. Report state before returning

```console
$ python3 scripts/report-status.py project/docs
SYSTEM_DOMAIN=1
CANDIDATES_OPEN=1
CANDIDATES_READY=1
REJECTED_RECORDED=1
...
```

Report the counts and paths; never treat a count as a domain decision.

---

### What this trace shows

- Bootstrap seeds **code-literal, System-only** scaffolds; nothing Essential is invented.
- `promote-next-system.py` stops at `AWAIT_GATE` (exit 0 = "go to the gate," **not** applied); only
  `apply-promotion.py` writes, and only after a `READY` verdict.
- The consistency gate sees **Content + Evidence only**, in a separate context, and checks fidelity —
  it is additive to the deterministic gates, never a replacement.
- `READY` → apply the exact prepared bytes; anything else → `NEEDS_HUMAN`, discard, leave queued.
- Explicit rejection is two steps (record **and** dequeue); the per-pointer resurrection guard makes
  the half-done case fail loud rather than silently re-queue.

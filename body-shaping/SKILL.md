---
name: body-shaping
description: Recovers and shapes a project's ubiquitous language and use cases into Essential/System domain documents. Use when a project lacks clear domain language, when analyzing legacy code for business meaning, or when preparing a project so future changes follow confirmed domain and use-case language.
---

# Body Shaping

## Purpose

Give an unstructured project a confirmed domain body: recover the real vocabulary scattered
across code, tests, docs, and schemas, split it into Essential (the conceptual domain model and
flow) and System (the runtime/implementation model and execution flow), and write down only what a
human has confirmed — so later work runs on a settled vocabulary.

This skill does not generate production code, refactor code, add validators, or enforce builds.

## Operating Loop

Run this loop exactly. Recover can add candidates again whenever new project evidence appears; it is
not a one-time phase.

1. **Recover** — read in-scope project sources and queue evidence-backed, atomic candidates.
2. **Select** — run `sh scripts/next-question.sh <docs-dir>` to choose the next ready candidate.
3. **Re-evaluate** — remove duplicates, surface clashes, or restore a missing blocker before asking.
4. **Consistency gate** — for an `observed` candidate, validate the question's `Content` against its
   evidence; a `proposed` candidate skips this and goes straight to Review.
5. **Question check** — run `sh scripts/check-question.sh <docs-dir> <Q-id>`; only a structurally
   ready queued question may reach Review.
6. **Review** — show the validated, question-check-clean question and ask the human whether its content is
   right.
7. **Promote** — apply the human's answer to the canonical body, queue, or rejection archive.
8. **Check** — run `sh scripts/check-body.sh <docs-dir>` as a post-write assertion before returning
   to Select.

## The two jobs — keep them separate

Everything here is one of two jobs. Do not mix them.

- **Classification — the LLM's job.** Every candidate has a `Type:` = **layer** × **shape**.
  - **layer**: Essential (conceptual domain model/flow) or System
    (runtime/implementation model/flow)
  - **shape**: Domain (a concept / state / policy / responsibility / relationship) or UseCase
    (Given/When/Then flow connecting domain concepts)

  The LLM assigns layer and shape by *reading the candidate* — its form and the domain terms
  around it. **Never ask the user which layer or shape something is**; the LLM reads this
  better than the user. The same word may yield both an Essential and a System candidate.
  Classify with one pass:

  - **Shape**:
    - Domain = meaning, identity, ownership, cardinality, allowed values, lifecycle states,
      policies, responsibilities, relationships, stable invariants, or "what this term means /
      is not".
    - UseCase = confirmed domain terms connected by a Given/When/Then flow. Given states context,
      When states an event/action, and Then states a resulting state, responsibility,
      relationship, or observable outcome. If nothing happens in the candidate, it is probably
      Domain.
  - **Layer**:
    - Essential = domain stakeholders can confirm it without knowing how the software runs. It uses
      conceptual domain vocabulary and remains true regardless of runtime machinery.
    - System = maintainers or operators confirm it through runtime/implementation behavior. It
      needs execution machinery such as storage, protocol, transaction, queue, cache, worker, query,
      or pagination.

- **Confirmation — the human's job.** Only a human confirms **content**: what a term means,
  and whether a use case is real and correctly worded. **Nothing becomes canonical without
  human confirmation — all four documents, System included.** The human confirms substance;
  the LLM files it in the right document.

The focal unit of a question is a **use-case flow**. A use case is built from domain terms, so its
layer follows from the vocabulary needed to make the flow true: an Essential use case connects
Essential domain concepts; a System use case connects System domain concepts.

## Canonical Outputs

Canonical body (confirmed content only):

- `docs/ESSENTIAL_DOMAIN.md`   — Essential × Domain
- `docs/ESSENTIAL_USECASE.md`  — Essential × UseCase
- `docs/SYSTEM_DOMAIN.md`      — System × Domain
- `docs/SYSTEM_USECASE.md`     — System × UseCase

Working queue: `docs/QUESTION_CANDIDATE.md` — unconfirmed candidates, each with an
LLM-assigned `Type:`.

Rejected archive: `docs/REJECTED.md` — candidates the user explicitly rejected, kept so a
later Recover pass does not resurrect them.

See [document templates](references/document-templates.md). New to this skill? Read
[a worked first run](references/first-run.md) once — one session traced end to end.

## Modes

### Recover

Read project-owned docs, code, tests, and schemas, and queue candidates. Exclude generated artifacts,
third-party or vendored code, and package lockfiles. Read in this order:

1. README, docs, product docs, UI text
2. tests
3. routes, controllers, API endpoints
4. service, use-case, domain code
5. database schema, migrations

For each finding, prepare a candidate and assign its `Type:` (layer × shape) by **what it
means and how it is used — not by how the identifier is spelled**, its plain **`Subject:`** (the
single canonical header name a Yes creates), and its **`Basis:`**:
`observed` when a file `path:line` is the claim's truth-maker, `proposed` when human confirmation is
(a new design, or a current domain fact not yet pinned to code; a file may still be cited as
provenance). Split first, then set `Type`, `Subject`, and `Basis` together at queue time — a candidate without a
valid `Basis` is malformed, and `scripts/next-question.sh` fails loud on it (`invalid-basis`, exit 3)
rather than asking or dropping it silently. Queue it as a `Q-{nnn}`
row. Nothing is canonical yet. Stop when every source is read once and every term is either
queued or already canonical.

A candidate contains **one independently confirmable claim**: one term meaning, state, policy,
responsibility, relationship, invariant, or one Given/When/Then flow. Split a finding that contains
multiple independent claims before queueing it. This keeps `Yes` equal to approval of the exact
displayed claim, not a bundle of claims.

When splitting a source candidate into children, copy the relevant **primary evidence** into every
child: keep file evidence at its exact `path:line`, or copy the full proposed-flow sentence for a
new design. `from use-case Q-{nnn}` is provenance context only; it is never sufficient evidence for
a child on its own.

Do not copy scenario bullets directly into use cases. Split each scenario finding first:

1. Conceptual term meaning, state, policy, responsibility, relationship, or invariant ->
   Essential Domain candidate.
2. Conceptual Given/When/Then flow connecting Essential domain concepts -> Essential UseCase
   candidate.
3. Runtime/implementation term, protocol, storage, cache, queue, identifier, or process ->
   System Domain candidate.
4. Runtime/implementation Given/When/Then flow connecting System domain concepts -> System UseCase
   candidate.

Example split:

- Bad Essential UseCase: "A [Member] belongs to exactly one [Organization] and is evaluated only
  inside its own [Organization]."
- Essential Domain: "A [Member] belongs to exactly one [Organization]."
- Essential Domain: "A [Member] is not shared across [Organizations]."
- Essential UseCase:
  - Given: "A [Member] belongs to an [Organization]."
  - When: "The platform evaluates the [Member] for domain behavior."
  - Then: "The platform evaluates that [Member] only inside the [Member]'s own [Organization]."

Example layer split:

- Essential UseCase:
  - Given: "A [Business Record] is `draft`."
  - When: "[Business Approval] executes."
  - Then: "The [Business Record] becomes `approved`, and one [Business Obligation] is created for
    each [Eligible Recipient]."
- System UseCase:
  - Given: "A [Database Transaction] has inserted [Obligation Row] records and committed."
  - When: "A worker receives a [Notification Channel] event."
  - Then: "The worker finds the relevant [Live Session] records and enqueues work in the
    [Bounded Worker Queue]."

### Review

Ask one question at a time, about **content** only, in the shape *"is this right?"*. Show the
candidate (a domain term, or a use-case flow) and offer two answers (rendered in the project's
language):

- **Yes** — correct, exactly as written.
- **Something else** — free text: a correction, a different wording, "that's legacy /
  accidental", "not sure", etc.

Use this review-question shape every time. Render the field labels and content in the user's or
project's language; keep the field structure stable:

```text
Progress: <resolved>/<total> resolved (<confirmed> confirmed + <rejected> rejected; <open> open).
Target: <Essential|System> × <Domain|UseCase>
Subject: <term or use-case name>
Why this layer × shape: <classification reason>
Content:
<domain definition or Given/When/Then flow>
Is this right?
- <Yes option>
- <Something else / correction option>
```

The top `Progress:` line is whatever `sh scripts/progress.sh <docs-dir>` prints — relay it verbatim,
parenthesised breakdown and all; never reword or recount by hand. **Evidence is not shown in the question.** It stays in the candidate's
`QUESTION_CANDIDATE.md` entry and is surfaced only when the user hesitates or asks where the
candidate came from — provenance is look-it-up-on-doubt information, not part of the first-level
question. The queued `Content` is exactly the bare candidate text shown below the displayed
`Content:` label. `Is this right?` is a presentation-only prompt; never store it in the candidate.

The user approves the **content under the displayed classification**. `Subject` is the selected
candidate's stored `Subject:` field — the same name Promote uses for the canonical `## [Subject]`
header. Do not ask the user to choose
Essential vs System or Domain vs UseCase. If the user challenges the classification, treat it as a
correction, re-evaluate the candidate, and present a revised approval question.

Rules:

- Ask questions in the order `sh scripts/next-question.sh <docs-dir>` prints — run it, do not reason
  out the order by hand. It prioritises **Essential before System** over the ready candidates, so an
  Essential candidate discovered *after* System questions began preempts the remaining System ones;
  it skips blocked candidates and prints `queue-empty` or `none-ready` when there is nothing to ask.
  (The full ordering rule lives in the script header.)
- A use-case question whose terms are not all confirmed is **blocked** (non-empty `Blocked by`); the
  selector skips it. Its `Type:` is already assigned; ask the unconfirmed domain term first — that
  term is itself a ready candidate. Once its terms are all confirmed the use case becomes ready.
- A domain term may be sourced from a **proposed use-case flow alone**, with no other
  evidence (a brand-new design). It is an ordinary candidate — its evidence is that sentence,
  and it is confirmed like any other.

**Consistency gate (internal — runs before the question is shown).** The user confirms domain
**content** while trusting that the question was faithfully derived from the project — the domain is
*not* fully in the user's head, that is why this skill runs. This gate owns that derivation fidelity
(evidence → `Content`) so a question's claims never overshoot their evidence. It is keyed on the
selected candidate's **`Basis`**, the third token `scripts/next-question.sh` prints:

- **`observed`** → run the gate. A file `path:line` backs the claim, so a separate-context validator
  reads that source directly and confirms the question's `Content` does not overshoot it before the
  question is shown.
- **`proposed`** → **skip the gate** (no spawn); go straight to Review. Human confirmation is the
  truth-maker — no file `path:line` backs the claim (a cited file is provenance, not its truth-maker),
  so there is nothing to validate against. Such a claim is asked as an ordinary `Is this right?` /
  `Something else` question, not presented as source-grounded.

Before running the gate the first time in a session, read
[`references/consistency-gate.md`](references/consistency-gate.md) and follow it exactly — the
validator's restricted inputs, the `READY` / `REWORK` contract (and its `SAFE_CONTENT` /
`REMOVE_EXACTLY` dual-write), and the single-hop rule all live there, and the gate is unsound if
they are not followed. (Why this shape: see `DESIGN.md`.)

**Question check (mechanical — runs before Review).** Once the question `Content` is final — after
`READY`, `REWORK`, or the direct proposed-candidate path — run:

```
sh scripts/check-question.sh <docs-dir> <Q-id>
```

It reads the selected queue entry's stored `Type:`, `Subject:`, `Basis:`, `Content:`, and `Blocked
by:` fields plus the canonical body. It verifies only mechanical readiness: exact field values, a
ready (empty) `Blocked by:`, no candidate notation in `Content`, and references resolvable in the
layers allowed by `Type:`. It does not judge evidence, wording, classification meaning, or whether
same-named concepts mean the same thing.

On failure, do not ask the human yet. Repair the queue's structural issue — for example a missed
`Blocked by`, invalid `Subject:`, or layer-invalid reference — then Re-evaluate. Do not change the
candidate's meaning merely to make the question check pass. On success, show the question. A
`Something else` response never promotes the old candidate: update or requeue it, then return to
Re-evaluate and run the question check on its new form.

### Promote

The LLM's step: read the user's answer and act. The user answers; they do not operate this step.

- **Yes** → write the candidate into the document for its already-assigned layer × shape;
  delete it from the queue; remove the now-confirmed term from every other queued entry's
  `Blocked by` list. Deterministic — no judgment.
- **Something else** → read the free text and act on it. For example: a replacement wording →
  write that wording; "legacy / accidental / wrong" → demote to `REJECTED.md` (delete only if
  the user says to discard it); a hedge or "not sure" → keep the item in the queue; a partial
  yes → write the confirmed part and requeue the rest.

Do not promote without a clear **Yes** or an explicit instruction in the free text. Do not
change canonical meaning without the user's confirmation.

> **Do not turn "Something else" into a fixed classification table.** Disagreements are too
> varied to enumerate; read them and use judgment. Pre-tabling this path is exactly what
> bloated earlier versions of this skill.

### Check (mechanical post-write assertion — runs itself, not a judgment)

`[ ]` vs `{ }` is a lookup, not a decision: a term is canonical **iff** it is a `## [X]`
header in one of the four canonical docs. Do not rest this on prose discipline — verify it.

After **every Yes Promote**, run the bundled checker against the project's real docs dir:

```
sh scripts/check-body.sh <docs-dir>      # default: docs; path is relative to this skill's base dir
```

It exits non-zero on a **dangling reference** — an inline `[ref]` whose confirming `## [ref]`
header is missing in the layer where it must resolve — or if candidate notation `{X}` leaked into a
canonical doc. Reference resolution is **directional**: the concrete layer may reference the abstract
one, never the reverse (System refs may resolve in Essential; Essential refs never in a System doc).
`check-body.sh` enforces the exact per-layer targets and names them in its failure output. This is not
a second approval of the user's answer: the question check already established that the approved
Content was structurally askable. A failure means the actual write violated the canonical-body
invariant or the body changed between the question check and Promote. Stop before selecting another
question, diagnose that write/state mismatch, and do not change canonical meaning without the user's
confirmation. Inline code (backtick spans) is ignored,
so `` `[Term]` `` placeholders and `` `messages:{groupId}` `` examples do not false-positive.
Markdown links `[label](url)` and `[X]` inside triple-backtick fenced blocks are **not** stripped
— wrap them in inline backticks if you need them in a canonical doc.
Fix any failure before asking the next question.

### Re-evaluate

Before asking the candidate the selector picked:

1. If another queued candidate in the same `Type:` expresses the **same independently confirmable
   claim**, even with different wording, keep one candidate, merge its primary evidence, and delete
   the duplicate. This is a meaning judgment, not a fixed matching table.
2. If the same word is already canonical in the same `Type:` **with the same meaning**,
   delete the question (already canonical).
3. If the same word is already canonical in the same `Type:` **with a different meaning**,
   do not propose it blindly — surface the clash and ask the user to disambiguate (use a
   different term, or confirm it is the same concept). The same word in another layer is a
   parallel meaning, not a clash.
4. Else, if its sentence still has unconfirmed terms, keep it blocked and ask the needed
   domain term first.
5. Else, ask it.

If step 1 or 2 deletes the candidate, or step 4 finds it blocked by a term the stale `Blocked by` missed,
run the selector again for the next one. (Step 3 is a real clash — resolve it with the user, do not
skip.) The selector orders; Re-evaluate is the per-candidate judgment the selector cannot make.

## Rules

- No fixed forbidden-word list for Essential language; treat technical-looking words as
  questions, not rejections.
- Apply the classification pass above; do not maintain a second layer/shape rule set here.
- Use-case flows become canonical only from already-confirmed domain language.
- Canonical meaning never changes without user confirmation. Formatting fixes are allowed;
  meaning changes are not.
- Before changing or renaming a confirmed term, trace every document that references it (its
  bracketed `[Term]` occurrences) — those are its dependents.
- `[Term]` (confirmed) vs `{Term}` (candidate) is mechanical, not a judgment — a selected candidate
  must pass `scripts/check-question.sh` before Review, and the real body must pass
  `scripts/check-body.sh` after Yes Promote (no dangling `[ref]`, no stray `{candidate}` in the
  canonical docs). The two checks catch question and write errors separately.

## Response Summary

- Skeleton changed: `ESSENTIAL_DOMAIN.md` +N, `ESSENTIAL_USECASE.md` +N, `SYSTEM_DOMAIN.md` +N, `SYSTEM_USECASE.md` +N.
- Queue: `QUESTION_CANDIDATE.md` +N / -N, with N blocked by unconfirmed terms.
- Rejected: `REJECTED.md` +N.
- Progress: relay the single line `sh scripts/progress.sh <docs-dir>` prints (e.g.
  `Progress: 7/19 resolved (5 confirmed + 2 rejected; 12 open).`) — verbatim, never counted by hand.
- Coverage: read `<areas>`; thinnest area `<area>`.
- Next question: render the candidate `sh scripts/next-question.sh <docs-dir>` selects as one exact
  content question — or `none — queue empty` when it prints `queue-empty` (every candidate canonical
  or rejected) or `none-ready` (only blocked candidates remain).

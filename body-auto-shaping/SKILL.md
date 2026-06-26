---
name: body-auto-shaping
description: Minimal automation wrapper over $body-shaping. Replaces the human Yes answer with a single sub-agent Approver that auto-approves by default and escalates to the human only when the source is incoherent (its own description is logically broken) or the related evidence conflicts (within a doc, within the code, between doc and code, against canonical, or a naming clash); everything else — including new domain terms and definitions — is auto-confirmed. Auto-promoted items carry a short visible `· A` header suffix; no provenance fields or auto-loops are added.
---

# Body Auto Shaping

## Purpose

Run `$body-shaping` and automatically answer **Yes** by default. The candidate has already cleared `$body-shaping`'s consistency gate (its question `Content` is a faithful, evidence-bounded derivation), so auto-confirm it — including a new domain term or definition — unless one of **two** checks fails: the source is **incoherent** (its own description is logically broken) or the evidence **conflicts** (inside a doc, inside the code, between doc and code, against canonical, or a naming clash). Those two cases go to the human unchanged; everything grounded, coherent, and unconflicted is auto-confirmed.

This skill is deliberately the smallest of the body-shaping automation wrappers.

It does **not**:
- add provenance metadata fields to promoted items (no `Confirmation: auto`, no `Evidence:` lines)
- auto-loop to queue-empty (one candidate per invocation)
- track auto/human counters

An auto-promoted item appends `· A` to its `##` heading. `A` means **Approver**:

```md
## [Member] · A
```

When a canonical document first receives this suffix, add the one-line legend immediately below its
`#` title:

```md
> A = Approver
```

Human-promoted and pre-existing items carry no suffix. The suffix is outside the bracketed domain
term, so it does not create a domain reference or change the canonical term name.

Use `$body-shaping` directly for full human confirmation. Use `$auto-body-shaping` when you need the auto/human distinction recorded inline. Use `$yolo-body-shaping` when you want inferred content segregated into `INFERRED_*.md`.

## Scope

This skill is an explicit opt-in override of `$body-shaping`'s normal confirmation loop, narrowed only to the **Yes** branch. It does not change:

- document locations, classification rules, or promotion rules
- the selector
- Re-evaluate, the consistency gate, or `check-body.sh`
- the Promote step's behavior on **Yes**
- rejection or "Something else" handling

Treat the user's standing automation instruction as authorizing a **Yes** answer only when the Approver returns `APPROVE`. Never auto-answer No or rewrite the candidate.

## Loop

1. Load `$body-shaping` and obey its rules. Locate the `$body-shaping` skill directory before running scripts. Prefer a sibling `body-shaping/` directory beside this skill; if neither is available, ask the user for the path.
2. Run `sh <body-shaping-skill>/scripts/progress.sh <docs-dir>` and relay the line only when presenting a human question or the final summary.
3. Run `sh <body-shaping-skill>/scripts/next-question.sh <docs-dir>`.
   - `queue-empty` → stop.
   - `none-ready` → stop and summarize blockers.
4. Re-evaluate the selected candidate using `$body-shaping` rules. If Re-evaluate removes or merges the candidate, stop.
5. Generate the body-shaping review question per `$body-shaping`.
6. If the candidate's `Basis` is `observed`, run `$body-shaping`'s consistency gate per `body-shaping/references/consistency-gate.md`.
   - `REWORK` → apply the safe correction (dual-write to candidate and displayed question, single hop, per gate protocol), then proceed with the corrected `Content`.
   - `READY` → proceed.
   - If the gate flipped `Basis` to `proposed` (un-narrowable claim), proceed as `proposed` below.
7. If `Basis` is `proposed`, skip the Approver and ask the human directly per `$body-shaping`. Proposed candidates always require human ratification — truth-maker is human, not the file.
8. Otherwise (`observed`, gate `READY`), spawn the **Approver** as a single sub-agent in a separate context, with the contract below.
   - `APPROVE` → treat the review answer as exactly **Yes** under the user's standing automation instruction and run `$body-shaping`'s Promote step. Append ` · A` to the new item's `##` heading. If its canonical document has no `> A = Approver` line directly below the `#` title, add that exact line once. Add no other metadata.
   - `NEEDS_HUMAN` → show the body-shaping question to the user verbatim and wait. Do not hint at the Approver's reason.
9. After Promote, run:

   ```sh
   sh <body-shaping-skill>/scripts/check-body.sh <docs-dir>
   ```

   If the only safe fix would alter the just-promoted meaning, revert the item to `QUESTION_CANDIDATE.md` and ask the human per `$body-shaping`.
10. Stop. This skill processes one candidate per invocation. Re-invoke for the next.

## Approver Contract

Spawn one sub-agent in a separate context. Give it:

- the candidate's `Content` (post-rework, if any),
- its `Basis` and `Evidence` (file references with `path:line` or `path:start-end`),
- the four canonical docs (`ESSENTIAL_DOMAIN.md`, `ESSENTIAL_USECASE.md`, `SYSTEM_DOMAIN.md`, `SYSTEM_USECASE.md`),
- the full `QUESTION_CANDIDATE.md` entry for the candidate (including `Blocked by`), and
- read-only access to the project solely for the bounded related-context search below.

Withhold `Progress`, free narration, and unrelated queue entries. The Approver does not receive a
project-wide open-ended review assignment. It starts at each cited evidence range and reads only:

- the enclosing document section;
- the definition and direct callers/callees of a cited code symbol, plus directly connected route,
  schema, storage, or transport declarations when the cited range names one; and
- project documentation and canonical entries that use the candidate term or a directly evidenced
  alias.

This is the **related context** for this decision. Do not expand it through transitive call chains,
unrelated modules, or unrelated queue candidates. If the cited range does not identify enough context
to perform one of these checks, return `NEEDS_HUMAN` rather than guessing.

Require exactly this output:

```text
VERDICT: APPROVE | NEEDS_HUMAN
REASON: <one line>
```

### Default verdict is `APPROVE`

The candidate has already cleared `$body-shaping`'s consistency gate, so the question's `Content` is a
faithful, evidence-bounded derivation. The Approver therefore does **not** re-judge fidelity,
wording, classification altitude, or readiness — those are owned by the gate, Re-evaluate, the
selector, and `check-body.sh`. Return `APPROVE` by default — **even for a brand-new domain term or
definition, and even when the only evidence is test, fixture, or generated code** — and escalate to
`NEEDS_HUMAN` only when either of the two checks below fails.

**Read precondition.** Before deciding, open and read every `path:line` (or `path:start-end`) in
`Evidence` directly, then perform the bounded related-context search above. If a file is missing, a
range is unreadable, or the required related context cannot be located, return `NEEDS_HUMAN`. This is
a verification prerequisite, not a third decision check.

### `NEEDS_HUMAN` — two checks (both must be clear to `APPROVE`)

`APPROVE` is a conjunction. The candidate is already **grounded** — `$body-shaping`'s gate guarantees the
question is a faithful derivation of real evidence, and any un-grounded claim was flipped to
`proposed` and sent to the human *before* the Approver ran (Loop step 7). So return `APPROVE` when
**both** checks below are clear, and `NEEDS_HUMAN` the moment **either** fails:

1. **Coherence.** The cited document prose and its enclosing section, or the cited code and its direct
   implementation context, are internally sound — not
   self-contradictory or logically broken on its face. A fact whose own description does not hold
   together is `NEEDS_HUMAN`.
2. **Consistency — no conflict in related context.** Nothing that should agree in the bounded related
   context disagrees:
   - a semantic conflict inside a single referenced document,
   - an implementation conflict inside the code (the code contradicts itself),
   - a **document↔code conflict** — the doc states a flow or definition the code does not actually
     enact (doc says X, the code does not-X),
   - a conflict with already-confirmed canonical content (promoting would contradict or change a
     confirmed entry), or
   - a **naming clash** — the same name used with different meanings, or different names used with
     the same meaning.

A name or definition otherwise **approves by default**: its base is the code or the doc, so it is a
fact to accept, not a choice to ratify. Only a naming clash (check 2) blocks it.

There is no third "needs judgment" check. A decision that feels hard to answer `Yes` to is always one
of: a conflict (check 2), an incoherence (check 1), or a claim not grounded in the source — and an
un-grounded claim is the **gate's** job, already routed to the human as `proposed` before you ran.
The Approver certifies exactly two things — coherence and consistency — invents no caution beyond
them, and never blocks a name or definition merely for being new.

The Approver does not promote, edit files, rewrite the candidate, or comment on `[Term]` references — those belong to the gate, Re-evaluate, and `check-body.sh`. It produces only the verdict and a one-line reason.

## On `APPROVE` — Promote

Run `$body-shaping`'s Promote step exactly as if the user answered **Yes**. Then append ` · A` to the
new item's `##` heading:

```md
## [Member] · A
```

If the canonical document has no `> A = Approver` line directly below its `#` title, add it once.
Do not add any other metadata. Human-promoted and pre-existing items have no suffix. The body-shaping
checker and progress script continue to read the leading `## [Term]` portion of the heading.

## On `NEEDS_HUMAN` — Ask the Human

Show the body-shaping review question to the user verbatim — the same `Progress:` / `Target:` / `Subject:` / `Why this layer:` / `Content:` block `$body-shaping` would have shown. Do not summarize, do not paraphrase, do not hint at the Approver's reason. Handle the human's answer per `$body-shaping`.

## Response Summary

Same as `$body-shaping`'s response summary, with one added line:

- `Auto-Yes: yes | no` — whether this invocation auto-answered Yes. No cumulative counters across invocations.

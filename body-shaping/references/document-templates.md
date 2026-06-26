# Document Templates

## Fixed Document Paths

```text
docs/ESSENTIAL_DOMAIN.md
docs/ESSENTIAL_USECASE.md
docs/SYSTEM_DOMAIN.md
docs/SYSTEM_USECASE.md
docs/QUESTION_CANDIDATE.md
docs/REJECTED.md
```

The first four documents are canonical — confirmed content only. `QUESTION_CANDIDATE.md` is the
working question queue. `REJECTED.md` is a non-canonical archive of candidates the user explicitly
rejected. Neither the queue nor the archive is canonical truth.

Document body language follows the project's main team language. File names and section labels stay
in English.

## Term Marking

```text
[Confirmed Term] = confirmed domain language
{Candidate Term} = unconfirmed domain language
```

Rules:

- Canonical documents use `[]` only — never `{}`.
- `QUESTION_CANDIDATE.md` may use both `[]` and `{}`.
- A candidate is blocked **iff** its `Blocked by:` section is non-empty. Every unconfirmed
  `{Candidate Term}` in its `Content` must be listed there; this is a queue invariant, not a
  second readiness rule.
- A candidate contains one independently confirmable claim. Split multiple independent meanings,
  policies, relationships, invariants, or flows into separate candidates before asking for approval.

## ESSENTIAL_DOMAIN.md

Confirmed conceptual domain language: terms, states, policies, responsibilities, relationships, and
invariants that explain what the system means at the domain-flow level.

```md
# ESSENTIAL_DOMAIN

## [Term]

Meaning:
-

Evidence:
- `path/to/file.ext:123`: [short reason]
```

## ESSENTIAL_USECASE.md

Confirmed conceptual domain flows only. Each use case uses Given/When/Then to show how Essential
domain concepts connect over time. Each bracketed term must already exist in
`ESSENTIAL_DOMAIN.md`.

Do not put static meanings here. Identity, ownership, cardinality, allowed values, lifecycle states,
policies, responsibilities, relationships, and stable invariants belong in `ESSENTIAL_DOMAIN.md`.

```md
# ESSENTIAL_USECASE

## [Use Case Name]

Given:
-

When:
-

Then:
-
```

## SYSTEM_DOMAIN.md

Confirmed runtime/implementation language: storage, transport, protocol, process, queue, cache,
transaction, scheduling, concurrency, routing, query, pagination, and operational concepts used to
execute the Essential flow. A System term may reference an `[Essential Domain]` term it operates on
(the concrete layer depends on the abstract one); the reverse — Essential naming a System term — is
not allowed.

```md
# SYSTEM_DOMAIN

## [Term]

Meaning:
-

Evidence:
- `path/to/file.ext:123`: [short reason]
```

## SYSTEM_USECASE.md

Confirmed runtime/implementation flows. Each bracketed term in the flow must already exist in
`SYSTEM_DOMAIN.md` or `ESSENTIAL_DOMAIN.md` — a System flow executes Essential concepts, so it may
name the Essential entities it acts on (never the reverse). `Related Essential Use Case` links the
execution to the conceptual flow it serves — the cross-layer dependency. It may be `None` for pure
system-maintenance use cases.

Each system use case uses Given/When/Then to show how System domain concepts connect during
execution. Technical terms alone belong in `SYSTEM_DOMAIN.md`.

```md
# SYSTEM_USECASE

## [System Use Case Name]

Related Essential Use Case:
-

Given:
-

When:
-

Then:
-

System decisions:
-
```

`System decisions` is optional. Use it only for technical decisions risky to change later:
transaction boundaries, retry behavior, ordering, trust boundaries, or failure handling.

## QUESTION_CANDIDATE.md

The working queue. One `Q-{nnn}` entry per unconfirmed candidate, with six fields:

```md
# QUESTION_CANDIDATE

## Q-001

Type:
<exactly one of: essential-domain | essential-usecase | system-domain | system-usecase>

Subject:
<the plain canonical header name created on Yes; no [] or {} notation>

Basis:
<exactly one of: observed | proposed>

Content:
- [the bare candidate: a domain term, or a use-case flow]

Evidence:
- `path/to/file.ext:123`: [short reason]
  (or, for a candidate sourced only from a proposed flow: `proposed flow: <verbatim sentence>`;
  add `from use-case Q-{nnn}` only as context)

Blocked by:
- {Unconfirmed Term}   (one bullet per unconfirmed term; leave the section empty for a ready question)
```

Rules:

- `Type:` carries both layer (essential/system) and shape (domain/usecase); the LLM assigns it.
  Shape is not stored separately — it is part of `Type:`.
- `Subject:` is the plain name of the one canonical item a Yes creates. It is the source for both the
  Review `Subject:` label and the canonical `## [Subject]` header; it is not inferred from `Content`.
- `Basis:` records the candidate's **truth-maker source**, set at Recover alongside `Type:`. It is
  exactly one of two literals:
  - `observed` — a file `path:line` in `Evidence` is the truth-maker of the claim. The consistency
    gate runs on this candidate before it is shown (see `references/consistency-gate.md`).
  - `proposed` — human confirmation is the truth-maker: a new-design claim, or a current domain fact
    not yet pinned to code. The gate is **skipped** and the candidate goes straight to Review. A
    file may still be cited as provenance (where the idea started), but it does not back the claim.
  `Basis` is not a meaning classification and is not derivable from `Evidence` alone (a cited file
  may be either truth-maker or provenance), so it is stored, not inferred. `scripts/next-question.sh`
  validates it structurally over the whole queue: a missing or unknown value is a malformed queue and
  fails loud (`invalid-basis Q-{nnn}`, exit 3) — never silently defaulted or skipped. Split a
  candidate **before** assigning `Basis`, so each `Q-{nnn}` carries a single truth-maker source.
- `Content` stores only the bare candidate. The review prompt `Is this right?` is added only when
  rendering the question, so the queued and displayed `Content` strings are identical.
- `Content` contains one independently confirmable claim. A `Yes` approves that one displayed
  claim; split a bundled candidate before it reaches Review.
- `Blocked by` is the sole readiness source: its non-empty value means blocked; an empty value means
  ready. List every unconfirmed dependency from `Content` there and ask that domain term first. A
  ready use-case contains only `[Confirmed Term]` references.
- `Status` is not stored — it is derived from `Blocked by`.
- `Q-{nnn}` numbers are monotonically increasing across the project's history. Removing an entry
  (Promote or Reject) does **not** free its number — gaps are normal and reflect how many
  candidates the project has worked through.
- When a candidate is Promoted (Yes), remove the freshly confirmed term from every remaining
  entry's `Blocked by` list. This sweep is deterministic and happens in the same step as
  `check-body.sh`.
- Before Review, run `scripts/check-question.sh <docs-dir> <Q-id>`. It checks the selected entry's
  exact `Type`/`Subject`/`Basis`, ready `Blocked by`, candidate notation, and reference layers. A
  non-zero result means do not ask yet.
- Before asking, run Re-evaluate: if the same word is already canonical in the same `Type:` with the
  same meaning, delete the question; if already canonical in the same `Type:` with a different
  meaning, surface the clash instead of asking. The same word in another layer is a parallel
  meaning, not a duplicate.
- If two queued candidates of the same `Type:` express the same independently confirmable claim,
  keep one, merge their primary evidence, and delete the duplicate. This is a meaning judgment, not
  a fixed matching table.

## Review Question Shape

When asking the user to approve a queued candidate, always show the LLM-assigned layer and shape
first. Render labels and answer options in the user's or project's language; the field structure is
fixed:

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

`Progress:` is whatever `scripts/progress.sh` prints, relayed verbatim (parenthesised breakdown
included), not hand-counted. **Evidence is
deliberately absent** from the asked question: it lives in the candidate's `QUESTION_CANDIDATE.md`
entry and is surfaced only when the user hesitates or asks where the candidate came from. The target
is presented by the LLM, not chosen by the user. The user confirms or corrects the content. If the
user says the classification itself is wrong, re-evaluate and ask again with the revised target.

## REJECTED.md

Non-canonical archive for candidates the user explicitly rejected during Promote ("Something else"
→ reject). The archive preserves the rejection so a later Recover pass does not resurrect the same
candidate. Skip writing only when the user says to discard it outright.

```md
# REJECTED

## R-001

Original candidate:
-

Reason:
- (free text — why this is not canonical; if it has been superseded or reframed, name what
  replaces it inline)

Evidence:
- `path/to/file.ext:123`: [short reason]

Replacement / current rule:
-
```

Rules:

- An `R-{nnn}` entry is appended whenever the user rejects a candidate during Promote. Numbering
  is monotonically increasing; removed entries do **not** free their number.
- `Reason` is free text. Do not enumerate fixed subtypes — that re-tables the "Something else"
  path the skill is built to avoid.
- `Replacement / current rule` is optional. Fill it only when the rejection points to a different
  term or rule that should be used instead.
- Do not move `R-{nnn}` entries back to `QUESTION_CANDIDATE.md`.

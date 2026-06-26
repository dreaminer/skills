---
name: yolo-body-shaping
description: Maximally automates body-shaping for code-only projects. Adds a Decision Maker that resolves UNDECIDED candidates from referenceable evidence (including code-only evidence) and isolates inferred results into INFERRED_*.md so canonical documents stay anchored to direct evidence. Use only when the user explicitly opts in to maximum auto-progression and accepts that inferred content is segregated, dependency-tracked, and audit-traceable.
---

# Yolo Body Shaping

## Purpose

Run `$body-shaping` with the strongest possible auto-progression gate. This skill keeps the original
Essential/System × Domain/UseCase document model and the parent's classification, selector, and
check-body rules, but pushes automation further than `$auto-body-shaping` along two axes:

1. The Consistency Validator's PASS gate is widened so that code-only evidence is acceptable when it
   directly supports the candidate. Essential candidates no longer require human-authored docs to
   reach PASS.
2. A third agent — the **Decision Maker** — is introduced to resolve `UNDECIDED` candidates from
   referenceable evidence alone (typically code, tests, fixtures, or already-canonical content),
   without escalating to a human.

To protect the truth of canonical docs, anything the Decision Maker decides is written to a
segregated set of `INFERRED_*.md` documents, never directly into the canonical four. Canonical
content remains "directly supported by referenceable evidence". Inferred content is "best
auto-reasoned interpretation of evidence", and its provenance is recorded inline.

Use this skill **only when the user explicitly requested yolo body shaping**. If the user wants
human confirmation, use `$body-shaping`. If the user wants validator-gated auto-promotion with human
review of ambiguous items, use `$auto-body-shaping`. This skill is an explicit opt-in override of
both: the user's invocation is a standing instruction to accept Decision Maker rulings without
per-candidate consent, except for the narrowly defined `TRULY_NEEDS_HUMAN` cases below.

Auto-decided items are not personally confirmed by a domain stakeholder; describe them as
auto-decided under the user's yolo automation request.

## Permission Model

| Skill | Invocation opt-in | Per-candidate consent |
|---|---|---|
| `$body-shaping` | explicit invocation | every candidate |
| `$auto-body-shaping` | explicit invocation | only `NEEDS_HUMAN` candidates |
| `$yolo-body-shaping` (this) | explicit invocation | only `TRULY_NEEDS_HUMAN` candidates (rare) |

## Roles

- **Coordinator**: the main agent. Load and follow `$body-shaping`; own all file edits; run
  selector, progress, and checker scripts; decide whether a verdict means canonical promotion,
  isolated inferred promotion, rejection, or human escalation.
- **Question Generator**: a sub-agent that receives one selected candidate and renders the exact
  body-shaping review question. It does not write files and does not approve content.
- **Consistency Validator**: a sub-agent that returns `PASS`, `FAIL`, or `UNDECIDED`. It performs
  evidence-integrity, classification, and reference checks only. It does not make domain judgments.
- **Decision Maker**: a sub-agent that receives `UNDECIDED` candidates and returns `DECIDE_YES`,
  `DECIDE_NO`, or `TRULY_NEEDS_HUMAN`. It is the only role allowed to perform domain inference from
  evidence. It does not write files.

If sub-agent tools are unavailable, simulate each role in clearly separated passes in the main
agent and use the same output contracts.

## Document Layout

### Canonical (unchanged from `$body-shaping`)
- `docs/ESSENTIAL_DOMAIN.md`
- `docs/ESSENTIAL_USECASE.md`
- `docs/SYSTEM_DOMAIN.md`
- `docs/SYSTEM_USECASE.md`

### Inferred (new, segregated by yolo)
- `docs/INFERRED_ESSENTIAL_DOMAIN.md`
- `docs/INFERRED_ESSENTIAL_USECASE.md`
- `docs/INFERRED_SYSTEM_DOMAIN.md`
- `docs/INFERRED_SYSTEM_USECASE.md`

Each inferred document uses the same item format as its canonical counterpart so that
`check-body.sh`'s directional reference rules apply unchanged. Inferred files are created lazily on
first insertion; treat a missing file as empty, not an error.

### Workflow queues
- `docs/QUESTION_CANDIDATE.md` — body-shaping queue (unchanged).
- `docs/REJECTED.md` — body-shaping rejected log (unchanged).
- `docs/REEVAL_QUEUE.md` — new yolo queue listing items that must be re-evaluated when an inferred
  dependency changes state.

## Workflow

1. Load `$body-shaping` and obey its document locations, classification rules, promotion rules,
   selector order, and check scripts except where this skill explicitly narrows or widens them.
2. Locate the `$body-shaping` skill directory before running scripts. Prefer a sibling
   `body-shaping/` directory beside this skill; otherwise use the loaded skill source path; if
   neither is available, ask the user for the path.
3. Recover candidates first only when `docs/QUESTION_CANDIDATE.md` is missing or empty, or when the
   user explicitly asks for a Recover pass. Do not infer that a partial queue is stale.
4. Start the yolo loop:
   - Run `sh <body-shaping-skill>/scripts/progress.sh <docs-dir>` and relay the line only when
     presenting a `TRULY_NEEDS_HUMAN` question or the final summary.
   - Run `sh <body-shaping-skill>/scripts/next-question.sh <docs-dir>`.
   - Stop on `queue-empty`.
   - Stop and summarize blockers on `none-ready`.
   - Re-evaluate the selected candidate using `$body-shaping` rules before any approval attempt.
5. Spawn the Question Generator with the selected candidate, its evidence, all four canonical docs,
   all four inferred docs, and the queue entry's blocked-by state.
6. Spawn the Consistency Validator with the raw candidate, generated question, evidence, canonical
   and inferred docs, the full queue entry, and the current blocked-by / canonical-reference state.
7. **Validator verdict dispatch**:
   - `PASS` → promote into the matching **canonical** file with `Confirmation: auto-validator`.
   - `FAIL` → fix only mechanical issues (formatting, candidate notation, `Blocked by` metadata,
     transcription errors) and re-run validator; do not change candidate meaning.
   - `UNDECIDED` → spawn the Decision Maker.
8. **Decision Maker verdict dispatch**:
   - `DECIDE_YES` → promote into the matching **inferred** file with `Confirmation: auto-decision`
     and full inference metadata.
   - `DECIDE_NO` → append a `REJECTED.md` entry with `Reason: yolo decision NO` and the Decision
     Maker's one-line reason.
   - `TRULY_NEEDS_HUMAN` → ask exactly one body-shaping review question using the validator's
     `QUESTION` plus the Decision Maker's `REQUIRED_HUMAN_QUESTION`; wait for the user's answer.
9. After every canonical or inferred promotion, run:

   ```sh
   sh <body-shaping-skill>/scripts/check-body.sh <docs-dir>
   ```

   Fix any mechanical failure before continuing. If a fix would alter the just-promoted meaning,
   revert the promotion to the queue and route to `TRULY_NEEDS_HUMAN`.
10. Update the dependency graph. If the just-promoted item resolves any pending `REEVAL_QUEUE.md`
    entries, prepend those re-eval items to the candidate queue before continuing.
11. Repeat until the queue is empty, only blocked candidates remain, a `TRULY_NEEDS_HUMAN` requires
    user input, the validator's check-body fix would alter meaning, or the user stops the run.

## Question Generator Contract

Ask the Question Generator for this exact output:

```text
QUESTION:
Progress: <progress line from coordinator>
Target: <Essential|System> × <Domain|UseCase>
Subject: <term or use-case name>
Why this layer × shape: <classification reason>
Content:
<domain definition or Given/When/Then flow>
Is this right?
- Yes
- Something else

NORMALIZED_CLAIMS:
- <one atomic claim per line>

EVIDENCE_USED:
- <file path>:<line or line-range> -- <short paraphrase>

GENERATOR_NOTES:
- <missing information, wording concern, or "none">
```

Rules for the generator:

- Preserve the body-shaping review shape exactly.
- Do not include evidence in `QUESTION`; keep it only in `EVIDENCE_USED`.
- Split bundled statements into atomic claims so the validator can check each one.
- Cite source evidence with concrete `path:line` or `path:start-end` references whenever the source
  is a file. Use candidate-only evidence only when no file source exists.
- Mark inferred wording in `GENERATOR_NOTES`; do not hide uncertainty.
- Do not approve, reject, promote, or edit files.
- When the coordinator routes a `TRULY_NEEDS_HUMAN` candidate to the user, show only the `QUESTION`
  section plus the Decision Maker's `REQUIRED_HUMAN_QUESTION` line. Other sections are internal.

## Consistency Validator Contract

Ask the Consistency Validator for this exact output:

```text
VERDICT: PASS | FAIL | UNDECIDED
REASON:
<brief reason>

CLAIM_CHECKS:
- PASS|FAIL|UNKNOWN: <claim> -- <why>

CLASSIFICATION_CHECK:
PASS|FAIL|UNKNOWN: <why>

REFERENCE_CHECK:
PASS|FAIL|UNKNOWN: <why>
```

`PASS` is allowed only when all of these are true:

- Every normalized claim is directly supported by cited project evidence or already-canonical docs.
- The validator directly opens and reads every cited `path:line` or `path:start-end` in
  `EVIDENCE_USED` and verifies that the source text supports the claim. Missing files, unreadable
  ranges, vague references, or source text that does not support the claim prohibit `PASS`.
- The candidate wording adds no unsupported cardinality, lifecycle state, policy, obligation,
  permission, timing, causality, or stakeholder intent beyond what the cited evidence shows.
- The assigned layer and shape match `$body-shaping` classification rules.
- The validator has received all four canonical docs and checked same-word clashes in the same
  `Type:`.
- The candidate has no unresolved bracketed references in body content, no candidate notation that
  would leak into a canonical doc, and no directional reference violation under `$body-shaping`
  rules.
- Confirmation metadata must not create bracketed references. `Confirmation:`, `Evidence:`,
  `Decision basis:`, and `Depends on inferred:` lines may use bare names or backtick spans, but
  never `[Term]` notation.
- A UseCase candidate uses already-confirmed canonical terms and is not blocked.
- No same-word canonical clash exists in the same `Type:`.
- The generated question faithfully represents the raw candidate.

**Code-only evidence is acceptable for `PASS`** when it directly supports each claim. The yolo
validator does not require human-authored product/domain/docs language for Essential candidates.

Return `UNDECIDED` (instead of escalating to a human) when the candidate may be true but cannot be
proven from cited evidence alone — typically because it asserts cardinality, lifecycle, policy,
ownership, obligation, timing, causality, or stakeholder intent that the cited evidence does not
literally state. The Decision Maker will decide.

Return `FAIL` when the generated question misstates the candidate or the evidence contradicts it.

`UNKNOWN` in any check counts as `UNDECIDED` for the overall verdict; do not allow a `PASS` to
include an `UNKNOWN`.

## Decision Maker Contract

Ask the Decision Maker for this exact output:

```text
VERDICT: DECIDE_YES | DECIDE_NO | TRULY_NEEDS_HUMAN
REASON:
<one line>

INFERENCE_BASIS:
- <single semantic inference drawn from evidence or canonical content>

CODE_PATTERNS_USED:
- `path:line` -- <what this pattern implies and why>

CANONICAL_REFERENCES:
- `Term` (canonical|inferred) -- <how it grounds this decision>

DEPENDENCY_INFERRED:
- `<inferred term>` -- <how this candidate depends on it>
  (or "none")

DEPTH_CHECK:
PASS|FAIL -- <accumulated inferred dependency depth, in hops>

REQUIRED_HUMAN_QUESTION:
<question to ask the user if VERDICT is TRULY_NEEDS_HUMAN, otherwise "none">
```

`DECIDE_YES` is allowed only when all of these are true:

- The Decision Maker can name at least one concrete code pattern, test fixture, runtime trace, or
  already-existing canonical/inferred entry that supports the candidate's meaning.
- The inference does not introduce a new policy, business rule, or behavior that is not implied by
  evidence; it must describe what evidence shows, not what evidence ought to do.
- The candidate's cumulative inferred-dependency depth, including this promotion, does not exceed
  **2 hops**. Count the longest chain of `Depends on inferred:` links from this candidate's
  dependencies, then add 1 for this item itself if it lands in an inferred file. Above 2 hops →
  `TRULY_NEEDS_HUMAN`.
- The Decision Maker is not personally uncertain. If any reasoning step is `UNKNOWN`, return
  `TRULY_NEEDS_HUMAN`.

`DECIDE_NO` is allowed when evidence shows the candidate is false, contradicted, refers to a
removed or stale system, or is a duplicate of an already-canonical entry under a different name.

Return `TRULY_NEEDS_HUMAN` in these narrow cases:

- Multiple cited sources give conflicting evidence with no reasonable resolution
- The candidate proposes new behavior, policy, or product intent rather than describing existing
  behavior
- Evidence is effectively zero (no code, no tests, no canonical link)
- The 2-hop inferred-depth limit is exceeded
- Any internal reasoning step is `UNKNOWN`
- A naming choice has multiple plausible options and the choice is not mechanical (i.e., not a
  simple synonym/casing collapse)

## Promotion & Isolation Rules

### Validator PASS → canonical
1. Promote the candidate content exactly as the question stated it. No rewriting, merging,
   renaming, or broadening.
2. Insert into the matching canonical file (`ESSENTIAL_DOMAIN.md`, `ESSENTIAL_USECASE.md`,
   `SYSTEM_DOMAIN.md`, or `SYSTEM_USECASE.md`).
3. Add inline metadata immediately below the item heading:

   ```md
   Confirmation: auto-validator
   Evidence:
   - `path/to/source.ext:42`
   Depends on inferred: `OrderName`, `Cart`
   ```

   - List inferred dependencies the candidate's body content actually references. Use bare names or
     backticks, never `[Term]`. Write `Depends on inferred: none` when there are none.
4. Delete the promoted candidate from `QUESTION_CANDIDATE.md`.
5. Remove the newly confirmed canonical term from other candidates' `Blocked by` lists.
6. Run `check-body.sh`.

### Decision Maker DECIDE_YES → inferred
1. Promote the candidate into the matching `INFERRED_*.md` file using the same item format as the
   canonical counterpart.
2. Add inline metadata immediately below the item heading:

   ```md
   Confirmation: auto-decision
   Decision basis: <one-line summary from REASON>
   Evidence:
   - `path/to/source.ext:42`
   Depends on inferred: `OrderName`, `Cart`
   Depth: <hops>
   ```

3. Delete the promoted candidate from `QUESTION_CANDIDATE.md`.
4. Inferred items unblock UseCase candidates only when the consumer is itself in an inferred file
   or already records the dependency as `Depends on inferred:`. **Canonical content must not gain a
   new `[Term]` body reference to an inferred item** — record dependency as metadata only.
5. Run `check-body.sh`.

### Validator FAIL → mechanical fix
Fix only generator formatting, candidate notation, broken `Blocked by` metadata, or an obvious
transcription error from the raw evidence. Do not change candidate meaning, term names, policies,
relationships, cardinality, or use-case outcomes without human confirmation. Re-run validator.

### Decision Maker DECIDE_NO → reject
Append to `REJECTED.md` as `## R-NNN` with:

```md
Reason: yolo decision NO — <Decision Maker REASON>
Replacement / current rule: <if Decision Maker pointed to a canonical or inferred replacement>
```

Then delete the candidate from `QUESTION_CANDIDATE.md`.

### TRULY_NEEDS_HUMAN
Ask exactly one body-shaping review question and wait. Do not auto-answer. If the user answers
**Yes**, promote into the canonical file with:

```md
Confirmation: human
Evidence:
- Human answer in review loop
```

Use `[Term]` only in body content, never in confirmation metadata.

## Directional Reference Rule (extended)

`$body-shaping`'s directional rules apply unchanged for canonical content:

- ED refs → ED
- EU refs → ED
- SD refs → SD or ED
- SU refs → SU, SD, or ED

Inferred files extend the rules as follows:

- Inferred items may reference their matching canonical layer and other inferred items of the same
  or lower layer, using the same direction (`I_SD` refs → `I_SD`, `SD`, `I_ED`, `ED`).
- Canonical items must not reference inferred items in body content via `[Term]`. Dependencies on
  inferred items live only in metadata (`Depends on inferred:`).

This preserves `check-body.sh`'s correctness on canonical files and lets it run unchanged on
inferred files when invoked with each file set in turn.

## Re-evaluation Queue

`docs/REEVAL_QUEUE.md` records items that need re-checking when an inferred dependency changes
state. Format:

```md
## R-NNN
Trigger: `<inferred-term>` → <canonical|REJECTED>
Affected:
- Q-014
- Q-022
Status: pending | done
```

When the coordinator promotes or rejects an inferred item:

1. Scan all canonical and inferred items for `Depends on inferred:` mentioning this term.
2. For each affected item, append it to the next yolo iteration's candidate queue ahead of other
   work, and mark this re-eval entry `done` after processing.

A canonical re-eval that downgrades may move an item back to inferred or to `REJECTED.md` depending
on the new validator/Decision Maker outcome. Treat as a fresh dispatch.

## Human Escalation

`TRULY_NEEDS_HUMAN` is the only path that asks the user. Reach it only when:

- Decision Maker explicitly returns `TRULY_NEEDS_HUMAN`
- A mechanical fix to satisfy `check-body.sh` would alter the just-promoted meaning
- The user has explicitly paused the run

Do not silently downgrade `DECIDE_YES` to a human question. Keep the validator's `QUESTION` plus the
Decision Maker's `REQUIRED_HUMAN_QUESTION` together so the user sees the candidate and the specific
ambiguity.

## Summary

End with the normal `$body-shaping` response summary plus:

- `Auto-promoted (validator PASS): N`
- `Auto-decided (inferred): N`
- `Auto-rejected (decision NO): N`
- `Human-required: N`
- `Re-evaluation queued: N`
- `Validator failures fixed: N`
- `Stopped because: queue-empty | none-ready | needs-human | user-stop | check-failure`

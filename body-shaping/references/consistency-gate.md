# Consistency Gate — Protocol

The detailed protocol for the evidence → `Content` fidelity check that runs before a generated
question is shown. `SKILL.md` carries only the entry decision and a pointer here; this file is the
contract. Read it before running the gate the first time in a session, and follow it exactly — the
gate is unsound if any step is skipped.

## Why it exists (one paragraph)

The user confirms domain **content**, trusting that the question was faithfully derived from the
project. The domain is *not* fully in the user's head — that is the reason this skill runs — so the
user cannot catch a question whose claims overshoot their evidence. The user owns domain truth; this
gate owns derivation fidelity. (Full rationale and rejected alternatives: `DESIGN.md`.)

## When it runs — keyed on `Basis`

The selected candidate's `Basis` (the third token `scripts/next-question.sh` prints) decides:

- **`observed`** → **run the gate.** A file `path:line` is the claim's truth-maker, so there is a
  source to validate the question against.
- **`proposed`** → **skip the gate.** No spawn. Human confirmation is the truth-maker; no file
  `path:line` is the claim's truth-maker (a provenance file may still be cited, but it does not back
  the claim, so there is nothing to validate against). The candidate goes straight to Review and is
  asked as an ordinary `Is this right?` / `Something else` question — never dressed up as
  source-grounded.

A candidate is split into one truth-maker source before `Basis` is assigned, so this decision is
never "part observed, part proposed."

## The check (observed candidates only)

Spawn **one** sub-agent in a **separate context** — the agent that wrote the question cannot reliably
catch its own over-inference (a same-context self-check rationalizes exactly the overshoot it made).

Give the sub-agent **only**:

- the candidate's `Content` and `Evidence`, and
- the generated question's `Content`.

Withhold `Target`, `Why this layer`, the `Progress` line, the canonical docs, and the `Type:`.
Classification, clashes, and `[Term]` references already belong to Re-evaluate and `check-body.sh`;
withholding those inputs keeps this gate from re-judging them and drifting into their job.

The sub-agent reads each file `Evidence` at its `path:line` **directly** — never a paraphrase — so
the check is source-to-question, not a second summary of the generator's summary.

It checks only:

- every factual claim in the question's `Content` is directly supported by the evidence read;
- it adds no cardinality, lifecycle, policy, causality, obligation, or intent the evidence does not
  state; and
- it drops no omission or compression that changes the candidate's meaning.

## Verdict — `READY` / `REWORK`

It returns exactly one of:

- **`READY`** → show the question to the user exactly as generated.
- **`REWORK`** → it must hand back the **exact** safe correction, as either:
  - `SAFE_CONTENT:` — an evidence-bounded replacement `Content` (verbatim), or
  - `REMOVE_EXACTLY:` — the precise phrases to delete mechanically, with no re-wording.

  Prefer `SAFE_CONTENT` when a clean deletion would leave a broken sentence.

### Applying a `REWORK` (dual-write, single-hop)

The main agent applies the correction **identically to both** the selected candidate's `Content` in
`QUESTION_CANDIDATE.md` **and** the displayed question's `Content`, so the two remain the same
string. This matters because Promote writes the **queue candidate** on `Yes`, not the shown question
text: correcting only the question would let the original over-inference reach canonical while the
user saw the narrowed wording — breaking "`Yes` is a Yes to the displayed content." This is not a
canonical edit; it is an evidence-bounded correction of the working candidate before human
confirmation.

The main agent applies **only** that edit, then shows the question. It does **not** re-generate
freely and does **not** call the validator again — free re-generation would emit an unvalidated
sentence and break the single-hop guarantee.

## Un-narrowable claims

When an `observed` candidate's claim cannot be narrowed into its evidence at all — no `SAFE_CONTENT`
or `REMOVE_EXACTLY` leaves a supported claim, the whole claim is unsupported — its real truth-maker
is human judgment, not the file. Before sending it on, the main agent **flips the queue candidate's
`Basis` to `proposed`** in `QUESTION_CANDIDATE.md` (a cited file, if any, becomes provenance). It
then goes to Review as an ordinary `Is this right?` / `Something else` question, **not** presented as
source-grounded. Updating `Basis` is what stops a later re-selection from routing the same candidate
back through the gate as `observed`.

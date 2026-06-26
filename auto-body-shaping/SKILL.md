---
name: auto-body-shaping
description: Automates the body-shaping review loop with separate question-generation and consistency-validation agents. Use when the user explicitly wants body-shaping to keep advancing automatically, auto-promote candidates that are strongly supported by project evidence, and ask a human only for ambiguous, inferred, conflicting, or policy-heavy domain content.
---

# Auto Body Shaping

## Purpose

Run `$body-shaping` with an automated review gate. This skill keeps the original
Essential/System and Domain/UseCase document model, but replaces routine "is this right?"
round-trips with a strict consistency check. Only auto-answer **Yes** when the validator can prove
the displayed candidate is directly supported by project evidence and does not need human domain
judgment.

Use this skill only when the user explicitly requested automated body shaping. If the user wants
human-confirmed domain language, use `$body-shaping` directly.

This skill is an explicit opt-in override of `$body-shaping`'s normal confirmation loop. Treat the
user's invocation as a standing instruction to answer **Yes** only for candidates that pass this
skill's validator gate. Do not describe auto-promoted content as personally confirmed by a domain
stakeholder; describe it as auto-confirmed under the user's automation request.

Every item promoted by this skill carries inline confirmation metadata in the canonical document.
Do not use a sidecar provenance file; it drifts on rename/delete.
Canonical items without `Confirmation:` metadata are treated as human-confirmed entries that existed
before this automation. Do not backfill them unless the user asks for a metadata normalization pass.

## Roles

- **Coordinator**: the main agent. Load and follow `$body-shaping`; own all file edits; run selector,
  progress, and checker scripts; decide whether to auto-promote or ask the human.
- **Question Generator**: a sub-agent that receives one selected candidate and renders the exact
  body-shaping review question. It does not write files and does not approve content.
- **Consistency Validator**: a separate sub-agent that receives the raw candidate, generated question,
  canonical docs, and evidence. It returns `PASS`, `FAIL`, or `NEEDS_HUMAN`. It does not write files.

If sub-agent tools are unavailable, simulate the two roles in two clearly separated passes in the
main agent and use the same output contracts.

## Workflow

1. Load `$body-shaping` and obey its document locations, classification rules, promotion rules,
   selector order, and check scripts except where this skill explicitly narrows the confirmation
   step.
2. Locate the `$body-shaping` skill directory before running scripts. Prefer a sibling
   `body-shaping/` directory beside this skill; otherwise use the loaded skill source path; if
   neither is available, ask the user for the path.
3. Recover candidates first only when `docs/QUESTION_CANDIDATE.md` is missing or empty, or when the
   user explicitly asks for a Recover pass. Do not infer that a partial queue is stale.
4. Start the auto-review loop:
   - Run `sh <body-shaping-skill>/scripts/progress.sh <docs-dir>` and relay the line only when
     presenting a human question or final summary.
   - Run `sh <body-shaping-skill>/scripts/next-question.sh <docs-dir>`.
   - Stop on `queue-empty`.
   - Stop and summarize blockers on `none-ready`.
   - Re-evaluate the selected candidate using `$body-shaping` rules before any approval attempt.
5. Spawn the Question Generator with the selected candidate, its evidence, all four canonical docs,
   and the queue entry's blocked-by state.
6. Spawn the Consistency Validator with the raw candidate, generated question, evidence, all four
   canonical docs, the full queue entry, and the current blocked-by/canonical-reference state.
7. If the validator returns `PASS`, treat the review answer as exactly **Yes** under the user's
   standing automation instruction and run the `$body-shaping` Promote step, adding the inline
   confirmation metadata described below.
8. After every promotion, run:

   ```sh
   sh <body-shaping-skill>/scripts/check-body.sh <docs-dir>
   ```

   Fix any mechanical failure before continuing.
9. Repeat until the queue is empty, only blocked candidates remain, a validator requires human input,
   or the user stops the run.

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
- When asking the human, show only the `QUESTION` section. The other sections are internal
  validation material and must not be included in the first-level body-shaping question.

## Consistency Validator Contract

Ask the Consistency Validator for this exact output:

```text
VERDICT: PASS | FAIL | NEEDS_HUMAN
REASON:
<brief reason>

CLAIM_CHECKS:
- PASS|FAIL|UNKNOWN: <claim> -- <why>

CLASSIFICATION_CHECK:
PASS|FAIL|UNKNOWN: <why>

REFERENCE_CHECK:
PASS|FAIL|UNKNOWN: <why>

REQUIRED_HUMAN_QUESTION:
<question to ask the user if VERDICT is NEEDS_HUMAN, otherwise "none">
```

`PASS` is allowed only when all of these are true:

- Every normalized claim is directly supported by cited project evidence or already canonical docs.
- The validator directly opens and reads every cited `path:line` or `path:start-end` in
  `EVIDENCE_USED` and verifies that the source text supports the claim. Missing files, unreadable
  ranges, vague references, or source text that does not support the claim prohibit `PASS`.
- The candidate wording adds no unsupported cardinality, lifecycle state, policy, obligation,
  permission, timing, causality, or stakeholder intent.
- The assigned layer and shape match `$body-shaping` classification rules.
- The validator has received all four canonical docs and checked same-word clashes in the same
  `Type:`.
- The candidate has no unresolved bracketed references, no candidate notation that would leak into a
  canonical doc, and no directional reference violation under `$body-shaping` rules.
- Confirmation metadata must not create bracketed references. Every variable value (paths, term
  names, evidence paraphrases) on `Evidence:` and `Depends on auto:` lines is wrapped in backticks;
  only the fixed keywords `auto`, `human`, and `none` may appear bare. Never `[Term]` or `{Term}`.
- A UseCase candidate uses already-confirmed domain terms and is not blocked.
- No same-word canonical clash exists in the same `Type:`.
- The generated question faithfully represents the raw candidate.
- Essential content is supported by human-authored product/domain/docs language or already canonical
  docs, not only implementation, fixture, generated, or test evidence.

Auto-on-auto is a known boundary. If a candidate relies on auto-confirmed canonical entries, record
that dependency in the inline metadata.

Return `NEEDS_HUMAN` when any of these hold. This is the single normative list of when to ask the
human; do not keep a second copy elsewhere.

- the candidate may be true but needs business judgment, product intent, terminology preference,
  legacy-vs-real distinction, or acceptance of a new design
- conflicting evidence or multiple plausible meanings
- inferred product policy, ownership, cardinality, permissions, lifecycle, or obligation
- a term name that is likely a business naming choice
- a use case proposes new behavior rather than describing existing behavior
- stale, generated, fixture-only, or test-only evidence that may not describe real domain language
- promoting the candidate would change the meaning of existing canonical wording
- a candidate's only substantive support is auto-confirmed canonical content, with no source
  evidence or human-confirmed canonical content behind it (auto-on-auto)
- any claim, classification, or reference check is `UNKNOWN` (so the verdict can never be `PASS`)

Return `FAIL` when the generated question misstates the candidate or the evidence contradicts it.

## Auto-Promotion Rules

When the validator returns `PASS`:

1. Promote the candidate content exactly as if the user answered **Yes**.
2. Do not improve, rewrite, merge, rename, or broaden the candidate during auto-promotion.
3. Add inline confirmation metadata immediately below the promoted item heading:

   ```md
   Confirmation: auto
   Evidence:
   - `path/to/source.ext:42`
   Depends on auto: `Order Table`, `Order Row`
   ```

   Use `Depends on auto:` only for auto-confirmed canonical entries that materially supported this
   promotion; otherwise write `none`. Wrap every variable value — paths, term names, evidence
   paraphrases — in backticks; only the fixed keywords `auto`, `human`, and `none` may appear bare.
   Never use `[Term]` or `{Term}` notation here. `check-body.sh` strips backtick spans, so a
   backticked value is inert; a bare `items[head]` or `messages:{groupId}` in an evidence paraphrase
   would be scanned as a dangling `[ref]` or stray `{candidate}` and fail the checker after
   promotion.
4. Delete the promoted candidate from `QUESTION_CANDIDATE.md`.
5. Remove the newly confirmed term from other candidates' `Blocked by` lists.
6. Run `check-body.sh`; if it fails, fix only mechanical notation/reference issues that preserve the
   exact confirmed meaning. If the fix would alter meaning, revert the just-promoted item to the
   queue and ask the human.

When the validator returns `FAIL`, fix only generator formatting, candidate notation, broken
`Blocked by` metadata, or an obvious transcription error from the raw evidence. Do not change
candidate meaning, term names, policies, relationships, cardinality, or use-case outcomes without
human confirmation.

When the validator returns `NEEDS_HUMAN`, ask exactly one body-shaping review question and wait for
the user's answer. Do not auto-answer. If the user answers **Yes**, promote with
`Confirmation: human` and either keep the evidence block from the candidate or write:

```md
Evidence:
- `Human answer in review loop`
```

Apply the same metadata backtick rule to human-promoted items: backtick every variable value and
keep `[Term]`/`{Term}` notation out of the confirmation metadata.

## Human Escalation

The Consistency Validator's `NEEDS_HUMAN` definition is the single normative list of when to ask the
human; this section does not restate it. The coordinator asks the human in exactly two situations:

1. The validator returns `NEEDS_HUMAN` — ask one body-shaping review question and wait.
2. A mechanical `check-body.sh` fix after promotion would alter the just-promoted meaning (see
   Auto-Promotion Rules) — revert the item to the queue and ask.

Do not auto-answer in either case.

## Summary

End with the normal `$body-shaping` response summary plus:

- `Auto-promoted: N`
- `Human-required: N`
- `Validator failures fixed: N`
- `Stopped because: queue-empty | none-ready | needs-human | user-stop | check-failure`

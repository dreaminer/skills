# Consistency Gate

The deterministic gates check **provenance** — that a candidate's Evidence pointer names a real,
in-scope code line. None of them check **fidelity** — that the candidate's `Content` does not claim
more than the cited code actually shows. Because a direct System candidate can be auto-promoted,
that gap would let an over-inferred claim reach a canonical document with no human looking. The
consistency gate closes it.

## When it runs

Only for a **System** candidate on the auto-track, after `promote-next-system.py` prints
`AWAIT_GATE` and before `apply-promotion.py`. Essential candidates never reach this gate — they are
refused earlier with `NEEDS_HUMAN` (exit 3) and always require human confirmation. The gate runs for
**every** System auto-track candidate, including mechanically seeded scaffolds: a human may have
enriched a scaffold's `Content` during System-body extraction, so the `Content` at promotion time
can exceed the original code-literal seed.

## The check (isolated sub-agent)

Spawn **one** sub-agent in a **separate context**. The context that extracted the candidate cannot
reliably catch its own over-inference — a same-context self-check rationalizes exactly the overshoot
it made. Give the sub-agent **only**:

- the project root needed to read cited source files,
- the candidate's `Content`, and
- the candidate's `Evidence` (each `path:line`).

Withhold the `Type`, the canonical documents, the preview, and the staged diffs. Classification,
references, and body invariants already belong to the deterministic checks; withholding them keeps
this gate from re-judging them and drifting into their job.

The sub-agent reads each `Evidence` pointer at its `path:line` **directly** — never a paraphrase —
using `scripts/show-evidence.py <project-root> <path:line>` or `scripts/review-candidate.py`. It
confirms that:

- every factual claim in `Content` is directly supported by the code read;
- it adds no cardinality, lifecycle, policy, causality, obligation, permission, ownership, or intent
  the code does not state; and
- it drops no omission or compression that changes the candidate's meaning.

## The prompt (paste this)

This adds no criteria beyond the three above — it only fixes them into a runnable form so the gate
runs the same way every time. Fill the three `<…>` slots and send nothing else:

```text
You are a fidelity checker. You are given ONLY a project root, a candidate's Content, and its
Evidence pointers — nothing else, and you must not request anything else. For each Evidence pointer,
read the cited source line directly (never a paraphrase) with:

    python3 scripts/show-evidence.py <project-root> <path:line> --radius 3

Then check, against the code you actually read, that ALL of these hold:
- every factual claim in Content is directly supported by the cited code;
- Content adds no cardinality, lifecycle, policy, causality, obligation, permission, ownership, or
  intent the code does not state;
- Content drops no omission or compression that changes its meaning.

Output exactly ONE line and nothing else:
- READY                         — every claim is bounded by the evidence
- NEEDS_HUMAN: <one-line reason> — anything else (unsupported or over-inferred claim, evidence
                                   mismatch, or any check you cannot resolve)

Content:
<paste the candidate's Content verbatim>

Evidence:
<paste each `path:line` — detail line verbatim>

Project root:
<paste the absolute project root path>
```

## Verdict (P0 contract)

The gate is **one-hop**: it runs once and the sub-agent emits **exactly one line** — `READY` or
`NEEDS_HUMAN: <reason>`. On `READY` run `apply-promotion.py`; on anything else discard the preview
and apply nothing. There are only these two outcomes.

- **`READY`** → the `Content` is bounded by its Evidence. Proceed to apply the prepared preview with
  `apply-promotion.py`. `READY` is **additive** — the candidate must already have passed the
  deterministic evidence/conflict/duplicate/stale/preview gates; the consistency gate never replaces
  them.
- **anything else** → **`NEEDS_HUMAN`**. Discard the preview and apply nothing; the candidate stays
  in `MAKE_BODY_CANDIDATES.md` for human review. "Anything else" includes an evidence mismatch, a
  claim that cannot be bounded by its evidence (unbounded), or any check the sub-agent cannot
  resolve (`UNKNOWN`). Escalate — do not auto-promote — when the candidate's support is any of:

  - inferred policy, ownership, cardinality, permission, lifecycle, or obligation;
  - conflicting evidence or more than one plausible meaning;
  - stale, generated, fixture-only, or test-only evidence;
  - a promotion that would change the meaning of existing canonical wording; or
  - **auto-on-auto**: the candidate's only substantive support is an already auto-confirmed canonical
    entry, with no code-observed or human-confirmed backing of its own.

In P0 the gate does **not** rewrite-then-reapply. A candidate whose `Content` overshoots is sent to a
human, not silently trimmed and auto-promoted: trimming proves "the excess can be cut," not "what
remains is worth recording," and a mechanical re-trim trusts the gate's *edit* before its *judgment*
has been validated. The rewrite-then-re-check auto path is deferred to P1 under the graduation
conditions in `DESIGN.md`.

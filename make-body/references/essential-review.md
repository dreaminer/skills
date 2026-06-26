# Essential Review Protocol

How a human (or the coordinator on a human's behalf) decides an Essential candidate. Essential meaning
is a human judgment, so — unlike the consistency gate — **this is not an auto-verdict step**. No script
and no sub-agent may approve an Essential candidate. `promote-next-system.py` refuses every Essential
candidate with `NEEDS_HUMAN` (exit 3), and that never changes.

## What the script gives you (deterministic)

`review-candidate.py <project-root> <docs-dir> <MB-id>` renders, for an `essential-domain` or
`essential-usecase` candidate, a fixed frame on top of the normal candidate + Evidence view:

- the candidate's Subject, Type, Content, and each Evidence pointer's source window;
- **co-located canonical System terms (lexical)** — the `SYSTEM_DOMAIN` / `SYSTEM_USECASE` subjects
  whose every token appears in the candidate's `Content` or cited Evidence line. This is token
  co-occurrence, not a claim that the term is *related*; a human decides whether each one matters and
  ignores incidental same-word hits;
- a fixed reviewer checklist.

The script renders the frame and nothing more. It does not author the questions, decide what the code
cannot establish, or score the candidate — those are yours.

## What you decide (judgment — not in any script)

Read the cited code first; never paraphrase it from the candidate. Then:

1. **Author the confirming questions.** What must a person who knows the business confirm before this
   meaning is recorded? The questions are candidate-specific and come from you, not the script.
2. **Name what code cannot establish.** Mark every part of the Content that the cited code does not
   force — intent, policy, ownership, cardinality, lifecycle, obligation. These are the points a human
   must affirm, not assume.
3. **Check the System/Essential boundary.** The Subject must name a business concept, not a System
   artifact (endpoint, table, queue, protocol). A co-located System term that the candidate is merely
   restating is a signal the candidate is System, not Essential.

## Verdict — one of three, all human

- **Approve** — a person confirms the meaning. Only then does the candidate proceed through the normal
  `prepare-promotion.py` → review → `apply-promotion.py` path. There is no Essential auto-apply.
- **Revise** — the meaning is close but the `Content` over- or under-claims. Edit the candidate's
  `Content`/`Evidence` in the queue, then re-render and review again.
- **Reject** — legacy, accidental, wrong implementation, or not the business meaning. This is the
  two-step rejection: append the `MR-{nnn}` record to `MAKE_BODY_REJECTED.md` **and** delete the
  candidate from the queue. `check-rejected.py` flags a half-done rejection (record without dequeue).

A candidate merely awaiting this review is **not** rejected — it stays queued. Rejection is terminal;
review is not.

## Relationship to the consistency gate

The consistency gate (`consistency-gate.md`) is an isolated sub-agent that returns an automatic
`READY` / `NEEDS_HUMAN` verdict for a **System** candidate's fidelity, so directly-evidenced System
language can auto-promote. This protocol is its deliberate opposite: Essential meaning is confirmed by
a person, the frame is an aid to that person, and the outcome is always a human decision.

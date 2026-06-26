# First Run — A Worked Trace

One small session, end to end, so the loop's steps are seen connected rather than as separate rules.
This adds **no** new rules — every step here is governed by `SKILL.md` and the references. It exists
to reduce drift: read it once before your first real run.

The example project (`club/`) is tiny:

```text
club/
  README.md          "Members belong to a club. Each member has one membership tier."
  db/schema.sql      members(id, club_id NOT NULL REFERENCES clubs(id), tier, joined_at)
  src/join.ts        createMembership(clubId, userId) -> inserts a members row
```

Docs are written under `club/docs/` (see `references/document-templates.md` for the six files).

---

## 1. Recover — read sources, queue atomic candidates with `Type` + `Basis`

Reading README → schema → route, each finding becomes one `Q-{nnn}` with a single confirmable claim.
`Type` (layer × shape) and `Basis` (truth-maker source) are both assigned **at queue time**:

```md
## Q-001
Type: essential-domain
Subject: Member
Basis: observed
Content:
- [Member]: a person who belongs to a club.
Evidence:
- `club/db/schema.sql:1`: members table; `README.md:1`: "Members belong to a club"
Blocked by:
-

## Q-002
Type: essential-domain
Subject: Member Organization Membership
Basis: observed
Content:
- [Member] belongs to exactly one [Club].
Evidence:
- `club/db/schema.sql:1`: `club_id NOT NULL REFERENCES clubs(id)`
Blocked by:
- {Club}

## Q-007
Type: essential-domain
Subject: Member Archive
Basis: proposed
Content:
- [Member] may be archived after 12 months of inactivity.
Evidence:
- proposed flow: "we want to archive dormant members after a year"
Blocked by:
-
```

`Q-001`/`Q-002` are **observed** (a `path:line` backs them). `Q-007` is **proposed**: no code states
it; human judgment is its truth-maker. The `schema.sql` line could be *cited* on a proposed candidate
as provenance, but it would not back the claim — so the candidate stays `proposed`.

> If a candidate were queued without a `Basis:` line, the selector in step 2 would print
> `invalid-basis Q-00N` and exit 3 — a malformed queue fails loud, it is never asked or dropped
> silently. Fix the candidate, don't default it.

---

## 2. Select — `scripts/next-question.sh` picks the next question

```console
$ sh scripts/next-question.sh club/docs
Q-001 essential-domain observed
```

Essential before System, Domain before UseCase, lowest `Q-` among ready candidates. `Q-002` is
blocked (`{Club}` unconfirmed). The third token, `observed`, drives step 4.

---

## 3. Re-evaluate — the per-candidate judgment the selector cannot make

`[Member]` is not yet canonical and clashes with nothing in `ESSENTIAL_DOMAIN.md`. Proceed. (If the
same word were already canonical with a different meaning, surface the clash instead of asking.)

---

## 4. Gate — `observed` runs it; `proposed` skips it

`Q-001` is `observed`, so the consistency gate runs (protocol: `references/consistency-gate.md`). A
separate-context validator reads `club/db/schema.sql:1` directly and confirms the question's
`Content` ("a person who belongs to a club") does not overshoot the evidence → **`READY`**.

A `REWORK` example, on `Q-002`: suppose the generated question read *"belongs to **exactly one**
[Club], and a Club must have at least one Member."* The validator reads the FK and finds support for
"one club per member" but **none** for "a club must have at least one member." It returns:

```text
REWORK
REMOVE_EXACTLY: , and a Club must have at least one Member
```

The main agent deletes that exact phrase from **both** the `Q-002` queue `Content` and the displayed
question (so `Yes` confirms what was validated), then shows it — without re-generating or re-calling
the validator.

`Q-007` is `proposed`: the gate is **skipped entirely** (no sub-agent). It still goes through the
same structural question check as every candidate before Review, but is not presented as source-grounded.

---

## 5. Question check — validate the queued question before Review

`Q-001` already stores the canonical header name separately from its Content:

```md
Subject: Member
```

The script reads that queue entry and the current canonical body:

```console
$ sh scripts/check-question.sh club/docs Q-001
OK -- Q-001 is structurally ready for Review.
```

If this check failed, the agent would repair the candidate's structural issue and repeat
Re-evaluate; it would not ask the user an invalid question.

---

## 6. Review — show the confirmed structure; the user owns content

```text
Progress: 0/7 resolved (0 confirmed + 0 rejected; 7 open).
Target: Essential × Domain
Subject: Member
Why this layer × shape: a core business concept, a static meaning (not a Given/When/Then flow)
Content:
- [Member]: a person who belongs to a club.
Is this right?
- Yes
- Something else
```

`Evidence` is deliberately absent here — it is pulled up only if the user hesitates or asks where the
candidate came from. The user answers **Yes**.

For the proposed `Q-007`, the same shape is shown, but the user is the truth-maker. They answer
*"Something else — only after 24 months"*; the main agent narrows the candidate accordingly before it
can be promoted.

---

## 7. Promote — deterministic on `Yes`

- Write `[Member]` into `club/docs/ESSENTIAL_DOMAIN.md` under a `## [Member]` header.
- Delete `Q-001` from the queue.
- Sweep `{Member}` out of every other entry's `Blocked by` — none here, but confirming `[Club]`
  later would unblock `Q-002`.

`Something else` instead routes to the free-text path (reword / requeue / reject to `REJECTED.md`) —
never a fixed table of outcomes.

---

## 8. Check — verify the actual canonical write

```console
$ sh scripts/check-body.sh club/docs
OK -- 1 confirmed term(s); refs resolve to the correct layer; no stray {candidate}.
```

No `{candidate}` notation leaked into a canonical doc, and every `[Term]` resolves in its allowed
layer. This is a post-write assertion: a failure means the real write violated the canonical-body
invariant or the body changed after the question check. Then run the selector again for the next question — the loop
continues until the queue is empty.

---

### What this trace shows

- `Type` **and** `Basis` are set once, at Recover.
- The selector's third token routes the gate with no extra judgment.
- `observed` → gate validates against `path:line`; `proposed` → gate is skipped and the human is the
  truth-maker.
- A `REWORK` is a mechanical dual-write, applied to queue **and** question, single hop.
- Every final question passes `check-question.sh` before it is shown.
- The post-Promote checker verifies the real canonical write, rather than deciding whether the
  approved content was valid.
- A missing `Basis` would have failed loud at selection, never silently.

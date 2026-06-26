# body-shaping — Design Rationale

> Why this skill has the shape it does. Read this **before** expanding the skill or discussing it
> with another model. It is intentionally **not linked from `SKILL.md`** and never loads at runtime
> — it exists for maintainers, not for the running skill.
>
> Discipline: record **decisions and their why**, plus **rejected alternatives**. Not a transcript.
> If this file starts narrating history blow-by-blow, trim it — the same restraint the skill itself
> follows.

## North Star

Give an unstructured project a **confirmed domain body**: recover the real vocabulary scattered
across code, tests, docs, and schemas, split it into **Essential** (what the business means) and
**System** (what the implementation calls things), and write down **only what a human has confirmed**
— so later work runs on a settled vocabulary.

Everything below serves that one sentence. If a proposed change does not serve it, it does not belong
in the skill.

## Core principles (these govern future decisions)

1. **Two jobs, kept separate.**
   - *Classification is the LLM's job.* Every candidate's `Type:` = layer (Essential/System) × shape
     (Domain/UseCase). The LLM assigns it by reading the candidate. **Never ask the user which layer
     or shape something is** — the model reads form and surrounding domain better than the user.
   - *Confirmation is the human's job.* The human confirms **content** only (what a term means,
     whether a use case is real). **Nothing is canonical without human confirmation — all four
     documents, System included.**
   - This split is why "who decides the layer" is settled and why confirmation is uniform.

2. **Boxify the question; do not classify the answer.** The question is always *"is this right?"* with
   two answers: **Yes** / **Something else** (free text). `Yes` → deterministic write. `Something
   else` → read and act with judgment. This moves disambiguation from *after* the answer (a 10-row
   table + guards classifying messy prose) to *before* it (the user picks). It is the single change
   that removed the most machinery.

3. **Derive, don't store.** Anything computable from the body is not stored separately, because a
   stored copy drifts. (`Status` is derived from `Blocked by`; dependencies are the bracketed
   `[Term]` references, not a separate checklist.)

4. **No guards for hypotheticals.** Do not add a rule to defend against a failure that has not
   actually happened in a real run. Add it only when a real run produces the failure.

5. **Don't re-table "Something else."** Disagreements are too varied to enumerate. The moment someone
   turns the free-text path back into a classification table, the bloat returns.

## Key decisions

| Decision | Why |
|---|---|
| LLM assigns layer×shape; the user is never asked the axis | The user confirms substance; the model classifies. Resolves the long-unanswered "how is Essential vs System assigned." |
| Confirmation is uniform across all four documents | Essential and System are both human-confirmed. The layer split is abstraction level, not an exemption from confirmation. |
| Promote = `Yes` / `Something else` boxes | See principle 2. Collapsed a 10-row table + Guards A–E into a deterministic-on-`Yes` lookup. |
| Conflict handled at ask-time, not write-time | A same-layer same-word clash is prevented when the question is posed (Re-evaluate splits same-meaning → drop vs different-meaning → disambiguate), not repaired after a bad write. |
| Same word across layers is parallel, not a duplicate | The four-document skeleton is built to host one word in both Essential and System. |
| Essential/System are abstraction layers | Essential captures the conceptual domain model and flow; System captures the runtime/implementation model and execution flow. The split is not "business words vs technical-looking words." |
| UseCase flows use Given/When/Then | Real runs promoted static invariants like "a Client belongs to one Group" as use cases. Static identity, ownership, cardinality, values, states, responsibilities, relationships, and invariants now stay in Domain; UseCase is reserved for Given/When/Then connections between domain concepts. |
| `REJECTED.md` uses a free-text `Reason` field, not a status enum | The earlier `rejected/legacy/accident/rejected-framing` subtypes were the same "classify the answer" table that Principle 5 forbids — just smaller. Free text matches Promote's `Something else` path and lets the LLM read the reason natively. |
| `check-body.sh` enforces **directional** layering, not per-layer confinement | The original bug was an Essential UseCase referencing a System Domain term — the *inversion* (abstract depending on concrete). The first fix over-corrected: it confined every layer to itself, which also blocked the **sound** direction (System referencing Essential), even though the skill *defines* System as "operational concepts used to execute the Essential flow." The real invariant is directional: **System may resolve refs in Essential (concrete depends on abstract); Essential may never resolve in System.** So `SYSTEM_DOMAIN`/`SYSTEM_USECASE` refs resolve in their own layer **or `ESSENTIAL_DOMAIN`** (plus `SYSTEM_USECASE`'s `Related Essential Use Case:` → `ESSENTIAL_USECASE`); `ESSENTIAL_*` refs stay within Essential. Notation stays single `[]`/`{}`: layer is already carried by the document and by a candidate's `Type:`, so a second bracket form (`[[]]`/`{{}}`) would be a redundant third encoding that drifts — rejected. |
| `check-question.sh` validates the selected queue entry before human Review; `check-body.sh` asserts the real write after Yes | A user should see only a structurally ready question. `Subject:` is stored in the queue rather than inferred from Content, so `check-question.sh` can mechanically validate the selected entry's field shape, readiness, candidate notation, and layer-aware references against canonical headers. A failure returns to Re-evaluate before the user is asked. After Yes, `check-body.sh` runs on the real body only to detect a write/state mismatch — not to retroactively judge approved content. |
| Progress (`resolved/total`) is printed by `scripts/progress.sh`, derived from file state — not stored, not hand-counted | Reporting, not machinery: no stored counter, no answer-classification. A dedicated script keeps it token-free and deterministic — the model relays one line instead of reading six docs to count headers itself (which costs tokens every turn). Kept separate from `check-body.sh` so the guard's single responsibility (`[Term]` discipline) stays intact; `progress.sh` only counts and never gates. `confirmed` (`## [..]` headers) + `rejected` (`## R-`) = resolved; `+ open` (`## Q-`) = total. Chosen over a max-`Q-{nnn}` counter, which is unrecoverable once promoted entries leave the queue; counting current items obeys principle 3 (derive, don't store) and survives deletion. |
| Question order is chosen by a **stateless** `scripts/next-question.sh`: Essential before System, then Domain before UseCase, then lowest `Q-`, over ready candidates only | The user's intent — when a new Essential candidate appears mid-System, return to Essential before continuing — is met *because the selector keeps no cursor*: it re-reads the whole queue each call, so late-discovered Essentials preempt remaining System questions with nothing to go stale (principle 3, derive don't store). It is a **priority sort, not a one-time gate**; a gate would be violated by progressive Recover discovery. Mechanical ordering off the queue's `Type:`/`Blocked by:` keeps it token-free and stops the order drifting on prose discipline (same rationale as `check-body.sh`). Meaning-level Re-evaluate (same word, different meaning → clash) stays the model's job on the chosen candidate; the script picks order, never judges. |
| The review question shows `Progress` on top and omits `Evidence`; provenance is pull, not push | The running `resolved/total` (from `progress.sh`) sits at the top so the user sees it while answering. `Evidence` is removed from the asked question and kept only in the `QUESTION_CANDIDATE.md` entry — it is look-it-up-on-doubt information, surfaced only when the user hesitates or asks where a candidate came from, so the first-level question stays short. Storage keeps it; presentation drops it. `Approval target` was shortened to `Target`, `Candidate` was renamed `Subject` (the field names the decision's subject — the identifier being canonized — not a summary of `Content`), and the redundant `Question:` echo (which re-stated the target) was dropped in favor of a constant `Is this right?`. |
| Queue stores bare `Content`; `Is this right?` is rendered, not stored | Promote canonizes the queued candidate, while the consistency gate validates displayed `Content`. Storing the same bare string in both places makes `Yes` refer to exactly what was validated and shown; a stored prompt wrapper would make that equality impossible. |
| File evidence is anchored at `path:line` | The consistency gate must read the exact source that supports each claim. A path without a line forces inference over an arbitrary file region; a proposed-flow sentence remains the explicit no-file exception. |
| `Blocked by` is the sole readiness source | The selector derives readiness mechanically from this one field. `{Candidate Term}` notation must be reflected there as a queue invariant, rather than creating a competing text-based readiness rule. |
| A 1-hop **consistency gate** validates every generated question's evidence → `Content` fidelity before it is shown | This is **not** a guard against a hypothetical failure (principle 4 does not bar it) — it is a precondition of the skill's own contract. The user confirms domain *content* while trusting the question was faithfully derived from the project; the domain is *not* fully in the user's head (that is why the skill exists), so a question whose claims overshoot their evidence makes the confirmation unsound. The user owns domain truth; the gate owns derivation fidelity. Scoped narrowly to stay off the "adversarial review has no stop condition" failure: **one** separate-context sub-agent (the writing context cannot catch its own over-inference); fed only the candidate `Content`/`Evidence` and the question `Content` — **no** canonical docs and **no** `Type:`, so it cannot drift into the classification/clash/reference work Re-evaluate and `check-body.sh` already own; it reads file `Evidence` at `path:line` directly, so the check is source-to-question, not a re-check of the generator's paraphrase. `REWORK` must return the **exact** safe edit (`SAFE_CONTENT:` verbatim replacement, or `REMOVE_EXACTLY:` phrases to delete mechanically); the main agent applies only that and never re-generates freely or re-validates — free regeneration would emit an unvalidated sentence and forfeit the single hop. The correction is applied to **both** the queue candidate and the shown question, because Promote canonizes the *queue candidate* on `Yes`, not the displayed string — correcting only the question would let the original over-inference reach canonical while the user saw the narrowed wording, breaking "`Yes` is a Yes to the displayed content." Un-narrowable claims fall back to the ordinary `Is this right?` / `Something else` human question, not dressed up as source-grounded. Motivated by the contract above, **not** by a logged run failure — the only reproduced failure in this project is the metadata bracket footgun; no "observed over-inference" claim is recorded because none was captured. |
| **`Basis` (`observed`/`proposed`) routes the gate** — a one-bit truth-maker source per candidate, set at Recover | Closes the mixed-evidence hole: a candidate carrying both a file `path:line` and a proposed-design sentence could make the gate validate a *proposed* claim against a file and wrongly `REWORK` it (a false positive). The fix is one bit of **truth-maker source**, deliberately **not** a per-clause annotation of `Evidence` — that was rejected as over-engineering, because atomicity already splits different claims, and a claim with any proposed component is wholly `proposed` (its file a provenance note, not its truth-maker). `observed` = a `path:line` is the claim's truth-maker → gate runs; `proposed` = human confirmation is → gate skipped. `Basis` is **not** derivable from `Evidence` (a cited file may be truth-maker *or* provenance), so it is stored like `Type:`, consistent with principle 3 (derive don't store applies only to what *is* derivable). Missing/unknown `Basis` is **fail-loud** (`scripts/next-question.sh` prints `invalid-basis Q-{nnn}`, exit 3) at selection, never silently defaulted: a silent default to `proposed` would silently skip the gate — the exact FN the gate exists to prevent — while a silent default to `observed` merely wastes a hop; the asymmetry forbids any default. The selector emits `Basis` as its third output token so the spawn decision is made from that one line, never a second read. |

## Rejected alternatives (do not reintroduce without a new, real reason)

- **Carrier taxonomy** (callable vs artifact vs unknown, bounded-evidence rules). *Rejected:*
  orthogonal to the essence — recovery + layering is not identifier parsing — and the model
  approximates shape from form anyway. Collapsed to one line: classify by meaning and use, not
  spelling.
- **Provisional candidate status + its guard.** *Rejected:* it existed only to restrict the weak
  back-check promotion path; boxify deleted that path, so it had nothing left to restrict. A term
  sourced only from a proposed use-case sentence is just an ordinary candidate.
- **`DOMAIN_CHANGE_CHECKLIST.md`.** *Rejected:* it is a dependency list, and dependencies already
  live in the body (a use case's bracketed terms; the System↔Essential mapping). A separate copy
  drifts. Replaced by one rule: before changing a term, trace its `[Term]` references.
- **`promote-signals.md` phrase dictionary.** *Rejected:* it is exactly the "classify the answer"
  table that boxify made unnecessary and that principle 5 forbids. The model reads "no" / "legacy"
  natively.
- **`REJECTED.md` status enum** (`rejected/legacy/accident/rejected-framing`). *Rejected:* same
  shape as the `promote-signals.md` table above — a fixed enumeration of "Something else" outcomes.
  Free text + an optional `Replacement / current rule` line covers every case the enum did, without
  pulling judgment back into a lookup table.
- **Free re-generation after a consistency `REWORK`** (the main agent rewrites the flagged question
  itself). *Rejected:* the validator inspected only the *previous* sentence, so a freshly written one
  can carry a new, unvalidated over-inference and the single-hop gate would no longer bound what the
  user sees. `REWORK` instead returns an exact mechanical edit (`SAFE_CONTENT` verbatim replacement,
  or `REMOVE_EXACTLY` phrases to delete); the main agent applies only that, and anything that cannot
  be narrowed into evidence goes to the human as an ordinary `Is this right?` / `Something else`
  question.
- **Same-context self-check instead of a separate sub-agent.** *Rejected:* over-inference is exactly
  what the generating context rationalizes; only a fresh-context reader given the raw `path:line`
  evidence makes the check independent.

## Failure modes to avoid (the most important section)

- **Adversarial review has no stop condition.** Asking a model to "find holes" in a natural-language
  spec always succeeds — you can always construct a new pathological input. Seven such rounds bloated
  this skill by converting every act of judgment into a rule. Hardening edge cases past the essence
  has negative return.
- **Armchair editing is the trap.** All of that bloat was reasoning about hypothetical inputs without
  ever running the skill. **Run it on a real project and let real failures drive changes.** That is
  the only reliable stop condition.
- **`body-setting` is a separate effort — do not conflate it with `body-shaping`.** They share a name
  prefix and once sat in the same commit; that is not shared lineage. (This document's author made
  exactly that mistake while writing this redesign — recorded here so the next reader does not.)

## Deferred to a real run — the gate-value experiment

The consistency gate is kept ON for `observed` candidates, **but its value is not yet validated**.
Per this file's own first lesson — run it on a real project; let real failures drive changes — the
following are deliberately **not** decided here. They must come from a real end-to-end trace, not
another armchair round:

- **Sample**: fix the source scope of ≥2 representative real projects *before* the run, complete one
  Recover pass per project, and evaluate **every** resulting `observed` candidate. `N` is the
  resulting candidate count — a census, not a pre-chosen cap — reported per-project and as a total.
- **Measure, blind**: a human source-reader (not necessarily a domain expert) adjudicates the
  **whole** sample — `READY`s included, so false negatives are observable — against the raw `Content`
  and each `path:line`, **blind to the gate's output**, yielding TP / FP / **FN**. Each TP/FN is
  tagged severity *wording-only / meaning-narrowing / meaning-inventing*; only narrowing and inventing
  count as fidelity errors. (Severity is an experiment tag only — it never enters the gate's runtime
  rules, which would re-table the judgment principle 5 forbids.)
- **Decide by loss asymmetry** over the census — the one hard, numeric trigger is a
  source-confirmable meaning-inventing **FN ≥ 1** → redesign (not remove — the worst miss means the
  *mechanism* needs work, and removing leaves no guard). The rest is a qualitative read of the same
  census, with no pre-set numeric thresholds: meaningful TP + low harmful FP/FN → keep ON; no TP + no
  harmful FP/FN across the whole census → keep ON if hop cost is acceptable, else move to opt-in;
  harmful FP recurring → opt-in or remove.
- **Cost lever before any opt-in**: the gate already spawns only for `observed` candidates
  (`proposed` skip mechanically), shrinking the firing population with no meaning judgment. Narrowing
  it further by risk-words / `Type` / domain kind is **rejected** — that re-tables classification.
- **No golden fixtures from imagination**: shell tests pin only the mechanical selector / `check-body`
  contract. The gate is an LLM judgment; add a golden case only when a *real* trace produces one.

`FN`-absence over the census is a sample observation, not a safety proof — report it with N, never as
"the gate is safe."

## How to use this when expanding the skill

1. Re-read the North Star. Does the change serve it?
2. Check it against the five principles. A change that violates one is almost always wrong.
3. Check the rejected list. If you are about to add one of these back, you need a *new, real* reason —
   ideally a failure observed in an actual run, not a hypothetical.

# body-auto-shaping — Design Rationale

> Maintainer notes for changes to `body-auto-shaping`. Not loaded at runtime. Keep
> decisions and rejected alternatives so the next maintainer does not reopen the
> same design arguments without a real failure.

## North Star

Automate the `Yes` branch of `$body-shaping`'s review loop by **default**: once a candidate clears `$body-shaping`'s consistency gate (its question is a faithful, evidence-bounded derivation), auto-confirm it — including a new domain term or definition — and send it to the human **only** when one of **two** checks fails — **coherence** (the source's own description is logically sound) or **consistency** (no conflict: inside a doc, inside the code, between doc and code, against canonical, or a naming clash). Grounding is already guaranteed upstream by the gate (un-grounded claims become `proposed` → human), so the Approver certifies just those two. Everything that clears both is auto-`APPROVE`.

## Design intent — "what can't be `Yes`?"

`$body-shaping` generates a domain for a project that had none, so the human reviewer has no prior
domain authority to draw on: **if a claim is genuinely in the code or docs, an honest review almost
always answers `Yes`.** A reviewer only dissents when they bring knowledge *beyond* the evidence — and
that case never reaches this Approver, because `$body-shaping`'s gate has already flipped any claim
that overshoots its evidence to `proposed` and routed it to the human. So the Approver only ever
sees **evidence-faithful** candidates, and for those the question "what can't be `Yes`?" has exactly
two answers: it does not hold together (coherence) or it clashes with something (consistency).
Everything else is `Yes`. The whole skill is: *auto-`Yes` everything except those two.*

### Rejected — an extra guard for "Essential from code/test alone"

Considered and dropped (2026-06-22). The worry was that coherence + consistency are both internal
checks and miss a third class: sources that agree and cohere but are not the *intended / current /
complete* domain (e.g. an implementation term canonicalised as if it were the business term).
**The gate already guards this.** An Essential claim asserts meaning; code shows only structure, so a
code-only Essential claim overshoots its evidence at the gate → it is narrowed (`REWORK`) or, if
un-narrowable, **flipped to `proposed` → human** before the Approver runs. The only residue that
survives the gate is a claim narrowed to a code-*faithful* reading — i.e. pure vocabulary or
staleness drift, which (a) this skill's owner has explicitly chosen to accept ("names pass by
default; their base is the code or doc"), and (b) an unaided human reviewer could not catch either.
Adding an Essential-only guard would duplicate the gate's `proposed`-flip and re-import the
conservatism this skill exists to shed.

## What this skill deliberately is not

This skill exists alongside `$auto-body-shaping` and `$yolo-body-shaping`. It is the smallest of the three.

| Feature | `$body-shaping` | `$body-auto-shaping` (this) | `$auto-body-shaping` | `$yolo-body-shaping` |
|---|---|---|---|---|
| Sub-agent Approver decides Yes | — | yes | yes | yes |
| Inline `Confirmation: auto` metadata | — | no | yes | yes (split labels) |
| Visible `· A` Approver marker | — | yes | no | no |
| `Evidence:` / `Depends on auto:` lines | — | no | yes | yes |
| Auto-loop to queue-empty | — | no | yes | yes |
| `Auto-promoted / Human-required` counters | — | no | yes | yes (more) |
| Question Generator + Approver role split | — | no (one Approver) | yes | yes (+ Decision Maker) |
| `INFERRED_*.md` segregation | — | no | no | yes |

A user who wants any feature in the "no" column should pick the matching skill, not extend this one.

## Decisions

| Decision | Why |
|---|---|
| One sub-agent, not two | `$body-shaping`'s consistency gate already spawns one sub-agent for derivation fidelity (`READY` / `REWORK`). This skill adds one more for the Yes-territory check. A combined check would replace the gate; we keep the gate untouched so this skill remains a thin wrapper. |
| Visible `· A` header suffix, no provenance metadata | Rendered output needs a minimal indication that the Approver, not a human, supplied Yes. The suffix stays outside `[Term]`, and `> A = Approver` appears once per document that uses it. It does not carry evidence or dependency data, so `$auto-body-shaping` remains the right choice when an audit trail is needed. |
| Single-candidate invocation, no auto-loop | A loop adds machinery (`check-body.sh` failure handling, stop conditions, counters) for marginal convenience. The user can re-invoke; the cost of one re-invocation is lower than the cost of a misbehaving loop with hidden failures. |
| `APPROVE` requires `Basis: observed` | `proposed` candidates have the human as truth-maker by definition (see `body-shaping/references/consistency-gate.md`). Auto-`APPROVE` on `proposed` is a category error: there is no file to ground the claim against. |
| Escalate only on a coherence or consistency failure (two checks) | The Approver certifies exactly two things: **coherence** (the source's own description is logically sound) and **consistency** (no conflict — inside a doc, inside the code, between doc and code, against canonical, or a naming clash). It traces a bounded related context from the cited range: its enclosing document section; direct code callers/callees and directly connected route, schema, storage, or transport declarations; and documentation/canonical uses of the candidate term or a directly evidenced alias. There is **no** independent "genuine judgment" trigger and **no** "any uncertainty → human" rule: a hard-to-say-`Yes` case is always a conflict, an incoherence, or an un-grounded claim — and un-grounded claims are the gate's job (`proposed` → human) *before* the Approver runs. The Approver invents no caution beyond the two checks and never blocks a candidate merely for being new. |
| Term names pass by default; only a naming clash blocks | Supersedes the original "code identifiers are not naming evidence → term-name introduction is always `NEEDS_HUMAN`" rule (2026-06-22). On an empty document set every term is new, so the blanket gate routed the whole vocabulary-establishing phase to the human and the wrapper delivered zero auto value (the **Group bootstrap** run, recorded below). A name's base is the code or the doc, so it is a fact to accept, not a choice to ratify. It escalates only on a **naming clash** (a consistency failure): the same name used with different meanings, or different names used with the same meaning. The original anti-drift concern — a code identifier silently becoming canonical — is caught by the document↔code conflict case of consistency, not by refusing every term. |
| UseCases via the same two checks | A UseCase that merely echoes a code/schema write the cited source obviously enacts is grounded, coherent, and unconflicted → `APPROVE`. A UseCase proposing behavior the code does not enact is *un-grounded*, so `$body-shaping`'s gate flips it to `proposed` → human before the Approver runs. No special UseCase gate beyond the two checks. |
| Test / fixture / generated evidence is accepted | Owner call (2026-06-22): honor the literal rule — a definition with no conflict and no logical defect auto-passes even when its only evidence is test, fixture, or generated code. The consistency gate already guarantees the question is a faithful derivation of that evidence. This intentionally diverges from `$auto-body-shaping` (whose `SKILL.md` requires human-authored product/domain language for Essential content); do not re-tighten it without the owner. |
| Approver searches bounded related context while **withholding** `Progress` and `Type:` rationale | The first gate owns evidence → Content fidelity. The Approver owns only surrounding coherence and consistency, so it starts at cited ranges and searches direct implementation/document neighbors rather than re-reading the entire project or re-judging classification and queue scheduling. |

## Rejected alternatives

- **Replace `$auto-body-shaping`.** The two skills implement different trade-offs (audit trail vs. minimum machinery). Both have legitimate users; coexistence is cheap.
- **Combine the gate and the Approver in one sub-agent.** Tempting (one fewer spawn per `observed` candidate), but requires modifying `$body-shaping`'s gate contract. Too invasive for a wrapper.
- **Auto-loop to queue-empty.** Re-invocation is cheap and observable; an auto-loop hides failure modes. If a loop is desired later, build it as a separate driver, not as machinery inside this skill.
- **Add a Decision Maker for `UNDECIDED` verdicts (yolo-style inferred isolation).** Belongs to `$yolo-body-shaping`. This skill keeps two verdicts: `APPROVE` or `NEEDS_HUMAN`. Anything in between is `NEEDS_HUMAN`.
- **Provenance sidecar (`BODY_PROVENANCE.md`).** Same drift problem `$auto-body-shaping`'s `DESIGN.md` already noted: sidecars drift on rename and delete. If audit is needed, use `$auto-body-shaping`'s inline metadata.
- **Generator + Approver role split.** `$auto-body-shaping` splits these to add a "question faithfully represents the candidate" check. This skill relies on `$body-shaping`'s gate for derivation fidelity (`READY` / `REWORK`) and gives the same question content to the Approver. Adding a Generator pass here would re-do work the gate already did.
- **`Auto-Yes` counters across invocations.** No persistent state in this skill. Counting auto-promotions across runs is an audit problem; `$auto-body-shaping` already owns that question.

## Failure modes worth watching

- **Approver re-inventing a judgment escape-hatch.** There are only two checks; a `NEEDS_HUMAN` whose reason is not a concrete coherence or consistency failure smuggles back the deleted "any uncertainty → human" rule and re-creates the Group bootstrap stall. A run that routes a clean, coherent, unconflicted term or definition to the human is the regression to watch.
- **Missed conflicts auto-promoting drift.** The consistency check is now the *only* thing between a code identifier and canonical terminology, so the Approver must trace the bounded related context — not only skim the cited lines — to compare relevant document and code behavior and look for naming clashes. A missed doc↔code conflict auto-promotes implementation drift — the harm the old blanket term-name gate used to prevent.
- **Approver returning `APPROVE` on a UseCase claim that "looks mechanical" but is actually un-grounded policy/intent.** UseCases are higher-risk than Domain terms; a policy the code does not enact should have been flipped to `proposed` by the gate, not echoed as mechanical. A grounded-looking UseCase that smuggles in behavior the code does not actually perform is a document↔code consistency failure. If this surfaces, harden the gate's narrowing or the consistency wording.
- **Approver over-trust of `path:line` ranges that drift after edits.** Line numbers are a verification snapshot, not a live pointer. If the Approver runs after the source has moved (so the read precondition cannot be met cleanly), it `NEEDS_HUMAN`, not paper over a mismatch.

If any of these surface, record the failing candidate in this file (with the cited evidence and the wrong verdict) before changing the rule in either direction. Premature hardening — or loosening — without a real failure is exactly the kind of cruft this skill exists to avoid.

## Recorded runs

- **Group bootstrap (drove the 2026-06-22 reversal).** Run against an **empty** document set. The
  first selected candidate was the Domain term `Group`. Under the original contract it was routed to
  the human purely because "a new term name choice" was `Always NEEDS_HUMAN` — not because anything
  was wrong, ambiguous, or conflicting. Because every term in an empty doc set is new, the wrapper
  could auto-confirm nothing until a human had hand-seeded the vocabulary, i.e. it added no value in
  the phase it exists for. The verdict was technically correct under the old rule, and that is the
  problem: the rule, not the run, was wrong. Fix: invert to default-`APPROVE` with the two-check
  escalation above.

## Positioning vs. the sibling skills

Escalation-aggressiveness and machinery are **orthogonal axes**. After the 2026-06-22 reversal this
skill has the *most permissive* human-gate of the family (it auto-confirms new terms/definitions and
test-only evidence) while keeping the *least* machinery (a one-character header suffix, no provenance
metadata fields, no loop, no counters — see the table above). That combination is intentional, not an oversight. Aligning `$auto-body-shaping` or
`$yolo-body-shaping` to the same two-check model is a possible follow-up but is **out of scope**
here: this change touches `$body-auto-shaping` only.

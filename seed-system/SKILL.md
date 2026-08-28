---
name: seed-system
description: 비준된 Seed body에서 Acceptance 계약, test 연결 계획, 구현 기본안을 사람과 비준한다. 사용자가 seed-system 단계만 명시 요청했거나 active seed-loop가 System owner로 선택했을 때 사용한다.
---

# Seed System

## Purpose

Turn a seed-body package into an implementation-ready Acceptance body without creating a separate
canonical System layer.

```text
frozen Essential language + parked System utterances
  -> raw system-flow evidence and design constraints
  -> human-ratified Acceptance scenarios
  -> implementation proposal
  -> test handoff records for RED/GREEN verification
```

`ACCEPTANCE.md` is the human contract; executable Acceptance tests are the mechanical constraint
on implementation. This skill writes no production code and authors no tests. It prepares the
contract, the agreed public seams, and the test-link records that a later `$seed-tdd` workflow
consumes.

Read `DESIGN.md` before changing these rules. It owns the ownership map and the edit gates that
decide what may become a rule in this skill.

## Identity principles

This list is frozen. It is judgment guidance, not a script-enforced gate. Adding a principle — or
rewording one so that it demands more — requires user ratification.

1. Ask one question at a time during divergence; rotate weak slots breadth-first.
2. Split each user utterance three ways: inherited Essential intent, system-flow constraint,
   implementation hint.
3. Treat Essential as read-only. Route new Essential intent to a back-to-Essential question;
   never invent missing Essential intent.
4. Converge in two stages: meta-ratify the closing criteria, then batch-ratify the full
   Acceptance body.
5. Propose implementation defaults only after Acceptance is ratified; when they conflict,
   Acceptance wins.
6. Choose the lowest stable public seam that can observe every `Then`; keep implementation
   detail out of Given/When/Then.
7. Publish no System canonical (`SYSTEM_DOMAIN.md`, `SYSTEM_USECASE.md`); System material lives
   in working evidence or `SEED_SYSTEM_IMPL_PROPOSAL.md`.
8. Human ratification is the only truth-maker; a GREEN test is not evidence of intent.
9. Stage no AC that merely restates an inherited Essential use case; look for one recorded
   decision beyond the inherited sentence — a decidable boundary, an exclusion, or a system-flow
   behavior. A finding that only seam selection was needed qualifies.

## Files

Read the seed-body package from the target project's `docs/` (input contract in
`references/artifacts.md`). If no package is found, ask once for its path; if the user confirms
none exists, route them to seed-body and stop. Do not start from conversation-only evidence.

Write three contract files under `docs/` — formats owned by `references/artifacts.md`:

- `ACCEPTANCE.md` — human-ratified v1 scenarios, hash-linked to tests.
- `SEED_SYSTEM_TESTS.md` — test command, test directory, one lifecycle record per AC.
- `SEED_SYSTEM_IMPL_PROPOSAL.md` — ratified implementation defaults.

Keep working notes in `.scratch/seed-system/` in whatever form serves the conversation; they carry
no schema and never become canonical by sitting there. Deferred items, open questions, and
rejections may be materialized as one free-form `docs/SEED_SYSTEM_NOTES.md` when the user wants
the record.

New `ACCEPTANCE.md` output must not coexist with active `SYSTEM_DOMAIN.md` or `SYSTEM_USECASE.md`
(mixed-mode, script-enforced). Route legacy System documents through human review as working
evidence; do not auto-convert them.

## Conversation

During divergence, accumulate raw system-flow evidence from the conversation and from parked
SF items — confirm, refine, or reject a parked item before it shapes canonical Acceptance. Record
fragments in scratch with Evidence lines and `[Term]`/`{term}` marking (example in artifacts.md).
Ask scenario questions, not checklist labels, drawn from the weak slots:

- Which user-visible state changes?
- What external boundary reads or writes?
- What happens on failure, retry, duplicate delivery, or partial completion?
- What reverse or cancellation path exists?
- What conflict can happen and who wins?
- What command is allowed, blocked, or deferred in v1?
- Which seam can observe the result without private implementation knowledge?
- Which inherited Essential outcome has no Acceptance coverage yet?

Example question:

```text
발주확인을 채널에 올리다 네트워크가 끊기면 같은 요청이 다시 갈 수 있어.
이 흐름에서는 두 번째 요청이 어떻게 보여야 해?
```

Enter convergence when the user signals completion, two turns add no new material, or every
inherited Essential outcome has a plausible scenario and seam. A false positive is fine; the
closing check can send you back to divergence.

Closing check — judge these before staging the batch:

- Coverage: does each inherited Essential outcome have at least one AC naming it in Evidence?
- Testability: can every `Then` be observed at its declared seam?
- Atomicity: does each scenario test one behavior at one seam?
- Failure paths: are relevant failure, retry, reverse, duplicate, and conflict flows included?
- v1 boundary: did deferred material leak into v1 Acceptance?
- Essential gap: does any scenario need product intent that Essential does not provide?

Ratify in two stages. Stage A, the criteria:

```text
완성도를 판정하기 위한 Acceptance 기준은 이 목록이면 충분해?
```

Stage B, the full staged body in one batch, grouped by `Basis` — for `inherited`, confirm the
mapping to ratified Essential content and the seam; for `proposed`, ratify the content:

```text
이 Acceptance 몸체로 v1 계약을 확정할까? 바꿀 항목만 짚어줘.
```

Apply partial edits to affected scenarios only, then re-present the batch.

After ratification, propose implementation defaults by area — storage, external ports,
synchronization, stack and test harness, deployment — one default each with the AC IDs it serves;
the user marks only changes.

Then prepare `SEED_SYSTEM_TESTS.md` records and hand off to `$seed-tdd` with the AC IDs, contract
hashes, seams, expected assertions, and per-scenario Risk/Layer. Record
`gap — test harness not created yet` where no test exists; `$seed-tdd` proves RED/GREEN one slice
at a time. At the end of a standalone run, present next-step categories only (`$seed-tdd`, PRD,
tickets, prototype); do not start one unless the user asks. Under an active seed-loop, return the
ratified handoff and verification result to the loop; the initial loop request already authorizes
the next owner transition but never substitutes for content ratification.

## Verification

Run `scripts/check-acceptance.py --docs <project-docs>` before presenting materialized output, and
again after any edit to a materialized `ACCEPTANCE.md`. The script is the sole owner of the
contract-hash computation and the structural gates (fields, hash-marker linkage, coverage naming,
mixed-mode); semantics stay a human/agent duty. Completion — every v1 AC current-hash GREEN under
`--complete` — is normally reached inside `$seed-tdd`, not here.

## First turn

Do not explain the document structure first. Load the input package silently, then say:

```text
Essential 몸체는 받았어. 어느 흐름부터 구현 판정 가능한 Acceptance로 잡아볼까?
떠오르는 대로 말해줘. seam과 테스트 가능성은 내가 정리할게.
```

If the package is missing, ask for its location. If the user confirms that none exists, say that
seed-body must run first and stop this workflow.

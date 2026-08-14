---
name: seed-system
description: seed-body가 남긴 동결 Essential 언어와 파킹된 System 발화를 입력으로, 코드 없는 출발점에서 사용자와 문답해 비준된 ACCEPTANCE.md, Acceptance 테스트 연결 계획, 구현 기본안(SEED_SYSTEM_IMPL_PROPOSAL)을 만드는 상류 설계 스킬. 코드는 쓰지 않으며 사용자가 /seed-system으로 직접 호출할 때만 실행한다.
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

Treat `ACCEPTANCE.md` as the human contract. Treat executable Acceptance tests as the mechanical
constraint on implementation. Do not treat a GREEN test as evidence that the human intended the
behavior; ratification is still the truth-maker.

This skill does not write production code and does not author tests. It prepares the contract,
the agreed public seams, and the test-link records that a later `$seed-tdd` workflow consumes.
`$seed-tdd` adapts TDD to this handoff protocol; it is not a runtime dependency of this skill.

Read `DESIGN.md` before changing these rules.

## Reference routing

- Load and classify seed-body inputs: read `references/conversation-loop.md`.
- Create or update working/canonical artifacts: read `references/artifacts.md`.
- Enter convergence, batch ratification, implementation proposal, or completion audit: read
  `references/closing-gate.md`.

## Operating rules

- Keep `ESSENTIAL_DOMAIN.md` read-only. Inherit its language; do not reopen or rewrite it here.
- Treat `ESSENTIAL_USECASE.md`, when present, as input coverage material only. Do not publish it as
  a parallel canonical contract.
- Treat `SEED_BODY_SYSTEM_PARKING.md` as seed evidence. Confirm, refine, or reject it before it
  shapes canonical Acceptance.
- Keep System vocabulary, state transitions, ports, retries, idempotency, conflict rules, commands,
  and implementation hints in working evidence or `SEED_SYSTEM_IMPL_PROPOSAL.md`; do not publish
  `SYSTEM_DOMAIN.md` or `SYSTEM_USECASE.md`.
- Use one atomic `AC-{nnn}` Acceptance scenario per observable domain flow.
- Do not stage an AC that only restates an inherited Essential use case in Given/When/Then form;
  require at least one recorded decision beyond the inherited sentence: a decidable boundary, an
  exclusion, or a system-flow behavior. If no v1-relevant decision remains, a recorded finding that
  only seam selection was needed satisfies this requirement.
- Choose the lowest stable public seam that can observe every `Then`. Do not pin private methods,
  internal call topology, or implementation-only collaborators.
- Ask one question at a time during divergence. During convergence, batch-review the full body.
- Use implementation defaults only after Acceptance is ratified. Propose defaults from the accepted
  scenarios and raw design constraints; let the user mark only what must change.

## Managed files

Use these canonical files in the target project's `docs/`:

- `ESSENTIAL_DOMAIN.md` — frozen inherited language from seed-body.
- `ACCEPTANCE.md` — human-ratified v1 business scenarios.

Use these seed-system working files:

- `.scratch/seed-system/SEED_SYSTEM_FLOWS.md`
- `.scratch/seed-system/SEED_SYSTEM_PRIOR.md`
- `.scratch/seed-system/SEED_SYSTEM_HARVEST.md`
- `.scratch/seed-system/SEED_SYSTEM_CANDIDATES.md`
- `.scratch/seed-system/SEED_SYSTEM_IMPL_PROPOSAL.md`
- `.scratch/seed-system/SEED_SYSTEM_TESTS.md`
- `.scratch/seed-system/SEED_SYSTEM_LATER.md`
- `.scratch/seed-system/SEED_SYSTEM_QUESTIONS.md`
- `.scratch/seed-system/SEED_SYSTEM_CRITERIA.md`
- `.scratch/seed-system/SEED_SYSTEM_REJECTED.md`

On completion, materialize `ACCEPTANCE.md`, `SEED_SYSTEM_IMPL_PROPOSAL.md`,
`SEED_SYSTEM_TESTS.md`, `SEED_SYSTEM_LATER.md`, `SEED_SYSTEM_QUESTIONS.md`, and
`SEED_SYSTEM_CRITERIA.md` under `docs/`. Never materialize `SYSTEM_DOMAIN.md` or
`SYSTEM_USECASE.md`.

Reject a workspace as mixed-mode if new `ACCEPTANCE.md` output would coexist with active
`SYSTEM_DOMAIN.md` or `SYSTEM_USECASE.md`. Route legacy System documents through human review as
working evidence; do not auto-convert them.

## Acceptance contract

`ACCEPTANCE.md` records one atomic scenario per observable domain flow: a stable unique `AC-{nnn}`
ID, `Basis` (`inherited` when every clause traces to ratified Essential content, `proposed` when
any clause adds system-designed behavior — when unsure, `proposed`), one observable `Seam` without
internal call topology, decidable Given/When/Then in inherited Essential language, and user
utterance or ratification Evidence. Include failure, reverse, retry, and conflict scenarios when
they are v1-relevant.

Each scenario carries a contract hash over its behavioral fields only (ID, Subject, Seam, Given,
When, Then); Basis and Evidence stay outside the hash so provenance edits never stale a test. A
semantic edit invalidates affected test records until the test is relinked under the current hash.
The scenario format, canonical hash computation, and invalidation records are owned by
`references/artifacts.md` — read it when staging or editing scenarios.

## Test lifecycle

`SEED_SYSTEM_TESTS.md` records the test command, test directory, and one record per Acceptance ID:
`red` (linked test fails for the not-yet-implemented behavior), `green` (linked test passes), or
`gap — <concrete reason>`. Red and green require a test path and an
`@acceptance: AC-{nnn} sha256:<hash>` marker. Record formats, including each record's worst-failure
`Risk` and narrowest verification `Layer`, are owned by `references/artifacts.md`.

Implementation handoff needs RED evidence regardless of Basis; a gap is honest but not verified.
Missing behavior uses an observed working-tree RED. Behavior already present before its AC slice may
use `$seed-tdd`'s isolated sensitivity RED before recording `PREEXISTING_GREEN`. Completion requires
every v1 Acceptance linked with the current hash and GREEN. Verify structure, hash-marker linkage,
and coverage mechanically with `scripts/check-acceptance.py`; it does not judge semantics, so
semantic review stays a human/agent duty.

Do not implement a TDD engine here. Hand the Acceptance IDs, hashes, seams, expected assertions, and
per-scenario Risk/Layer to `$seed-tdd`, which links the tests and proves RED/GREEN one slice at a
time.

## Workflow

1. Load the seed-body package silently. If no package exists, ask once for its path and stop. If the
   user confirms that none exists, route them to seed-body; do not start from conversation-only
   evidence. If only optional package files are missing, continue under the input rules in
   `references/artifacts.md`.
2. Accumulate raw system-flow evidence from parked SF items and the conversation. Split mixed
   utterances into Essential gaps, system-flow constraints, and implementation hints.
3. Rotate through weak slots: state transitions, external boundaries, synchronization, idempotency,
   retries, failures, reverse flows, conflict rules, commands, and v1/LATER boundaries.
4. Enter the closing gate when the user signals completion, the conversation stalls, or the working
   body can cover every inherited Essential use case.
5. Rewrite raw flows into testable Acceptance scenarios. Choose and record seams before test
   authoring. Batch-review the complete `ACCEPTANCE.md`.
6. After Acceptance is ratified, propose implementation defaults by area: storage, external ports,
   sync/mirroring, stack, deployment, test harness. Ask the user to mark only changes.
7. Prepare `SEED_SYSTEM_TESTS.md` records. If tests are not authored yet, record concrete gaps or
   return a `$seed-tdd` handoff with the scenario IDs, hashes, seams, and intended assertions.
8. Materialize the accepted documents and route the next step. Do not start PRD, ticketing, TDD,
   prototype, or implementation unless the user asks.

## First turn

Do not explain the document structure first. Load the input package, then say:

```text
Essential 몸체는 받았어. 어느 흐름부터 구현 판정 가능한 Acceptance로 잡아볼까?
떠오르는 대로 말해줘. seam과 테스트 가능성은 내가 정리할게.
```

If the package is missing, ask for its location. If the user confirms that none exists, say that
seed-body must run first and stop this workflow.

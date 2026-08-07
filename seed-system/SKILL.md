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
the agreed public seams, and the test-link records that a later `$tdd` workflow can use. `$tdd` is
a handoff method for test authoring, not a runtime dependency of this skill.

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

Record one scenario per `## [Subject]`:

```md
## [중복 없이 발주확인 반영]

ID:
AC-001

Basis:
proposed

Seam:
- 발주확인 채널 접점

Given:
- 반영되지 않은 [발주확인]이 있다.

When:
- 전송 도중 연결이 끊겨 같은 요청이 다시 전달된다.

Then:
- [발주확인]은 한 번만 반영된다.

Evidence:
- T12 (비준) "다시 보내도 두 번 잡히면 안 돼"
```

Require:

- a stable unique `AC-{nnn}` ID;
- `Basis: inherited` when every clause traces to ratified Essential content, `Basis: proposed`
  when any clause adds system-designed behavior — when unsure, use `proposed`;
- one observable `Seam` stated without internal call topology;
- concrete Given/When/Then clauses in inherited Essential language;
- user utterance or ratification Evidence;
- success, failure, reverse, retry, and conflict scenarios when they are v1-relevant.

The contract hash covers ID, Subject, Seam, Given, When, and Then. Exclude Basis and Evidence so
provenance edits do not stale the test. After any semantic contract edit, change every affected
`red` or `green` record to `gap — contract changed; test relink required`. Preserve the previous
test path and marker in Notes for audit, but do not keep the stale marker as the active Marker.

## Test lifecycle

Use `SEED_SYSTEM_TESTS.md` to record the declared test command, test directory, and one record per
Acceptance ID:

- `red` — a linked executable test exists and fails for the missing, not-yet-implemented behavior;
- `green` — the linked executable test passes;
- `gap — <concrete reason>` — no runnable or faithful test exists yet.

For `red` and `green`, require a test path and marker:

```text
@acceptance: AC-001 sha256:<canonical-contract-hash>
```

Normal implementation handoff needs RED regardless of Basis. A gap is honest but not verified.
Completion requires every v1 Acceptance to be linked with the current hash and GREEN.

Do not implement a second TDD engine here. When the user moves from design to test authoring, hand
the Acceptance IDs, hashes, seams, and expected assertions to `$tdd`. `$tdd` writes the tests and
proves RED/GREEN.

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
   return a `$tdd` handoff with the scenario IDs, hashes, seams, and intended assertions.
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

## Forbidden patterns

- Do not modify frozen Essential files.
- Do not publish `SYSTEM_DOMAIN.md` or `SYSTEM_USECASE.md` as new canonical output.
- Do not auto-promote parked SF items, legacy System prose, or GREEN tests into desired behavior.
- Do not stage an AC that only restates an inherited Essential use case in Given/When/Then form;
  require at least one recorded decision beyond the inherited sentence: a decidable boundary, an
  exclusion, or a system-flow behavior. If no v1-relevant decision remains, a recorded finding that
  only seam selection was needed satisfies this requirement.
- Do not place framework, schema, queue, route, polling interval, or selector choices in
  `ACCEPTANCE.md` unless they are user-visible business facts.
- Do not ask the user to design every technical detail. Propose implementation defaults after the
  Acceptance body is closed.
- Do not claim completion from natural-language review alone. Completion requires current linked
  tests to be GREEN, or an explicit non-completion handoff/gap.

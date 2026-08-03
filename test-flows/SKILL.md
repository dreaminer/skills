---
name: test-flows
description: Curate permanent project tests that expose code-observed actor-to-outcome domain flows and invariants, then prove each selected scenario catches a plausible regression. Use when a human wants executable domain-flow evidence, stronger process tests, or characterization coverage; do not create a project-understanding document.
---

# Test Flows

Build an **executable domain story** as permanent tests in the target project's established test
roots.

A selected test is evidence only when it has both forms of fitness:

- **Story fitness:** a reader can see domain facts, one actor action or automatic trigger, and the resulting domain outcome.
- **Regression fitness:** a plausible defect in the behavior makes the test fail for a relevant assertion.

Tests record code-observed behavior, including existing quirks. They can support later domain
interpretation; they do not prove business intent. This skill owns the permanent test evidence and
its regenerable verification receipt. Do not create `QUICK_UNDERSTANDING.md` or another
project-flow document.

Before writing the receipt, read `references/result-contract.md`. The tests remain the authority for
observed behavior; `TEST_FLOWS_RESULT.md` only records that Test Flows qualified and executed them.

## 1. Resolve locations and let the human choose the test stack

Inspect only enough to identify the project root, language, runtime, installed dependencies, test configuration, normal build/test commands, existing test locations, and public boundaries capable of exercising domain behavior.

Resolve both outputs explicitly:

- use an established test root inside the target project; if none exists, propose a conventional
  project-owned test root for each stack option;
- use `<target-project>/docs/TEST_FLOWS_RESULT.md` for the verification receipt unless the human
  names another documentation directory inside that project.

Present 2–4 compatible choices, including the installed stack when viable:

| Stack | Repository fit | Domain-flow support | Required change | Main trade-off |
|---|---|---|---|---|
| `<framework and companions>` | `<observed fit>` | `<process, rules, async, persistence>` | `<dependencies/config>` | `<gain and cost>` |

Recommend one using repository evidence. When no stack was named, output
`WAITING_FOR_TEST_STACK`, the resolved test location, the table, and one direct selection question.
Make no dependency or configuration change before selection.

Pause here only when selection is still missing. When the human already named a compatible stack, show the alternatives for transparency, state the selected stack, and continue immediately. After selection, continue through all remaining steps without another routine approval gate. Pause only for a production behavior change, a material scope expansion, or an external blocker.

This step is complete when the human has selected a compatible stack and both output paths are
inside the target project.

## 2. Establish the observed baseline and trace the domain story

Run the repository's normal relevant test command before editing when one exists, and record pre-existing failures or the absence of a baseline command. Inventory every in-scope public entry point. Trace domain-bearing entry points through the collaborators that decide outcomes, state and persistence transitions, outgoing effects, and the existing tests that reach them; classify purely technical or supporting entry points without expanding them into domain scenarios.

Map each actor goal or initiating trigger as:

`starting domain facts → action or trigger → decisions and invariants → state/effects → actor-visible outcome`

Find the narrow points where a stable public boundary exposes the result of a wide flow. Use those **pinch points** for process evidence. Use the narrowest stable rule seam for a domain invariant. Treat hard-wired infrastructure as a seam problem; substitute only at an enabling point the test can control.

Classify existing tests internally:

- **Process evidence:** crosses real orchestration from domain starting facts to a final observable outcome.
- **Invariant evidence:** distinguishes the meaningful alternatives of a domain rule or lifecycle constraint.
- **Technical regression:** protects parsing, serialization, adapters, persistence mapping, transport, performance, or another implementation concern without explaining a domain outcome by itself.

For behavior with no trustworthy specification, characterize what the code actually does. Probe, observe, and pin the result. Record suspicious behavior separately instead of silently converting it into an imagined `should` assertion.

This step is complete when every in-scope entry point belongs to a named process or an evidenced technical/supporting role, and every code-observed decision that changes a domain outcome is visible in the map.

## 3. Design the smallest permanent evidence set

Plan scenarios around behavior, not source methods or coverage percentage. Include:

- the main successful journey from trigger to completed outcome;
- every domain decision that changes that outcome;
- meaningful rejection, terminal, retry, or recovery outcomes present in code;
- durable or outgoing effects required to complete the process;
- high-risk intersections where independent rules interact.

Build an internal plan:

| Process or invariant | Existing evidence | Defect hypothesis | Stable seam | Action |
|---|---|---|---|---|
| `<behavior>` | `<test or none>` | `<plausible regression>` | `<boundary>` | `reuse / strengthen / add / propose` |

Choose the action as follows:

- **Reuse** when the existing test has story fitness and its relevant assertions would catch the defect hypothesis.
- **Strengthen** when an existing scenario reaches the behavior but misses a domain result or effect.
- **Add** when no test kills a distinct, domain-relevant defect at the appropriate seam.
- **Propose** when production code lacks the behavior, so no passing test can establish it.

Before strengthening or adding, state one concrete defect hypothesis: the decision, boundary, transition, recipient, ordering, error, or effect that could be wrong; the observation that would change; and why existing assertions would miss it. Combine scenarios when one focused test kills the same defect; separate them when their failure meanings differ.

Preserve the full existing suite. Add evidence to domain-owned test files and directories that the
project would keep independently. Do not create a `test-flows` test directory or replace unrelated
tests.

This step is complete when every mapped process and invariant has a disposition, and every planned change names a distinct defect, a stable seam, a project-owned location, and the normal command that discovers it.

## 4. Write tests with story fitness

Follow the selected framework and repository conventions. Reuse established fixtures when they express the right facts; introduce helpers only when their names preserve domain meaning.

For a process scenario:

- name the actor goal and final domain outcome;
- make Given, When, and Then visually separable using the framework's idiom;
- enter through the widest stable, deterministic product boundary;
- execute real orchestration and domain decisions;
- replace clocks, randomness, networks, external stores, and third parties only at environmental seams;
- assert the final result together with every state, persistence, event, message, or absence of duplicate effect that is part of that scenario's contract.

For an invariant scenario:

- state the rule and outcome in the title;
- exercise the narrowest stable seam that owns the rule;
- cover each code-observed alternative that changes the outcome;
- use a decision table or parameterized cases when it makes the rule clearer;
- assert exact allowed, rejected, and terminal results.

Use realistic, non-degenerate facts. Prefer concrete values and domain outcomes over existence-only assertions. Keep causes next to their effects and keep assertion logic simple. Mocking an internal collaborator weakens process evidence; use real internal collaborators unless isolation is required to control an environmental boundary.

Run affected tests while writing. Change production code only after separate human authorization; a mismatch between plausible intent and observed behavior is a finding, not permission to repair it.

This step is complete when every changed test passes in its project-owned location, is found by a
maintained command, and remains useful independently of any generated documentation.

## 5. Prove regression fitness

Perform a **kill review** on every reused, strengthened, or added evidence scenario. Inspect the production decisions reached by the test and consider relevant mutations such as a flipped boundary or boolean, removed guard, wrong return, skipped transition, swallowed error, wrong recipient, reordered effect, or duplicated/omitted side effect.

For each scenario:

1. name the smallest plausible mutation representing its defect hypothesis;
2. trace which assertion changes and classify the mutation as `killed`, `survived`, `not covered`, or `equivalent`;
3. strengthen or replace evidence for every high-risk `survived` or `not covered` mutation;
4. avoid multiplying tests when one scenario kills several mutations with the same domain meaning.

For every selected evidence scenario, obtain a **red proof**: use an already-configured mutation tool, or apply one reversible mutation in an isolated scratch copy and confirm the intended test fails while the unmodified code passes. One mutation may prove several scenarios only when each fails through a relevant assertion. Keep the user's working tree untouched. A reasoned mutation review may guide test design but does not replace red proof; report `EFFECTIVENESS_UNVERIFIED` and do not claim that scenario as completed evidence when execution is impossible.

Passing alone is insufficient: an empty implementation, unchanged input echo, removed key decision, or omitted contract effect must not leave the selected evidence green.

This step is complete when each selected scenario has a defect hypothesis, kill classification, and executable red proof, and no high-risk survived mutation is hidden.

## 6. Close the flow

Audit the process map against production code and passing evidence. Every meaningful intermediate state and durable effect must reach one of:

- a tested continuation;
- a tested terminal outcome;
- a reported candidate continuation absent from production code.

An implemented but unprotected continuation returns to steps 3–5 for permanent evidence. An absent continuation becomes a proposal only when concrete evidence leaves the process open: a stranded nonterminal state, an invariant unable to complete, an explicit requirement or TODO, or a contrasting implemented path with the same obligation.

Do not turn an absent continuation into a passing characterization test. Report each proposal in
the final handoff as:

`**<candidate>** — Evidence: <open edge> | Proposal: [G] <facts> → [W] <missing trigger> → [T] <expected outcome> | Confidence: <high/medium/low> | Human decision: <question>`

This step is complete when every process state, effect, and domain-changing alternative is closed by passing evidence, an evidenced terminal outcome, or a visible proposal.

## 7. Verify and hand off

Run the selected evidence tests, the repository's normal full test command for the resolved project
or package, and any normal build, typecheck, or lint command affected by the changes. Compare with
the baseline and separate pre-existing failures from introduced failures.

Use commands maintained by the target project and execute them through its required runtime or
package manager. Do not replace a repository-mandated command with a generic equivalent.

Maintain an internal trace while working:

| Evidence scenario | Kind | Domain result | Defect killed | Proof | Action |
|---|---|---|---|---|---|
| `<test>` | `process/invariant` | `<result>` | `<mutation>` | `executed` | `reused/strengthened/added` |

After final verification, create or replace the resolved `TEST_FLOWS_RESULT.md` using
`references/result-contract.md`:

- write `FLOW_TESTS_READY` only when every listed evidence scenario has story fitness, executable
  red proof, passing final verification, and no in-scope flow-gap proposal;
- otherwise write `FLOW_TESTS_NOT_READY` with the blocking reason and command result;
- list only project-relative evidence-test paths and maintained test commands under
  `Final test verification`;
- summarize command outcomes instead of copying full console logs.

Hand off only:

- the result path and status;
- the selected stack and resolved test root;
- domain processes and invariants represented;
- reused, strengthened, and added test files;
- each selected evidence scenario's defect hypothesis and red-proof result;
- commands run and baseline-versus-final result;
- flow-gap proposals, or `Flow-gap proposals: none`.

When existing evidence is sufficient, report `New tests: none — existing project tests already provide effective domain evidence` instead of manufacturing tests.

The skill is complete only when its permanent evidence set and result receipt are inside the target
project, the receipt says `FLOW_TESTS_READY`, the existing suite remains intact, every changed test
is discovered by normal project commands, every selected scenario passes both story and regression
fitness, and every verification failure or open flow is explicitly accounted for. A
`FLOW_TESTS_NOT_READY` receipt is a truthful terminal handoff, not successful completion.

Return exactly one terminal status matching the receipt: `FLOW_TESTS_READY` or
`FLOW_TESTS_NOT_READY`.

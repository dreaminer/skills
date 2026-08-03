# Seed System Conversation Loop

Use this reference during divergence.

## First turn

Silently load the seed-body package:

1. `ESSENTIAL_DOMAIN.md` -> inherited language.
2. `ESSENTIAL_USECASE.md`, if present -> coverage input only.
3. `SEED_BODY_SYSTEM_PARKING.md` -> seed raw system-flow evidence.
4. `SEED_BODY_LATER.md`, `SEED_BODY_QUESTIONS.md`, and `SEED_BODY_CRITERIA.md` -> context.

If the package cannot be found, ask once for its path. If the user confirms that no seed-body
package exists, stop and route them to seed-body. Do not start seed-system from conversation-only
evidence. Treat missing optional context files as partial input and continue when the minimum input
contract in `artifacts.md` is satisfied.

Do not start by explaining layers or document formats. Invite the first flow.

## Turn handling

1. Reflect the new fragment as a concrete flow:

   ```text
   [actor/component] + [trigger/context] -> [observable result/state change]
   ```

2. Split the fragment into:

   - inherited Essential intent: reference only;
   - system-flow constraint: state, external boundary, synchronization, retry, idempotency, conflict,
     command, error, reverse flow;
   - implementation hint: stack, schema, library, deployment, selector, timeout, interval, credential.

3. Add system-flow constraints to `SEED_SYSTEM_FLOWS.md` with Evidence.
4. Put implementation hints in the proposal work area for later. Do not decide them during
   Acceptance divergence unless the user makes them product requirements.
5. If new Essential intent appears, record a `back-to-Essential` question. Do not resolve it here.
6. If a fragment looks v1-out, ask once whether to park it in `SEED_SYSTEM_LATER.md`.
7. Ask one next question for the most valuable weak slot.

## Weak slots

Rotate through weak slots breadth-first. Do not ask the same slot twice in a row unless it is the
last blocker.

- Which user-visible state changes?
- What external boundary reads or writes?
- What happens on failure, retry, duplicate delivery, or partial completion?
- What reverse or cancellation path exists?
- What conflict can happen and who wins?
- What command is allowed, blocked, or deferred in v1?
- Which seam can observe the result without private implementation knowledge?
- Which inherited Essential outcome has no Acceptance coverage yet?

Ask as scenarios, not checklist labels. Example:

```text
발주확인을 채널에 올리다 네트워크가 끊기면 같은 요청이 다시 갈 수 있어.
이 흐름에서는 두 번째 요청이 어떻게 보여야 해?
```

## Category prior

Once the system category is recognizable, create `SEED_SYSTEM_PRIOR.md` as question material. For a
multi-channel integration, typical prior items include idempotency, retries, rate limits, webhook
versus polling, token expiry, partial failure, ordering, conflict resolution, and audit logs.

Priors are not evidence and do not become canonical. Each item must be disposed as:

- answered -> raw flow;
- not applicable -> user-confirmed;
- deferred -> question;
- v1-out -> later.

## Three-way question handling

For each weak slot:

- if the answer is strongly implied, create an `[assumption]` candidate and ask for confirmation;
- if the user can likely answer, ask one direct scenario question;
- if the user cannot answer now, record a concrete question and rotate.

Off-topic answers may still be useful. Save them as later/context, then return to the highest-value
weak slot.

## Vocabulary

Use inherited Essential terms as `[Term]`. Mark unratified system terms as `{term}` in raw flows.
Harvest only when entering the closing gate. Do not create a canonical System Domain; use harvested
terms to make Acceptance scenarios readable and to inform `SEED_SYSTEM_IMPL_PROPOSAL.md`.

## Closing-gate triggers

Enter `closing-gate.md` when any trigger fires:

- the user explicitly says the flows are enough or asks for the next step;
- two turns add no new material;
- every inherited Essential outcome has at least one plausible Acceptance scenario and seam;
- remaining questions are implementation defaults rather than domain outcomes.

False positives are acceptable. The closing gate can expose gaps and return to divergence.

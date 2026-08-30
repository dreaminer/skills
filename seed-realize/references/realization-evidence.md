# Realization Evidence

Realization evidence answers one question: does the selected ratified `Default` exist and work at
the boundary it promises?

## Evidence pair

A `verified` record needs both:

1. at least one existing project-relative artifact path;
2. one command actually run in this invocation, recorded with its observed exit result.

Allowed path kinds are `artifact`, `code`, `config`, `integration`, `migration`, and `deployment`.
Prefer the kind that identifies what the path proves.

```md
Evidence:
- migration: implementation/drizzle/0001_outbox.sql
- integration: implementation/tests/outbox-restart.integration.test.ts
- command: bun test implementation/tests/outbox-restart.integration.test.ts (exit 0)
```

## Match proof to the Default

- Storage choice: exercise the real driver, schema/migration, and restart or transaction behavior
  promised by the Default. An in-memory substitute is not evidence.
- External port: exercise the actual adapter or a protocol-faithful local boundary. A domain fake
  proves behavior isolation, not adapter realization.
- Outbox or scheduler: demonstrate enqueue/claim/retry/restart properties that distinguish it from
  a direct in-process call.
- HTTP/runtime boundary: boot the selected runtime and exercise its public route or generated
  contract through maintained integration evidence.
- Deployment: repository manifests and dry runs prove deployability only. Mark live deployment
  verified only when the authorized environment exposes evidence of the live operation.

## Insufficient evidence

Do not verify from any of these alone:

- package dependency declarations;
- an implementation proposal or architecture note;
- mocks standing in for the selected external technology;
- a passing AC suite whose seam does not traverse the selected capability;
- a command copied from prior output but not run now;
- unrelated repository-wide GREEN.

When available evidence proves a narrower statement than the Default, either add the missing
observation or route the Default to `seed-system` for an explicit change or deferral.

# Promotion Contract

Use promotion only after the selected approval gate has accepted a prepared preview. Directly
evidenced System candidates may be auto-approved by the Make Body workflow. Essential candidates
require human confirmation. Ambiguous System candidates require maintainer review; if the agent
judges a System candidate ambiguous, it does not call the auto-promotion script. Promotion itself is
a two-step transaction:

1. `prepare-promotion.py <project-root> <docs-dir> <MB-id> <preview-dir>` checks the selected
   candidate, writes all resulting canonical files plus the reduced queue into a new preview
   directory, and checks that staged body.
2. Review or auto-approve that directory according to the candidate Type and evidence boundary. On
   approval, `apply-promotion.py <preview-dir> <project-root> <docs-dir>` copies the staged files
   byte-for-byte into the live documents.

For the common System path, use
`promote-next-system.py <project-root> <docs-dir> <preview-dir>`. It runs the workspace audit,
selects the next ready candidate, refuses an Essential candidate with `NEEDS_HUMAN` (exit 3),
prepares and reviews the preview, then **stops** with `AWAIT_GATE` (exit 0) without
applying. It never applies a System candidate on its own: applying is gated behind the consistency
gate, which is a coordinator (LLM) step and cannot run inside this deterministic script. Exit 0 is
"proceed to the gate", not "applied".

On `AWAIT_GATE`, run the consistency gate (see `consistency-gate.md`) on the candidate. Only on
`READY` does the agent call `apply-promotion.py` on the prepared preview. Any other verdict
(evidence mismatch, unbounded claim, or uncertain check) becomes `NEEDS_HUMAN`: discard the
preview, leave the candidate in `MAKE_BODY_CANDIDATES.md`, and apply nothing. The gate is additive
to — never a replacement for — the deterministic evidence/conflict/duplicate/stale/preview gates.

The preview manifest contains hashes for its source files, cited Evidence files, and staged files.
Apply rejects a modified preview and rejects any changed source document, queue, or Evidence file.
Discard the preview on correction; do not edit it or ask apply to regenerate it.

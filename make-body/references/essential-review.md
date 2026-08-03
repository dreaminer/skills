# Essential batch review

Review the entire hypothesis batch once. Do not ask the human to approve a mechanical translation
for every test.

## Present

For each candidate meaning, show:

- proposed Essential Domain or UseCase text;
- qualified flow-test evidence and the production decision it reaches;
- the implementation concepts removed during abstraction;
- remaining uncertainty;
- any overlapping canonical Essential entry.

Also show:

- technical test flows that produced no Essential candidate;
- competing interpretations recorded as conflicts;
- proposed merges or wording changes to existing canonical entries.

## Human decisions

- **Ratify** — confirms the business meaning. Add a `Human-ratified:` Evidence line and materialize
  the entry after the whole batch decision.
- **Correct** — update the hypothesis, preserve the observed evidence, and present the corrected item
  again.
- **Reject** — record the explicit rejection in `MAKE_BODY_REJECTED.md`; do not create canonical
  content.
- **Undecided** — leave the hypothesis noncanonical with `Status: awaiting-human` or `conflicted`.

## Review tests

Ask of each proposed Essential entry:

1. Does it remain meaningful if the implementation technology changes?
2. Does it add business information rather than merely renaming a test or route?
3. Which part cannot be established by executable behavior alone?
4. Did the human explicitly confirm that interpretation?
5. Does every `[Term]` use the canonical Essential Domain language?

Green tests never answer questions 2–4.

## Apply

Apply ratified Domain entries before UseCases that reference them. Preserve unrelated canonical
bytes. Run `check-workspace.py` after writing. Do not rewrite tests, `TEST_FLOWS_RESULT.md`, the
optional system guide, or legacy System/Acceptance files during this transaction.

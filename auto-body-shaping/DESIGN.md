# auto-body-shaping -- Design Rationale

> Maintainer notes for the automated wrapper around `body-shaping`. This file is not loaded at
> runtime. Keep decisions and rejected alternatives here so the next maintainer does not reopen the
> same design arguments without a real failure.

## North Star

Advance `body-shaping` automatically only when the user explicitly opts in, while preserving the
reader's ability to distinguish human-confirmed domain language from auto-confirmed language.

## Decisions

| Decision | Why |
|---|---|
| Auto confirmation is an explicit opt-in override | The parent skill treats confirmation as a human job. This wrapper is only valid when the user asks for automation and the output is labelled as auto-confirmed. |
| Provenance is inline, not a sidecar | `Confirmation: auto|human` and `Evidence:` live with the canonical item. A separate `BODY_PROVENANCE.md` would drift on rename/delete and violate the parent skill's derive-don't-store principle in the worst place. |
| Missing `Confirmation:` means pre-automation human confirmation | Existing body-shaping documents may already contain confirmed entries. Backfilling every old item adds churn; the convention is explicit and cheap. |
| Provenance metadata avoids `[Term]` notation | The parent checker treats bracketed text as domain references. `Depends on auto:` uses backticks or bare names so provenance does not create dangling or directional reference failures. |
| Validator must directly read `path:line` evidence | A generator paraphrase is not grounding. `PASS` requires direct source rereading; missing or unsupported evidence blocks auto-promotion. |
| `UNKNOWN` routes to the human before adding voting machinery | The parent skill warns against guards for unobserved failures. A second skeptic/vote pass is reserved for a real observed validator-overconfidence failure. |
| Coverage mode is optional and depends on grounding | Repeated Recover can be useful only after direct evidence checks and hard dedup against canonical plus `REJECTED.md`. Without that, it can amplify weak candidates. |
| Auto-on-auto is a known boundary, not a new mechanism yet | Auto-confirmed entries can support later candidates only with an explicit `Depends on auto:` marker. If auto-confirmed content is the only substantive support, route to human. Add more machinery only after a real failure. |
| `path:line` evidence is a verification snapshot | Line numbers are used so the validator can ground a claim at promotion time. They are not promised to remain live pointers after the source changes. |
| Confirmation metadata mandates backticks on variable values; only `auto`/`human`/`none` stay bare | `check-body.sh` strips backtick spans but scans the rest of the line. A bare evidence paraphrase containing a code token like `items[head]` or `messages:{groupId}` is read as a dangling `[ref]` / stray `{candidate}` and fails the checker *after* promotion, halting the auto-loop. Backticking every variable value (paths, terms, paraphrases) makes provenance inert to the checker. The earlier "bare names or backtick spans" wording permitted exactly the footgun. |
| Validator `NEEDS_HUMAN` definition is the single escalation list; `Human Escalation` only routes | The criteria previously lived in three places (inverse of the PASS list, the `NEEDS_HUMAN` prose, and a standalone `Human Escalation` enumeration). Three copies drift (parent principle 3). The validator contract now owns the list; `Human Escalation` points to it and adds only the check-body-fix-alters-meaning case. |
| Any `UNKNOWN` check ⇒ `NEEDS_HUMAN`, never `PASS`, stated explicitly | The mapping was only implicit across the PASS list and escalation prose. `yolo` states it in one line; auto- now matches so the verdict rule is not reconstructed by the reader. |

## Rejected Alternatives

- **Sidecar provenance file.** Rejected because it mirrors canonical entries and will drift when
  terms are renamed, merged, or deleted.
- **Immediate disagreement vote between generator and validator.** Rejected until a real run shows
  validator overconfidence. Keep the first guard simple: any `UNKNOWN` means human.
- **Always-on coverage fixpoint.** Rejected as the default because not every run wants full project
  coverage, and repeated Recover is safe only after grounding and dedup are strong.

## Future Work

- Add an explicit coverage mode that repeats Recover until zero new grounded candidates appear, with
  hard dedup against canonical entries and `REJECTED.md`.
- Add a second-pass skeptic only if actual runs show the validator returning overconfident `PASS`
  verdicts.
- Resolve the Summary counters' semantics before touching them. They are **this-run flow**, not
  cumulative **stock**, so a repo-wide `grep -c '^Confirmation: auto'` is wrong (it counts every
  prior run). `Auto-promoted` / `Human-required` are recoverable as a start-vs-end Δ of
  `Confirmation:` labels; `Validator failures fixed` leaves no trace in the final file state and
  cannot be derived at all. Preferred resolution: drop `Validator failures fixed` (an unauditable
  number is worse than none) and either keep the other two as an explicit run-scoped Δ or drop all
  three — whichever the maintainer decides. Do not implement a `grep -c` stock count.

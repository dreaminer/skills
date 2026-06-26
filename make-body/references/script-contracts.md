# Script Contracts

Every Make Body script is deterministic provenance, never a domain decision. Each one checks,
selects, renders, hashes, collects, or stages — and each carries an explicit "it never …" boundary
so judgment stays with the coordinator (see `DESIGN.md`, "Determinism stays in scripts; judgment
stays in the coordinator"). This file is the per-script reference; `SKILL.md` holds the executable
workflow that invokes them.

- `check-question.sh` — validates one ready candidate against canonical headers and the directional
  table. It does not classify, infer, or approve.
- `check-body.sh` — validates canonical headers, directional references, and leaked `{candidate}`
  notation after Promote. It also requires a Meaning/Evidence pair for each Domain subject and a
  Given/When/Then/Evidence set for each UseCase subject; it does not judge the evidence meaning.
- `check-canonical-evidence.py` — validates that canonical Evidence pointers still name in-scope code
  lines; it never decides whether that code proves the canonical claim.
- `check-code-facts.py` — regenerates the declared fact adapter in a temporary file and reports a
  stale fact index; it never changes the checked index.
- `collect-typescript-facts.py` — deterministically indexes in-scope TypeScript/JavaScript/SQL code;
  it never classifies a fact as Essential or System.
- `collect-python-facts.py` — deterministically indexes Python decorators/calls/effects and SQL code;
  it never classifies a fact as Essential or System.
- `collect-code-facts.py` — combines the supported TypeScript and Python fact adapters without
  classifying their facts.
- `report-fact-coverage.py` — lists in-scope files without fact entries so they receive deliberate
  review; it never concludes that such a file lacks domain meaning.
- `extract-typescript-candidates.py` — turns selected lexical facts into conservative, code-literal
  System candidate scaffolds, skipping any whose `(Type, Subject, Evidence pointer)` matches a record
  in `MAKE_BODY_REJECTED.md`; it never infers Essential meaning or promotes a candidate.
- `extract-python-candidates.py` — turns selected Python lexical facts into the same conservative,
  rejection-suppressed System candidate scaffolds; it never infers Essential meaning or promotes a candidate.
- `extract-code-facts-candidates.py` — turns a combined fact index into the same conservative,
  rejection-suppressed System candidate scaffolds; it never infers Essential meaning or promotes a candidate.
- `show-evidence.py` — prints a bounded, in-scope source window for one Evidence pointer; it never
  interprets the displayed code.
- `trace-system-flows.py` — renders lexical entrypoint-to-handler traces from
  `MAKE_BODY_CODE_FACTS.md`; it prints direct/effect calls and schema context for investigation, but
  never creates candidates, infers Essential meaning, or proves runtime reachability.
- `review-candidate.py` — renders one validated candidate alongside every Evidence context. For an
  Essential candidate it adds a deterministic review frame (fixed checklist plus lexically co-located
  canonical System terms); it never authors per-candidate questions, decides what code cannot
  establish, or approves the candidate. Judgment follows `references/essential-review.md`.
- `review-next-candidate.py` — selects the next ready candidate and renders its Evidence contexts;
  it never approves or changes the candidate.
- `prepare-next-promotion.py` — selects the next ready candidate and creates its promotion preview;
  it never applies the preview or changes the project documents.
- `promote-next-system.py` — audits the workspace, selects the next ready candidate, refuses an
  Essential candidate with `NEEDS_HUMAN` (exit 3), and for a System candidate prepares and reviews
  the byte-stable preview, then stops with `AWAIT_GATE` (exit 0) without applying — the consistency
  gate runs as a coordinator step before `apply-promotion.py`. It never applies. If the agent
  judges a System candidate ambiguous, it does not call this script.
- `review-promotion-preview.py` — verifies a preview is still current and renders its exact diffs;
  it never approves or applies the preview.
- `find-symbol-uses.py` — lists in-scope lexical uses of one identifier for caller/callee review; it
  never proves runtime reachability.
- `check-evidence.py` — validates that a selected candidate cites existing, in-scope source lines;
  it never evaluates the cited claim's semantic support.
- `next-candidate.py` — deterministically selects from already-classified, unblocked candidates;
  it never interprets or approves their meaning.
- `init-docs.py` — creates only missing Make Body files with their required top-level headers; it
  never replaces an existing file.
- `bootstrap-make-body.py` — selects a supported adapter, initializes documents, collects facts,
  seeds only safe System candidates, and audits the result; it verifies forced adapter/source
  compatibility, stages all changes through the workspace audit, and preflights a non-empty queue
  before changing a workspace. It rolls back already-applied managed files after a write failure
  and rejects concurrent bootstrap runs or source changes during staging.
- `report-fact-coverage.py --fail-on-unrepresented` — turns the coverage report into a strict
  mechanical gate; it never decides whether an unrepresented file is domain-relevant.
- `report-status.py` — counts canonical subjects, open/ready/blocked candidates, unresolved
  conflict records, and recorded rejected records; it never interprets them.
- `check-conflicts.py` — validates conflict record fields and existing in-scope Evidence pointers;
  it never resolves the conflict.
- `check-rejected.py` — validates rejected (`MR-{nnn}`) record fields and in-scope Evidence pointers
  in the optional `MAKE_BODY_REJECTED.md`, and flags any queued candidate whose `(Type, Subject,
  Evidence pointer)` matches a rejected record; it never decides a rejection. An absent archive is
  valid.
- `check-candidate-duplicates.py` — rejects only candidates with identical Type, Subject, Content,
  and Evidence pointer sets; it never infers semantic duplication.
- `check-workspace.py` — runs all deterministic fact-index, body, canonical Evidence, conflict,
  rejected, duplicate-candidate, candidate, and status checks without
  making a domain decision. Its strict coverage option requires facts or documented exceptions for
  every in-scope supported source.
- `prepare-promotion.py` — creates an isolated, fully validated preview and records the input and
  preview digests.
- `apply-promotion.py` — records the exact approved preview only when all captured input digests
  still match; it never regenerates the candidate output.
- Future progress scripts may count candidates but must not decide domain meaning.

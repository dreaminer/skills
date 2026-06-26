# Candidate Selection

`next-candidate.py` selects only candidates with an empty `Blocked by` section that pass the existing
structural and Evidence provenance checks. It orders the already assigned Types as System Domain,
System UseCase, Essential Domain, then Essential UseCase; ties use the numeric `MB-` id.

This keeps the code-observed System body ahead of Essential hypotheses. A System UseCase discovered
first should still be blocked on missing System Domain terms; once those terms are canonical, the
UseCase becomes ready.

The script does not classify a candidate, compare business meanings, approve content, or resolve a
conflict. Repair any unblocked candidate that fails validation before selecting a later one.

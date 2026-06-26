# MAKE_BODY_CANDIDATES

## MB-001
Type: essential-usecase
Subject: Submit Member
Content:
Given:
- A [Member] exists.
When:
- Submission is requested.
Then:
- The [Member] is submitted.
Evidence:
- `source/member.ts:2` — member state declaration
Blocked by:
-

## MB-002
Type: essential-domain
Subject: Plan
Content:
- [Plan] has a kind.
Evidence:
- `source/plan.ts:2` — kind field
Blocked by:
-

## MB-003
Type: system-domain
Subject: Membership Row
Content:
- [Membership Row] persists a [Member].
Evidence:
- `source/member.ts:2` — member state declaration
Blocked by:
- [Member]

## MB-004
Type: system-usecase
Subject: Submit Member Handler
Content:
Given:
- [Member] exists.
When:
- The submit member handler reads the membership state.
Then:
- The handler observes the [Member]'s membership state.
Evidence:
- `source/member.ts:2` — member state declaration
Blocked by:
-

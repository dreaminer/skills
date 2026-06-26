#!/usr/bin/env python3
"""Report deterministic Make Body document and queue counts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CANONICAL = (
    "ESSENTIAL_DOMAIN.md",
    "ESSENTIAL_USECASE.md",
    "SYSTEM_DOMAIN.md",
    "SYSTEM_USECASE.md",
)
REQUIRED_WORKING = ("MAKE_BODY_CODE_FACTS.md", "MAKE_BODY_CANDIDATES.md", "MAKE_BODY_CONFLICTS.md")
PATHS = (
    "MAKE_BODY_CODE_FACTS.md",
    "MAKE_BODY_COVERAGE_IGNORE.md",
    "MAKE_BODY_CANDIDATES.md",
    "MAKE_BODY_CONFLICTS.md",
    "MAKE_BODY_REJECTED.md",
)
CANDIDATE = re.compile(r"^## MB-\d{3,}\s*$")
CONFLICT = re.compile(r"^## MC-\d{3,}\s*$")
REJECTED = re.compile(r"^## MR-\d{3,}\s*$")
SUBJECT = re.compile(r"^## \[[^]]+\]\s*$")


def queue_counts(path: Path) -> tuple[int, int]:
    open_count = blocked_count = 0
    blocked = False
    in_candidate = False
    in_blocked = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if CANDIDATE.match(line):
            if in_candidate and blocked:
                blocked_count += 1
            open_count += 1
            in_candidate = True
            blocked = False
            in_blocked = False
            continue
        if not in_candidate:
            continue
        if line.startswith("Blocked by:"):
            in_blocked = True
            inline = line[len("Blocked by:") :].strip()
            if inline and inline != "-":
                blocked = True
            continue
        if in_blocked and line.strip() and line.strip() != "-":
            blocked = True
    if in_candidate and blocked:
        blocked_count += 1
    return open_count, blocked_count


def count_headers(path: Path, pattern: re.Pattern[str]) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if pattern.match(line))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    docs = args.docs_dir.resolve()
    missing = [name for name in (*CANONICAL, *REQUIRED_WORKING) if not (docs / name).is_file()]
    if missing:
        print("missing Make Body files: " + ", ".join(missing), file=sys.stderr)
        return 2

    for name in CANONICAL:
        print(f"{name[:-3]}={count_headers(docs / name, SUBJECT)}")
    open_count, blocked_count = queue_counts(docs / "MAKE_BODY_CANDIDATES.md")
    print(f"CANDIDATES_OPEN={open_count}")
    print(f"CANDIDATES_READY={open_count - blocked_count}")
    print(f"CANDIDATES_BLOCKED={blocked_count}")
    print(f"CONFLICTS_UNRESOLVED={count_headers(docs / 'MAKE_BODY_CONFLICTS.md', CONFLICT)}")
    rejected_path = docs / "MAKE_BODY_REJECTED.md"
    rejected = count_headers(rejected_path, REJECTED) if rejected_path.is_file() else 0
    print(f"REJECTED_RECORDED={rejected}")
    print("PATHS:")
    for name in (*CANONICAL, *PATHS):
        print(f"- {docs / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

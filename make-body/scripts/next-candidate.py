#!/usr/bin/env python3
"""Select the next structurally valid, evidence-backed, unblocked Make Body candidate."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


CANDIDATE = re.compile(r"^## (MB-\d{3,})\s*$")
FIELD = re.compile(r"^(Type|Subject|Blocked by):\s*(.*)$")
TYPE_RANK = {
    "system-domain": 0,
    "system-usecase": 1,
    "essential-domain": 2,
    "essential-usecase": 3,
}


@dataclass
class Candidate:
    identifier: str
    candidate_type: str = ""
    subject: str = ""
    blocked: bool = False
    section: str = ""


def candidates(queue: Path) -> list[Candidate]:
    found: list[Candidate] = []
    current: Candidate | None = None
    for raw in queue.read_text(encoding="utf-8").splitlines():
        match = CANDIDATE.match(raw)
        if match:
            current = Candidate(match.group(1))
            found.append(current)
            continue
        if current is None:
            continue
        match = FIELD.match(raw)
        if match:
            current.section, inline = match.groups()
            if current.section == "Type" and inline.strip():
                current.candidate_type = inline.strip()
            elif current.section == "Subject" and inline.strip():
                current.subject = inline.strip()
            elif current.section == "Blocked by" and inline.strip() and inline.strip() != "-":
                current.blocked = True
            continue
        value = raw.strip()
        if not value:
            continue
        if current.section == "Type" and not current.candidate_type:
            current.candidate_type = value
        elif current.section == "Subject" and not current.subject:
            current.subject = value
        elif current.section == "Blocked by" and value != "-":
            current.blocked = True
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    docs = args.docs_dir.resolve()
    queue = docs / "MAKE_BODY_CANDIDATES.md"
    if not queue.is_file():
        parser.error(f"missing candidate queue: {queue}")
    queued = candidates(queue)
    identifiers = [candidate.identifier for candidate in queued]
    duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    if duplicates:
        print("DUPLICATE candidate IDs: " + ", ".join(duplicates), file=sys.stderr)
        return 1

    ready = [candidate for candidate in queued if not candidate.blocked]
    evidence_check = Path(__file__).with_name("check-evidence.py")
    failures = []
    for candidate in ready:
        result = subprocess.run(
            [sys.executable, str(evidence_check), str(args.project_root), str(docs), candidate.identifier],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            failures.append(f"{candidate.identifier}: {(result.stdout + result.stderr).strip()}")
    if failures:
        print("UNREADY candidates:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    if not ready:
        print("NO_READY_CANDIDATE")
        return 3

    next_item = min(
        ready,
        key=lambda candidate: (TYPE_RANK.get(candidate.candidate_type, 99), int(candidate.identifier[3:]), candidate.identifier),
    )
    print(f"NEXT {next_item.identifier} {next_item.candidate_type} {next_item.subject}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

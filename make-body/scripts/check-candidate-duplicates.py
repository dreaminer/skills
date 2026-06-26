#!/usr/bin/env python3
"""Find source-equivalent duplicate candidates without deciding semantic similarity."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


CANDIDATE = re.compile(r"^## (MB-\d{3,})\s*$")
FIELD = re.compile(r"^(Type|Subject|Content|Evidence|Blocked by):\s*(.*)$")


def normalize(lines: list[str]) -> str:
    return " ".join(" ".join(line.split()) for line in lines if line.strip())


def candidates(queue: Path) -> list[tuple[str, tuple[str, str, str, tuple[str, ...]]]]:
    found = []
    identifier = ""
    section = ""
    fields: dict[str, list[str]] = {}

    def finish() -> None:
        if identifier:
            evidence = tuple(sorted(line.split(" — ", 1)[0] for line in fields.get("Evidence", []) if line.strip()))
            found.append((identifier, (normalize(fields.get("Type", [])), normalize(fields.get("Subject", [])), normalize(fields.get("Content", [])), evidence)))

    for raw in queue.read_text(encoding="utf-8").splitlines():
        match = CANDIDATE.match(raw)
        if match:
            finish(); identifier = match.group(1); section = ""; fields = {}
            continue
        if not identifier: continue
        match = FIELD.match(raw)
        if match:
            section, inline = match.groups(); fields.setdefault(section, [])
            if inline.strip(): fields[section].append(inline)
        elif section:
            fields.setdefault(section, []).append(raw)
    finish()
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    queue = args.docs_dir.resolve() / "MAKE_BODY_CANDIDATES.md"
    if not queue.is_file(): parser.error(f"missing candidate queue: {queue}")
    groups: dict[tuple[str, str, str, tuple[str, ...]], list[str]] = defaultdict(list)
    for identifier, signature in candidates(queue): groups[signature].append(identifier)
    duplicates = [identifiers for identifiers in groups.values() if len(identifiers) > 1]
    for identifiers in sorted(duplicates): print("DUPLICATE source-equivalent candidates: " + ", ".join(identifiers))
    if duplicates:
        print(f"FAIL -- {len(duplicates)} duplicate candidate group(s).")
        return 1
    print("OK -- no source-equivalent candidate duplicates.")
    return 0


if __name__ == "__main__": raise SystemExit(main())

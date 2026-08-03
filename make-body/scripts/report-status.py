#!/usr/bin/env python3
"""Report R6 Make Body counts without deciding meaning."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CANONICAL = re.compile(r"^## \[[^]]+\]$")
RECORD = re.compile(r"^## \S")
STATUS = re.compile(r"^- (awaiting-human|ratified|rejected|conflicted)$")


def count(path: Path, pattern: re.Pattern[str]) -> int:
    if not path.is_file():
        return 0
    return sum(bool(pattern.match(line)) for line in path.read_text(encoding="utf-8").splitlines())


def hypothesis_statuses(path: Path) -> dict[str, int]:
    result = {name: 0 for name in ("awaiting-human", "ratified", "rejected", "conflicted")}
    if not path.is_file():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        match = STATUS.match(line)
        if match:
            result[match.group(1)] += 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    docs = args.docs_dir.resolve()
    statuses = hypothesis_statuses(docs / "MAKE_BODY_ESSENTIAL_HYPOTHESES.md")

    print(f"ESSENTIAL_DOMAIN={count(docs / 'ESSENTIAL_DOMAIN.md', CANONICAL)}")
    print(f"ESSENTIAL_USECASE={count(docs / 'ESSENTIAL_USECASE.md', CANONICAL)}")
    for name, value in statuses.items():
        print(f"HYPOTHESES_{name.upper().replace('-', '_')}={value}")
    print(f"CONFLICTS={count(docs / 'MAKE_BODY_CONFLICTS.md', RECORD)}")
    print(f"REJECTED={count(docs / 'MAKE_BODY_REJECTED.md', RECORD)}")
    for name in (
        "ESSENTIAL_DOMAIN.md",
        "ESSENTIAL_USECASE.md",
        "MAKE_BODY_ESSENTIAL_HYPOTHESES.md",
        "MAKE_BODY_CONFLICTS.md",
        "MAKE_BODY_REJECTED.md",
    ):
        print(f"PATH={docs / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

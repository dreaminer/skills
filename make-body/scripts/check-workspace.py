#!/usr/bin/env python3
"""Audit the small R6 Make Body workspace without inspecting tests."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


HEADER = re.compile(r"^## (\S.+)$")


def nonempty_records(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [match.group(1) for line in path.read_text(encoding="utf-8").splitlines() if (match := HEADER.match(line))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    docs = args.docs_dir.resolve()
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    if not docs.is_dir():
        parser.error(f"docs directory is not a directory: {docs}")

    body = Path(__file__).with_name("check-body.sh")
    result = subprocess.run(["sh", str(body), str(docs)], text=True, capture_output=True)
    if result.returncode:
        print(result.stdout + result.stderr, end="")
        return result.returncode

    expected_titles = {
        "MAKE_BODY_ESSENTIAL_HYPOTHESES.md": "# MAKE_BODY_ESSENTIAL_HYPOTHESES",
        "MAKE_BODY_CONFLICTS.md": "# MAKE_BODY_CONFLICTS",
        "MAKE_BODY_REJECTED.md": "# MAKE_BODY_REJECTED",
    }
    failures = 0
    for name, title in expected_titles.items():
        path = docs / name
        if not path.is_file():
            print(f"MISSING {name}")
            failures += 1
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0] != title:
            print(f"INVALID title for {name}")
            failures += 1

    for name in ("MAKE_BODY_CONFLICTS.md", "MAKE_BODY_REJECTED.md"):
        duplicates = []
        records = nonempty_records(docs / name)
        for record in set(records):
            if records.count(record) > 1:
                duplicates.append(record)
        if duplicates:
            print(f"DUPLICATE records in {name}: {', '.join(sorted(duplicates))}")
            failures += 1

    if failures:
        print(f"FAIL WORKSPACE -- {failures} violation(s).")
        return 1
    print("OK WORKSPACE -- Essential recovery artifacts are structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

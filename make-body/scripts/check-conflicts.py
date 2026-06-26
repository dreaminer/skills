#!/usr/bin/env python3
"""Validate Make Body conflict records and their code Evidence pointers."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

CONFLICT = re.compile(r"^## (MC-\d{3,})\s*$")
FIELD = re.compile(r"^(Subject|Claims|Evidence|Context searched|Why unresolved):\s*(.*)$")
REQUIRED = ("Subject", "Claims", "Evidence", "Context searched", "Why unresolved")
EVIDENCE = re.compile(r"^- `([^`]+):(\d+)` — (.+)$")
SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".sql"}
EXCLUDED_DIRS = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next"}
EXCLUDED_SUFFIXES = (".d.ts", ".min.js")


@dataclass
class Record:
    identifier: str
    fields: dict[str, list[str]] = field(default_factory=lambda: {name: [] for name in REQUIRED})
    section: str = ""


def records(path: Path) -> list[Record]:
    found: list[Record] = []
    current: Record | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = CONFLICT.match(raw)
        if match:
            current = Record(match.group(1))
            found.append(current)
            continue
        if raw.startswith("## "):
            raise ValueError(f"invalid conflict header: {raw}")
        if current is None:
            continue
        match = FIELD.match(raw)
        if match:
            current.section, inline = match.groups()
            if inline.strip():
                current.fields[current.section].append(inline.strip())
            continue
        if current.section and raw.strip():
            current.fields[current.section].append(raw.strip())
    return found


def meaningful(lines: list[str]) -> bool:
    return any(line.strip() and line.strip() != "-" for line in lines)


def in_scope(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.suffix not in SOURCE_EXTENSIONS:
        return False
    return not path.name.endswith(EXCLUDED_SUFFIXES) and ".generated." not in path.name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    conflicts_path = args.docs_dir.resolve() / "MAKE_BODY_CONFLICTS.md"
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    if not conflicts_path.is_file():
        parser.error(f"missing conflict file: {conflicts_path}")
    try:
        found = records(conflicts_path)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2

    failures = 0
    identifiers = [record.identifier for record in found]
    for identifier in sorted({item for item in identifiers if identifiers.count(item) > 1}):
        print(f"DUPLICATE conflict ID: {identifier}")
        failures += 1
    for record in found:
        for name in REQUIRED:
            if not meaningful(record.fields[name]):
                print(f"MISSING {name} for {record.identifier}")
                failures += 1
        for entry in record.fields["Evidence"]:
            match = EVIDENCE.match(entry)
            if not match:
                print(f"INVALID Evidence format for {record.identifier}: {entry}")
                failures += 1
                continue
            raw_path, raw_line, _ = match.groups()
            source = (root / raw_path).resolve()
            line_number = int(raw_line)
            if not in_scope(source, root) or not source.is_file():
                print(f"INVALID Evidence pointer for {record.identifier}: {raw_path}:{raw_line}")
                failures += 1
                continue
            try:
                lines = source.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                print(f"INVALID Evidence pointer for {record.identifier}: {raw_path}:{raw_line}")
                failures += 1
                continue
            if line_number < 1 or line_number > len(lines) or not lines[line_number - 1].strip():
                print(f"INVALID Evidence pointer for {record.identifier}: {raw_path}:{raw_line}")
                failures += 1
    if failures:
        print(f"FAIL -- {failures} conflict violation(s).")
        return 1
    print(f"OK -- {len(found)} conflict record(s) are structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

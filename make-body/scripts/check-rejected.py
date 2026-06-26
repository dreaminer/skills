#!/usr/bin/env python3
"""Validate Make Body rejected records and flag resurrected candidates.

MAKE_BODY_REJECTED.md is an optional archive of candidates a human explicitly
rejected. An absent archive is valid (nothing to validate). This script checks
record structure and Evidence provenance only; it never re-judges a rejection.
It also flags any queued candidate whose (Type, Subject, Evidence pointer)
matches a rejected record, so a rejection is not silently re-queued by hand.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rejected_index import rejected_keys

REJECTED = re.compile(r"^## (MR-\d{3,})\s*$")
FIELD = re.compile(r"^(Type|Subject|Reason|Evidence|Replacement):\s*(.*)$")
REQUIRED = ("Type", "Subject", "Reason", "Evidence")
OPTIONAL = ("Replacement",)
EVIDENCE = re.compile(r"^- `([^`]+):(\d+)` — (.+)$")
CANDIDATE = re.compile(r"^## (MB-\d{3,})\s*$")
CANDIDATE_FIELD = re.compile(r"^(Type|Subject|Content|Evidence|Blocked by):\s*(.*)$")
LOCATION = re.compile(r"^- `([^`]+:\d+)`")
VALID_TYPES = {"essential-domain", "essential-usecase", "system-domain", "system-usecase"}
SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".sql"}
EXCLUDED_DIRS = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next"}
EXCLUDED_SUFFIXES = (".d.ts", ".min.js")


@dataclass
class Record:
    identifier: str
    fields: dict[str, list[str]] = field(default_factory=lambda: {name: [] for name in (*REQUIRED, *OPTIONAL)})
    section: str = ""


def records(path: Path) -> list[Record]:
    found: list[Record] = []
    current: Record | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = REJECTED.match(raw)
        if match:
            current = Record(match.group(1))
            found.append(current)
            continue
        if raw.startswith("## "):
            raise ValueError(f"invalid rejected header: {raw}")
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


def queued_candidates(queue: Path) -> list[tuple[str, str, str, list[str]]]:
    """Return (identifier, type, subject, [locations]) for each queued candidate."""
    found: list[tuple[str, str, str, list[str]]] = []
    identifier = ctype = subject = section = ""
    locations: list[str] = []

    def finish() -> None:
        if identifier:
            found.append((identifier, ctype, subject, locations))

    for raw in queue.read_text(encoding="utf-8").splitlines():
        match = CANDIDATE.match(raw)
        if match:
            finish()
            identifier, ctype, subject, section, locations = match.group(1), "", "", "", []
            continue
        if not identifier:
            continue
        field_match = CANDIDATE_FIELD.match(raw)
        if field_match:
            section, inline = field_match.groups()
            inline = inline.strip()
            if section == "Type" and inline:
                ctype = inline
            elif section == "Subject" and inline:
                subject = inline
            elif section == "Evidence":
                pointer = LOCATION.match(inline)
                if pointer:
                    locations.append(pointer.group(1))
            continue
        body = raw.strip()
        if not body:
            continue
        if section == "Type" and not ctype:
            ctype = body
        elif section == "Subject" and not subject:
            subject = body
        elif section == "Evidence":
            pointer = LOCATION.match(body)
            if pointer:
                locations.append(pointer.group(1))
    finish()
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    docs = args.docs_dir.resolve()
    rejected_path = docs / "MAKE_BODY_REJECTED.md"
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    if not rejected_path.is_file():
        print("OK -- 0 rejected record(s); no archive present.")
        return 0
    try:
        found = records(rejected_path)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2

    failures = 0
    identifiers = [record.identifier for record in found]
    for identifier in sorted({item for item in identifiers if identifiers.count(item) > 1}):
        print(f"DUPLICATE rejected ID: {identifier}")
        failures += 1
    for record in found:
        for name in REQUIRED:
            if not meaningful(record.fields[name]):
                print(f"MISSING {name} for {record.identifier}")
                failures += 1
        type_value = " ".join(record.fields["Type"]).strip()
        if type_value and type_value not in VALID_TYPES:
            print(f"INVALID Type for {record.identifier}: {type_value}")
            failures += 1
        subject_value = " ".join(record.fields["Subject"])
        if any(token in subject_value for token in ("[", "]", "{", "}")):
            print(f"INVALID Subject for {record.identifier}: {subject_value}")
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
                print(f"INVALID Evidence encoding for {record.identifier}: {raw_path}")
                failures += 1
                continue
            if not 1 <= line_number <= len(lines) or not lines[line_number - 1].strip():
                print(f"INVALID Evidence line for {record.identifier}: {raw_path}:{raw_line}")
                failures += 1

    queue = docs / "MAKE_BODY_CANDIDATES.md"
    if queue.is_file():
        rejected = rejected_keys(rejected_path)
        for identifier, ctype, subject, locations in queued_candidates(queue):
            if any((ctype, subject, location) in rejected for location in locations):
                print(f"RESURRECTED {identifier} matches a rejected record: {ctype} {subject}")
                failures += 1

    if failures:
        print(f"FAIL -- {failures} rejected violation(s).")
        return 1
    print(f"OK -- {len(found)} rejected record(s) are structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

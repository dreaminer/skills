#!/usr/bin/env python3
"""Verify that a selected Make Body candidate cites in-scope, non-empty code lines."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".sql"}
EXCLUDED_DIRS = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next", ".venv", "venv", "__pycache__"}
EXCLUDED_SUFFIXES = (".d.ts", ".min.js")
CANDIDATE = re.compile(r"^## (MB-\d{3,})\s*$")
FIELD = re.compile(r"^(Type|Subject|Content|Evidence|Blocked by):")
EVIDENCE = re.compile(r"^- `([^`]+):(\d+)` — (.+)$")


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


def evidence_lines(queue: Path, candidate_id: str) -> list[str]:
    selected = False
    found = False
    section = ""
    result: list[str] = []
    for raw in queue.read_text(encoding="utf-8").splitlines():
        match = CANDIDATE.match(raw)
        if match:
            if selected:
                break
            selected = match.group(1) == candidate_id
            found = found or selected
            section = ""
            continue
        if not selected:
            continue
        if raw.startswith("Evidence:"):
            section = "evidence"
            inline = raw[len("Evidence:") :].strip()
            if inline:
                result.append(inline)
            continue
        if FIELD.match(raw):
            section = ""
            continue
        if section == "evidence" and raw.strip():
            result.append(raw.strip())
    if not found:
        raise ValueError(f"unknown candidate: {candidate_id}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    parser.add_argument("candidate_id")
    args = parser.parse_args()
    root = args.project_root.resolve()
    docs = args.docs_dir.resolve()
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    queue = docs / "MAKE_BODY_CANDIDATES.md"
    if not queue.is_file():
        parser.error(f"missing candidate queue: {queue}")

    check_question = Path(__file__).with_name("check-question.sh")
    result = subprocess.run(["sh", str(check_question), str(docs), args.candidate_id], text=True, capture_output=True)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode

    try:
        entries = evidence_lines(queue, args.candidate_id)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    failures = 0
    if not entries:
        print(f"MISSING Evidence for {args.candidate_id}")
        failures += 1
    for entry in entries:
        match = EVIDENCE.match(entry)
        if not match:
            print(f"INVALID Evidence format for {args.candidate_id}: {entry}")
            failures += 1
            continue
        raw_path, raw_line, description = match.groups()
        source = (root / raw_path).resolve()
        line_number = int(raw_line)
        if not description.strip() or not in_scope(source, root):
            print(f"INVALID Evidence pointer for {args.candidate_id}: {raw_path}:{raw_line} -- outside input scope")
            failures += 1
            continue
        if not source.is_file():
            print(f"INVALID Evidence pointer for {args.candidate_id}: {raw_path}:{raw_line} -- file missing")
            failures += 1
            continue
        try:
            lines = source.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            print(f"INVALID Evidence pointer for {args.candidate_id}: {raw_path}:{raw_line} -- file is not UTF-8 text")
            failures += 1
            continue
        if line_number < 1 or line_number > len(lines):
            print(f"INVALID Evidence pointer for {args.candidate_id}: {raw_path}:{raw_line} -- line out of range")
            failures += 1
        elif not lines[line_number - 1].strip():
            print(f"INVALID Evidence pointer for {args.candidate_id}: {raw_path}:{raw_line} -- line is blank")
            failures += 1
    if failures:
        print(f"FAIL -- {failures} evidence violation(s).")
        return 1
    print(f"OK -- {args.candidate_id} evidence pointers are in-scope code lines.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

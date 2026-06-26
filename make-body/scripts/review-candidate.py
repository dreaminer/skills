#!/usr/bin/env python3
"""Render one validated Make Body candidate with all of its evidence contexts."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


CANDIDATE = re.compile(r"^## (MB-\d{3,})\s*$")
FIELD = re.compile(r"^(Type|Subject|Content|Evidence|Blocked by):")
EVIDENCE = re.compile(r"^- `([^`]+:\d+)` — .+$")
SYSTEM_HEADER = re.compile(r"^## \[(.+)\]\s*$")
WORD = re.compile(r"[a-z0-9]+")

ESSENTIAL_TYPES = {"essential-domain", "essential-usecase"}
ESSENTIAL_CHECKLIST = (
    "Subject names a business concept, not a System artifact (endpoint, table, queue, protocol).",
    "Every claim in Content is meaning a human can confirm, not an inference the code forces.",
    "The cited Evidence is consistent with the asserted meaning.",
    "Meaning the code cannot establish (intent, policy, ownership, cardinality, lifecycle) is named, not assumed.",
    "Verdict recorded as approve / revise / reject per references/essential-review.md.",
)


def block(queue: Path, identifier: str) -> list[str]:
    lines = queue.read_text(encoding="utf-8").splitlines()
    start = None
    for index, line in enumerate(lines):
        match = CANDIDATE.match(line)
        if match and match.group(1) == identifier:
            start = index
        elif start is not None and match:
            return lines[start:index]
    if start is None:
        raise ValueError(f"unknown candidate: {identifier}")
    return lines[start:]


def pointers(lines: list[str]) -> list[str]:
    section = ""
    found = []
    for line in lines[1:]:
        if line.startswith("Evidence:"):
            section = "evidence"
            continue
        if FIELD.match(line):
            section = ""
            continue
        if section == "evidence" and (match := EVIDENCE.match(line)):
            found.append(match.group(1))
    return found


def field_scalar(lines: list[str], name: str) -> str:
    """Return a scalar candidate field, whether written inline or on the next line."""
    prefix = f"{name}:"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            inline = line[len(prefix):].strip()
            if inline:
                return inline
            for follow in lines[index + 1:]:
                if FIELD.match(follow):
                    break
                if follow.strip():
                    return follow.strip().lstrip("- ").strip()
            return ""
    return ""


def content_text(lines: list[str]) -> str:
    section = ""
    parts = []
    for line in lines[1:]:
        if line.startswith("Content:"):
            section = "content"
            inline = line[len("Content:"):].strip()
            if inline:
                parts.append(inline)
            continue
        if FIELD.match(line):
            section = ""
            continue
        if section == "content" and line.strip():
            parts.append(line.strip().lstrip("- ").strip())
    return " ".join(parts)


def cited_line(project_root: Path, pointer: str) -> str:
    path_part, _, line_part = pointer.rpartition(":")
    try:
        number = int(line_part)
    except ValueError:
        return ""
    try:
        source = (project_root / path_part).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    return source[number - 1] if 1 <= number <= len(source) else ""


def canonical_system_subjects(docs: Path) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for name in ("SYSTEM_DOMAIN.md", "SYSTEM_USECASE.md"):
        path = docs / name
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            match = SYSTEM_HEADER.match(line)
            if match:
                subject = match.group(1).strip()
                if subject not in seen:
                    seen.add(subject)
                    ordered.append(subject)
    return ordered


def colocated_system_terms(subjects: list[str], haystack: str) -> list[str]:
    lowered = haystack.lower()
    found = []
    for subject in subjects:
        tokens = WORD.findall(subject.lower())
        if tokens and all(re.search(rf"\b{re.escape(token)}\b", lowered) for token in tokens):
            found.append(subject)
    return found


def render_essential_frame(project_root: Path, docs: Path, candidate: list[str], identifier: str) -> None:
    haystack = content_text(candidate) + " " + " ".join(cited_line(project_root, p) for p in pointers(candidate))
    terms = colocated_system_terms(canonical_system_subjects(docs), haystack)
    print()
    print(f"# Essential Review: {identifier}")
    print()
    print("This candidate asserts business meaning that code alone cannot confirm. It is never")
    print("auto-promoted; promotion requires explicit human confirmation. Judge it with the protocol")
    print("in `references/essential-review.md`.")
    print()
    print("## Co-located canonical System terms (lexical)")
    if terms:
        for term in terms:
            print(f"- [{term}]")
    else:
        print("- (none)")
    print()
    print("## Reviewer checklist")
    for item in ESSENTIAL_CHECKLIST:
        print(f"- [ ] {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    parser.add_argument("candidate_id")
    parser.add_argument("--radius", type=int, default=3)
    args = parser.parse_args()
    docs = args.docs_dir.resolve()
    queue = docs / "MAKE_BODY_CANDIDATES.md"
    if not queue.is_file():
        parser.error(f"missing candidate queue: {queue}")
    check = Path(__file__).with_name("check-evidence.py")
    result = subprocess.run([sys.executable, str(check), str(args.project_root), str(docs), args.candidate_id], text=True, capture_output=True)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode
    try:
        candidate = block(queue, args.candidate_id)
    except ValueError as error:
        parser.error(str(error))
    print(f"# Candidate Review: {args.candidate_id}")
    print()
    print("\n".join(candidate))
    show = Path(__file__).with_name("show-evidence.py")
    for pointer in pointers(candidate):
        result = subprocess.run([sys.executable, str(show), str(args.project_root), pointer, "--radius", str(args.radius)], text=True, capture_output=True)
        if result.returncode:
            sys.stderr.write(result.stdout + result.stderr)
            return result.returncode
        print()
        print(result.stdout, end="")
    if field_scalar(candidate, "Type") in ESSENTIAL_TYPES:
        render_essential_frame(args.project_root, docs, candidate, args.candidate_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

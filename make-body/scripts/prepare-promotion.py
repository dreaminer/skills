#!/usr/bin/env python3
"""Create a validated, byte-stable Make Body promotion preview."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


CANONICAL = (
    "ESSENTIAL_DOMAIN.md",
    "ESSENTIAL_USECASE.md",
    "SYSTEM_DOMAIN.md",
    "SYSTEM_USECASE.md",
)
QUEUE = "MAKE_BODY_CANDIDATES.md"
TARGET = {
    "essential-domain": "ESSENTIAL_DOMAIN.md",
    "essential-usecase": "ESSENTIAL_USECASE.md",
    "system-domain": "SYSTEM_DOMAIN.md",
    "system-usecase": "SYSTEM_USECASE.md",
}
FIELD = re.compile(r"^(Type|Subject|Content|Evidence|Blocked by):\s*(.*)$")
CANDIDATE = re.compile(r"^## (MB-\d{3,})\s*$")
EVIDENCE_POINTER = re.compile(r"^- `([^`]+):\d+` — .+$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_block(queue: Path, candidate_id: str) -> tuple[list[str], list[str]]:
    lines = queue.read_text(encoding="utf-8").splitlines(keepends=True)
    start = end = None
    for index, line in enumerate(lines):
        match = CANDIDATE.match(line.rstrip("\n"))
        if match and match.group(1) == candidate_id:
            start = index
            continue
        if start is not None and match:
            end = index
            break
    if start is None:
        raise ValueError(f"unknown candidate: {candidate_id}")
    if end is None:
        end = len(lines)
    return lines[start:end], lines[:start] + lines[end:]


def parse_candidate(lines: list[str]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {"Type": [], "Subject": [], "Content": [], "Evidence": [], "Blocked by": []}
    section: str | None = None
    for line in lines[1:]:
        match = FIELD.match(line.rstrip("\n"))
        if match:
            section, inline = match.groups()
            if inline:
                values[section].append(inline + "\n")
            continue
        if section is not None:
            values[section].append(line)
    return values


def one_plain_value(name: str, lines: list[str]) -> str:
    values = [line.strip() for line in lines if line.strip()]
    if len(values) != 1:
        raise ValueError(f"candidate has invalid {name}")
    return values[0]


def required_block(name: str, lines: list[str]) -> str:
    value = "".join(lines).strip()
    if not value or value == "-":
        raise ValueError(f"candidate has missing {name}")
    return value


def promoted_text(existing: str, candidate_type: str, subject: str, content: str, evidence: str) -> str:
    if candidate_type.endswith("-domain"):
        body = f"Meaning:\n{content}\n\nEvidence:\n{evidence}"
    else:
        body = f"{content}\n\nEvidence:\n{evidence}"
    return existing.rstrip() + f"\n\n## [{subject}]\n\n{body}\n"


def evidence_hashes(root: Path, lines: list[str]) -> dict[str, str]:
    hashes = {}
    for line in lines:
        match = EVIDENCE_POINTER.match(line.strip())
        if match:
            relative = match.group(1)
            hashes[relative] = digest(root / relative)
    return hashes


def write_manifest(path: Path, candidate_id: str, target: str, base: dict[str, str], preview: dict[str, str], evidence: dict[str, str]) -> None:
    lines = ["make-body-promotion-v1", f"candidate {candidate_id}", f"target {target}"]
    for name in (*CANONICAL, QUEUE):
        lines.append(f"base {name} {base[name]}")
        lines.append(f"preview {name} {preview[name]}")
    for name, source_hash in sorted(evidence.items()):
        lines.append("evidence " + json.dumps({"path": name, "sha256": source_hash}, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    parser.add_argument("candidate_id")
    parser.add_argument("preview_dir", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    docs = args.docs_dir.resolve()
    preview = args.preview_dir.resolve()
    if preview.exists():
        parser.error(f"preview directory already exists: {preview}")
    if not re.fullmatch(r"MB-\d{3,}", args.candidate_id):
        parser.error(f"invalid candidate id: {args.candidate_id}")
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    for name in (*CANONICAL, QUEUE):
        if not (docs / name).is_file():
            parser.error(f"missing input: {docs / name}")

    check_question = Path(__file__).with_name("check-question.sh")
    result = subprocess.run(["sh", str(check_question), str(docs), args.candidate_id], text=True, capture_output=True)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode
    check_evidence = Path(__file__).with_name("check-evidence.py")
    result = subprocess.run([sys.executable, str(check_evidence), str(root), str(docs), args.candidate_id], text=True, capture_output=True)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode

    block, remaining = selected_block(docs / QUEUE, args.candidate_id)
    fields = parse_candidate(block)
    candidate_type = one_plain_value("Type", fields["Type"])
    subject = one_plain_value("Subject", fields["Subject"])
    if candidate_type not in TARGET:
        raise ValueError(f"candidate has invalid Type: {candidate_type}")
    content = required_block("Content", fields["Content"])
    evidence = required_block("Evidence", fields["Evidence"])

    base = {name: digest(docs / name) for name in (*CANONICAL, QUEUE)}
    preview.mkdir(parents=True)
    for name in CANONICAL:
        shutil.copyfile(docs / name, preview / name)
    (preview / TARGET[candidate_type]).write_text(
        promoted_text((preview / TARGET[candidate_type]).read_text(encoding="utf-8"), candidate_type, subject, content, evidence),
        encoding="utf-8",
    )
    (preview / QUEUE).write_text("".join(remaining).rstrip() + "\n", encoding="utf-8")

    check_body = Path(__file__).with_name("check-body.sh")
    result = subprocess.run(["sh", str(check_body), str(preview)], text=True, capture_output=True)
    if result.returncode:
        shutil.rmtree(preview)
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode

    preview_hashes = {name: digest(preview / name) for name in (*CANONICAL, QUEUE)}
    write_manifest(preview / "MAKE_BODY_PROMOTION_MANIFEST", args.candidate_id, TARGET[candidate_type], base, preview_hashes, evidence_hashes(root, fields["Evidence"]))
    print(f"OK -- preview for {args.candidate_id}: {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

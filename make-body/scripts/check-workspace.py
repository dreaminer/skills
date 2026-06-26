#!/usr/bin/env python3
"""Run all deterministic Make Body checks for the current workspace."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


CANDIDATE = re.compile(r"^## (MB-\d{3,})\s*$")


def unblocked_candidates(queue: Path) -> tuple[list[str], int]:
    ready: list[str] = []
    identifier = ""
    blocked = False
    in_blocked = False

    def finish() -> None:
        nonlocal identifier
        if identifier:
            if blocked:
                pass
            else:
                ready.append(identifier)

    for raw in queue.read_text(encoding="utf-8").splitlines():
        match = CANDIDATE.match(raw)
        if match:
            finish()
            identifier = match.group(1)
            blocked = False
            in_blocked = False
            continue
        if not identifier:
            continue
        if raw.startswith("Blocked by:"):
            in_blocked = True
            inline = raw[len("Blocked by:") :].strip()
            if inline and inline != "-":
                blocked = True
            continue
        if in_blocked and raw.strip() and raw.strip() != "-":
            blocked = True
    finish()
    total = len([line for line in queue.read_text(encoding="utf-8").splitlines() if CANDIDATE.match(line)])
    return ready, total - len(ready)


def run(label: str, command: list[str]) -> bool:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode == 0:
        print(f"OK {label}")
        return True
    print(f"FAIL {label}")
    sys.stderr.write(result.stdout + result.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    parser.add_argument("--require-full-coverage", action="store_true", help="fail when an in-scope supported source has no fact or documented exception")
    args = parser.parse_args()
    root = args.project_root.resolve()
    docs = args.docs_dir.resolve()
    queue = docs / "MAKE_BODY_CANDIDATES.md"
    if not root.is_dir() or not queue.is_file():
        parser.error("project root and MAKE_BODY_CANDIDATES.md must exist")

    scripts = Path(__file__).parent
    passed = run("code-facts", [sys.executable, str(scripts / "check-code-facts.py"), str(root), str(docs / "MAKE_BODY_CODE_FACTS.md")])
    if args.require_full_coverage:
        passed = run(
            "fact-coverage",
            [
                sys.executable,
                str(scripts / "report-fact-coverage.py"),
                str(root),
                str(docs / "MAKE_BODY_CODE_FACTS.md"),
                "--ignore",
                str(docs / "MAKE_BODY_COVERAGE_IGNORE.md"),
                "--fail-on-unrepresented",
            ],
        ) and passed
    passed = run("canonical-body", ["sh", str(scripts / "check-body.sh"), str(docs)]) and passed
    passed = run("canonical-evidence", [sys.executable, str(scripts / "check-canonical-evidence.py"), str(root), str(docs)]) and passed
    passed = run("conflicts", [sys.executable, str(scripts / "check-conflicts.py"), str(root), str(docs)]) and passed
    passed = run("rejected", [sys.executable, str(scripts / "check-rejected.py"), str(root), str(docs)]) and passed
    passed = run("candidate-duplicates", [sys.executable, str(scripts / "check-candidate-duplicates.py"), str(docs)]) and passed
    ready, blocked = unblocked_candidates(queue)
    for identifier in ready:
        passed = run(
            f"candidate-{identifier}",
            [sys.executable, str(scripts / "check-evidence.py"), str(root), str(docs), identifier],
        ) and passed
    print(f"SKIPPED_BLOCKED={blocked}")
    status = subprocess.run([sys.executable, str(scripts / "report-status.py"), str(docs)], text=True, capture_output=True)
    if status.returncode:
        passed = False
        print("FAIL status")
        sys.stderr.write(status.stdout + status.stderr)
    else:
        print(status.stdout, end="")
    if passed:
        print("OK WORKSPACE")
        return 0
    print("FAIL WORKSPACE")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

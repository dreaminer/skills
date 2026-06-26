#!/usr/bin/env python3
"""Prepare and review the next ready System candidate, then stop at the consistency gate.

Refuses an Essential next candidate with NEEDS_HUMAN (exit 3). For a System candidate it audits
the workspace, prepares and reviews a byte-stable preview, then prints
AWAIT_GATE and exits 0 without applying: the consistency gate is a coordinator (LLM) step the
agent must run before calling apply-promotion.py on the preview. Exit 0 means "no error, proceed
to the gate" — it never means "applied", because this script never applies.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


NEXT = re.compile(r"^NEXT (MB-\d{3,}) ([-a-z]+) (.*)$", re.MULTILINE)
SYSTEM_TYPES = {"system-domain", "system-usecase"}


def run(command: list[str]) -> int:
    result = subprocess.run(command, text=True, capture_output=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    parser.add_argument("preview_dir", type=Path)
    args = parser.parse_args()
    scripts = Path(__file__).parent

    workspace = run([sys.executable, str(scripts / "check-workspace.py"), str(args.project_root), str(args.docs_dir)])
    if workspace:
        return workspace

    selection = subprocess.run(
        [sys.executable, str(scripts / "next-candidate.py"), str(args.project_root), str(args.docs_dir)],
        text=True,
        capture_output=True,
    )
    sys.stdout.write(selection.stdout)
    sys.stderr.write(selection.stderr)
    if selection.returncode:
        return selection.returncode

    match = NEXT.search(selection.stdout)
    if not match:
        print("next-candidate.py returned no selectable candidate", file=sys.stderr)
        return 1
    candidate_id, candidate_type, subject = match.groups()
    if candidate_type not in SYSTEM_TYPES:
        print(f"NEEDS_HUMAN -- next candidate is {candidate_type}: {candidate_id} {subject}")
        return 3

    prepared = run(
        [
            sys.executable,
            str(scripts / "prepare-promotion.py"),
            str(args.project_root),
            str(args.docs_dir),
            candidate_id,
            str(args.preview_dir),
        ]
    )
    if prepared:
        return prepared

    reviewed = run(
        [
            sys.executable,
            str(scripts / "review-promotion-preview.py"),
            str(args.project_root),
            str(args.docs_dir),
            str(args.preview_dir),
        ]
    )
    if reviewed:
        return reviewed

    # The consistency gate is a coordinator (LLM) step and cannot run inside this
    # deterministic script. Stop here with a validated, reviewed preview and hand off:
    # the agent runs the gate on this candidate and only then calls apply-promotion.py.
    print(f"AWAIT_GATE -- {candidate_id} {candidate_type} {subject} preview={args.preview_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

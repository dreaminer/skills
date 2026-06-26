#!/usr/bin/env python3
"""Select the next ready candidate and create its byte-stable promotion preview."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


NEXT = re.compile(r"^NEXT (MB-\d{3,})\b", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    parser.add_argument("preview_dir", type=Path)
    args = parser.parse_args()
    scripts = Path(__file__).parent
    selection = subprocess.run(
        [sys.executable, str(scripts / "next-candidate.py"), str(args.project_root), str(args.docs_dir)],
        text=True,
        capture_output=True,
    )
    if selection.returncode:
        sys.stdout.write(selection.stdout)
        sys.stderr.write(selection.stderr)
        return selection.returncode
    match = NEXT.search(selection.stdout)
    if not match:
        print("next-candidate.py returned no selectable candidate", file=sys.stderr)
        return 1
    print(selection.stdout, end="")
    result = subprocess.run(
        [
            sys.executable,
            str(scripts / "prepare-promotion.py"),
            str(args.project_root),
            str(args.docs_dir),
            match.group(1),
            str(args.preview_dir),
        ]
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

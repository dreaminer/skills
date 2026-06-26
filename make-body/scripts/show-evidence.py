#!/usr/bin/env python3
"""Print a bounded source window around one Make Body Evidence pointer."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


POINTER = re.compile(r"^([^:]+):(\d+)$")
EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".sql"}
EXCLUDED = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next", ".venv", "venv", "__pycache__"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("pointer", help="relative/path:line")
    parser.add_argument("--radius", type=int, default=3)
    args = parser.parse_args()
    if args.radius < 0:
        parser.error("radius must be non-negative")
    match = POINTER.match(args.pointer)
    if not match:
        parser.error(f"invalid pointer: {args.pointer}")
    raw_path, raw_line = match.groups()
    root = args.project_root.resolve()
    source = (root / raw_path).resolve()
    try:
        relative = source.relative_to(root)
    except ValueError:
        parser.error("pointer is outside project root")
    if source.suffix not in EXTENSIONS or any(part in EXCLUDED for part in relative.parts) or not source.is_file():
        parser.error("pointer is outside Make Body input scope")
    lines = source.read_text(encoding="utf-8").splitlines()
    line_number = int(raw_line)
    if line_number < 1 or line_number > len(lines):
        parser.error("pointer line is out of range")
    start = max(1, line_number - args.radius)
    end = min(len(lines), line_number + args.radius)
    print(f"# Evidence Context: {relative.as_posix()}:{line_number}")
    for number in range(start, end + 1):
        mark = ">" if number == line_number else " "
        print(f"{mark} {number:>4} | {lines[number - 1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

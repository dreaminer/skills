#!/usr/bin/env python3
"""Report in-scope source files that have no entry in a Make Body fact index."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".sql"}
EXCLUDED = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next", ".venv", "venv", "__pycache__"}
FACT = re.compile(r"^- `([^`]+):(\d+)` — .+$")
IGNORE = re.compile(r"^- `([^`]+)` — .+$")


def ignored_paths(path: Path) -> set[str]:
    ignored = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line == "# MAKE_BODY_COVERAGE_IGNORE":
            continue
        match = IGNORE.match(line)
        if not match:
            raise ValueError(f"invalid coverage ignore entry at {path}:{number}")
        source = match.group(1)
        if source in ignored:
            raise ValueError(f"duplicate coverage ignore entry at {path}:{number}: {source}")
        ignored.add(source)
    return ignored


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path); parser.add_argument("facts", type=Path)
    parser.add_argument("--ignore", type=Path, help="MAKE_BODY_COVERAGE_IGNORE.md with documented source exceptions")
    parser.add_argument("--fail-on-unrepresented", action="store_true", help="exit non-zero when an in-scope source has no fact")
    args = parser.parse_args(); root = args.project_root.resolve(); facts = args.facts.resolve()
    if not root.is_dir(): parser.error(f"project root is not a directory: {root}")
    if not facts.is_file(): parser.error(f"missing fact index: {facts}")
    sources = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() and path.suffix in EXTENSIONS and not any(part in EXCLUDED for part in path.relative_to(root).parts))
    ignored = set()
    if args.ignore:
        ignore = args.ignore.resolve()
        if not ignore.is_file(): parser.error(f"missing coverage ignore file: {ignore}")
        try:
            ignored = ignored_paths(ignore)
        except ValueError as error:
            parser.error(str(error))
        unknown = ignored - set(sources)
        if unknown: parser.error(f"coverage ignore is not an in-scope source: {sorted(unknown)[0]}")
    represented = set()
    for line in facts.read_text(encoding="utf-8").splitlines():
        if match := FACT.match(line): represented.add(match.group(1))
    stale = ignored & represented
    if stale: parser.error(f"coverage ignore already has facts: {sorted(stale)[0]}")
    absent = [path for path in sources if path not in represented and path not in ignored]
    print(f"FILES_IN_SCOPE={len(sources)}")
    print(f"FILES_WITH_FACTS={len(sources) - len(absent) - len(ignored)}")
    print(f"FILES_WITHOUT_FACTS={len(absent)}")
    print(f"FILES_IGNORED={len(ignored)}")
    for path in absent: print(f"UNREPRESENTED {path}")
    return 1 if args.fail_on_unrepresented and absent else 0


if __name__ == "__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""Verify that canonical Make Body Evidence pointers still name in-scope code lines."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DOCUMENTS = ("ESSENTIAL_DOMAIN.md", "ESSENTIAL_USECASE.md", "SYSTEM_DOMAIN.md", "SYSTEM_USECASE.md")
POINTER = re.compile(r"^- `([^`]+):(\d+)` — .+$")
EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".sql"}
EXCLUDED = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next", ".venv", "venv", "__pycache__"}


def valid_pointer(root: Path, raw_path: str, raw_line: str) -> str | None:
    source = (root / raw_path).resolve()
    try:
        relative = source.relative_to(root)
    except ValueError:
        return "outside project root"
    if source.suffix not in EXTENSIONS or any(part in EXCLUDED for part in relative.parts) or not source.is_file():
        return "outside input scope or file missing"
    lines = source.read_text(encoding="utf-8").splitlines()
    line_number = int(raw_line)
    if line_number < 1 or line_number > len(lines) or not lines[line_number - 1].strip():
        return "line missing or blank"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    docs = args.docs_dir.resolve()
    if not root.is_dir(): parser.error(f"project root is not a directory: {root}")
    missing = [name for name in DOCUMENTS if not (docs / name).is_file()]
    if missing: parser.error("missing canonical documents: " + ", ".join(missing))
    failures = pointers = 0
    for name in DOCUMENTS:
        evidence = False
        for raw in (docs / name).read_text(encoding="utf-8").splitlines():
            if raw.startswith("## "):
                evidence = False
            elif raw.startswith("Evidence:"):
                evidence = True
                inline = raw[len("Evidence:") :].strip()
                if inline: raw = inline
                else: continue
            elif raw.endswith(":"):
                evidence = False
            if not evidence or not raw.strip(): continue
            match = POINTER.match(raw.strip())
            if not match:
                print(f"INVALID canonical Evidence format in {name}: {raw}"); failures += 1; continue
            pointers += 1
            problem = valid_pointer(root, match.group(1), match.group(2))
            if problem:
                print(f"INVALID canonical Evidence pointer in {name}: {match.group(1)}:{match.group(2)} -- {problem}")
                failures += 1
    if failures:
        print(f"FAIL -- {failures} canonical evidence violation(s).")
        return 1
    print(f"OK -- {pointers} canonical Evidence pointer(s) are valid.")
    return 0


if __name__ == "__main__": raise SystemExit(main())

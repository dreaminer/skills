#!/usr/bin/env python3
"""List lexical in-scope uses of one identifier for Make Body caller/callee review."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py"}
EXCLUDED = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next", ".venv", "venv", "__pycache__"}
SYMBOL = re.compile(r"^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("symbol")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    if not SYMBOL.match(args.symbol): parser.error(f"invalid symbol: {args.symbol}")
    if args.limit < 1: parser.error("limit must be positive")
    root = args.project_root.resolve()
    if not root.is_dir(): parser.error(f"project root is not a directory: {root}")
    expression = re.compile(rf"(?<![\w$]){re.escape(args.symbol)}(?![\w$])")
    uses = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in EXTENSIONS: continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED for part in relative.parts): continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if expression.search(line): uses.append((relative.as_posix(), number, line.strip()))
    print(f"# Symbol Uses: {args.symbol}")
    if not uses:
        print("NO_USES")
        return 0
    for path, number, snippet in uses[: args.limit]: print(f"- `{path}:{number}` — {snippet}")
    if len(uses) > args.limit: print(f"TRUNCATED {len(uses) - args.limit} additional use(s)")
    return 0


if __name__ == "__main__": raise SystemExit(main())

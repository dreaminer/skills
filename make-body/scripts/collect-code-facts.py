#!/usr/bin/env python3
"""Combine supported Make Body adapter facts into one deterministic index."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


KINDS = ("direct-call", "effect-call", "exported-symbol", "http-entry", "schema-constraint", "schema-table", "worker-entry")
FACT = re.compile(r"^- `([^`]+)` — (.+)$")
EXCLUDED = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next", ".venv", "venv", "__pycache__"}


def has_extension(root: Path, extensions: set[str]) -> bool:
    return any(path.is_file() and path.suffix in extensions and not any(part in EXCLUDED for part in path.relative_to(root).parts) for path in root.rglob("*"))


def parse(path: Path) -> tuple[str, dict[str, set[tuple[str, str]]]]:
    adapter = ""; kind = ""; facts: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Adapter: "): adapter = line[len("Adapter: "):]
        elif line.startswith("## "): kind = line[3:]
        elif kind and (match := FACT.match(line)): facts[kind].add((match.group(1), match.group(2)))
    return adapter, facts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args(); root = args.project_root.resolve()
    if not root.is_dir(): parser.error(f"project root is not a directory: {root}")
    scripts = Path(__file__).parent
    commands = []
    if has_extension(root, {".ts", ".tsx", ".js", ".jsx"}): commands.append(scripts / "collect-typescript-facts.py")
    if has_extension(root, {".py"}): commands.append(scripts / "collect-python-facts.py")
    combined: dict[str, set[tuple[str, str]]] = defaultdict(set); adapters = []
    with tempfile.TemporaryDirectory() as temporary:
        for index, script in enumerate(commands):
            result = Path(temporary) / f"{index}.md"
            subprocess.run([sys.executable, str(script), str(root), str(result)], check=True)
            adapter, facts = parse(result); adapters.append(adapter)
            for kind, entries in facts.items(): combined[kind].update(entries)
    label = "combined-lexical-v1" + (" (" + ", ".join(adapters) + ")" if adapters else " (no-supported-code)")
    output = ["# MAKE_BODY_CODE_FACTS", "", f"Adapter: {label}", ""]
    for kind in KINDS:
        entries = sorted(combined.get(kind, set()))
        if entries:
            output.extend((f"## {kind}", "")); output.extend(f"- `{location}` — {detail}" for location, detail in entries); output.append("")
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text("\n".join(output), encoding="utf-8")
    return 0


if __name__ == "__main__": raise SystemExit(main())

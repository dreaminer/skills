#!/usr/bin/env python3
"""Collect deterministic lexical code facts for Make Body's Python adapter."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


EXTENSIONS = {".py", ".sql"}
EXCLUDED = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".venv", "venv", "__pycache__"}
KINDS = ("direct-call", "effect-call", "exported-symbol", "http-entry", "schema-constraint", "schema-table", "worker-entry")
HTTP = re.compile(r"^\s*@(?:app|router)\.(?:get|post|put|patch|delete)\s*\(")
WORKER = re.compile(r"^\s*@(?:app|celery)\.task\b|^\s*@task\b")
DEF = re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(")
CLASS = re.compile(r"^\s*class\s+([A-Za-z_]\w*)\b")
CALL = re.compile(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\(")
EFFECT = re.compile(r"\.(save|insert|update|delete|emit|publish|enqueue|send|commit|rollback)\s*\(")
TABLE = re.compile(r"\bCREATE\s+TABLE\s+([A-Za-z_][\w.]*)", re.I)
CONSTRAINT = re.compile(r"\b(?:PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|NOT\s+NULL)\b", re.I)
KEYWORDS = {"if", "for", "while", "with", "except", "return", "def", "class"}


def files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.suffix in EXTENSIONS and not any(part in EXCLUDED for part in path.relative_to(root).parts)
    )


def collect(root: Path) -> dict[str, set[tuple[str, str]]]:
    facts: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for path in files(root):
        lines = path.read_text(encoding="utf-8").splitlines()
        pending: list[tuple[str, int, str]] = []
        for number, line in enumerate(lines, 1):
            location = f"{path.relative_to(root).as_posix()}:{number}"
            snippet = line.strip()
            if path.suffix == ".sql":
                for match in TABLE.finditer(line): facts["schema-table"].add((location, match.group(1)))
                if CONSTRAINT.search(line): facts["schema-constraint"].add((location, snippet))
                continue
            if HTTP.match(line): pending.append(("http-entry", number, snippet)); continue
            if WORKER.match(line): pending.append(("worker-entry", number, snippet)); continue
            definition = DEF.match(line)
            if definition:
                name = definition.group(1)
                if not name.startswith("_"): facts["exported-symbol"].add((location, name))
                for kind, decorator_line, decorator in pending:
                    facts[kind].add((f"{path.relative_to(root).as_posix()}:{decorator_line}", f"{decorator} -> {name}"))
                pending.clear()
                continue
            class_match = CLASS.match(line)
            if class_match and not class_match.group(1).startswith("_"):
                facts["exported-symbol"].add((location, class_match.group(1)))
            if snippet and not snippet.startswith("#"):
                if EFFECT.search(line): facts["effect-call"].add((location, snippet))
                for match in CALL.finditer(line):
                    if match.group(1) not in KEYWORDS: facts["direct-call"].add((location, match.group(1)))
    return facts


def render(facts: dict[str, set[tuple[str, str]]]) -> str:
    result = ["# MAKE_BODY_CODE_FACTS", "", "Adapter: python-lexical-v1", ""]
    for kind in KINDS:
        entries = sorted(facts.get(kind, set()))
        if entries:
            result.extend((f"## {kind}", ""))
            result.extend(f"- `{location}` — {detail}" for location, detail in entries)
            result.append("")
    return "\n".join(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args(); root = args.project_root.resolve()
    if not root.is_dir(): parser.error(f"project root is not a directory: {root}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(collect(root)), encoding="utf-8")
    return 0


if __name__ == "__main__": raise SystemExit(main())

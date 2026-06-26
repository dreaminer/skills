#!/usr/bin/env python3
"""Collect deterministic lexical code facts for Make Body's TypeScript adapter."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".sql"}
EXCLUDED_DIRS = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next"}
EXCLUDED_SUFFIXES = (".d.ts", ".min.js")
KINDS = (
    "direct-call",
    "effect-call",
    "exported-symbol",
    "http-entry",
    "schema-constraint",
    "schema-table",
    "worker-entry",
)

HTTP_ENTRY = re.compile(r"\b(?:app|router|server)\.(?:get|post|put|patch|delete|use)\s*\(")
WORKER_ENTRY = re.compile(
    r"\b(?:new\s+Worker|[A-Za-z_$][\w$]*\.process\s*\(|consume\s*\(|schedule\s*\(|cron\s*\(|on\s*\(\s*['\"]message['\"])"
)
EXPORTED_SYMBOL = re.compile(
    r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let)\s+([A-Za-z_$][\w$]*)"
)
CALL = re.compile(r"\b([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*\(")
EFFECT = re.compile(r"\.(save|insert|update|delete|emit|publish|enqueue|send|commit|rollback)\s*\(")
CREATE_TABLE = re.compile(r"\bCREATE\s+TABLE\s+([A-Za-z_][\w.]*)", re.IGNORECASE)
CONSTRAINT = re.compile(r"\b(?:PRIMARY\s+KEY|FOREIGN\s+KEY|UNIQUE|NOT\s+NULL)\b", re.IGNORECASE)
KEYWORDS = {"if", "for", "while", "switch", "catch", "function", "return", "typeof", "new"}
FUNCTION_DECLARATION = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\("
)


def is_in_scope(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.suffix not in SOURCE_EXTENSIONS:
        return False
    return not path.name.endswith(EXCLUDED_SUFFIXES) and ".generated." not in path.name


def source_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and is_in_scope(path, root))


def pointer(root: Path, path: Path, line_number: int) -> str:
    return f"{path.relative_to(root).as_posix()}:{line_number}"


def collect(root: Path) -> dict[str, set[tuple[str, str]]]:
    facts: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for path in source_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            location = pointer(root, path, line_number)
            snippet = line.strip()
            if not snippet:
                continue

            if path.suffix == ".sql":
                for match in CREATE_TABLE.finditer(line):
                    facts["schema-table"].add((location, match.group(1)))
                if CONSTRAINT.search(line):
                    facts["schema-constraint"].add((location, snippet))
                continue

            for match in EXPORTED_SYMBOL.finditer(line):
                facts["exported-symbol"].add((location, match.group(1)))
            if HTTP_ENTRY.search(line):
                facts["http-entry"].add((location, snippet))
            if WORKER_ENTRY.search(line):
                facts["worker-entry"].add((location, snippet))
            if EFFECT.search(line):
                facts["effect-call"].add((location, snippet))
            if not FUNCTION_DECLARATION.search(line):
                for match in CALL.finditer(line):
                    name = match.group(1)
                    if name not in KEYWORDS:
                        facts["direct-call"].add((location, name))
    return facts


def render(facts: dict[str, set[tuple[str, str]]]) -> str:
    output = ["# MAKE_BODY_CODE_FACTS", "", "Adapter: typescript-node-lexical-v1", ""]
    for kind in KINDS:
        entries = sorted(facts.get(kind, set()))
        if not entries:
            continue
        output.extend((f"## {kind}", ""))
        output.extend(f"- `{location}` — {detail}" for location, detail in entries)
        output.append("")
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    root = args.project_root.resolve()
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(collect(root)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

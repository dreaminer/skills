#!/usr/bin/env python3
"""Render lexical System flow traces from a Make Body fact index."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


FACT = re.compile(r"^- `([^`]+)` — (.+)$")
TS_HTTP = re.compile(r"^\s*(?:app|router|server)\.(get|post|put|patch|delete|use)\(\s*(['\"])(.*?)\2\s*,\s*([A-Za-z_$][\w$]*)")
PY_HTTP = re.compile(r"^@(app|router)\.(get|post|put|patch|delete)\(\s*(['\"])(.*?)\3.*\)\s*->\s*([A-Za-z_]\w*)$")
TS_WORKER = re.compile(r"^\s*[A-Za-z_$][\w$]*\.process\(\s*(['\"])(.*?)\1\s*,\s*([A-Za-z_$][\w$]*)")
PY_WORKER = re.compile(r"^@(?:app|celery)\.task\s*->\s*([A-Za-z_]\w*)$|^@task\s*->\s*([A-Za-z_]\w*)$")


@dataclass(frozen=True)
class Fact:
    kind: str
    location: str
    detail: str


@dataclass(frozen=True)
class Entry:
    location: str
    detail: str
    label: str
    handler: str | None


@dataclass(frozen=True)
class Body:
    path: str
    start: int
    end: int


def parse_facts(path: Path) -> list[Fact]:
    facts: list[Fact] = []
    kind = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            kind = line[3:].strip()
            continue
        match = FACT.match(line)
        if match and kind:
            facts.append(Fact(kind, match.group(1), match.group(2)))
    return facts


def pointer_parts(location: str) -> tuple[str, int] | None:
    path, separator, line = location.rpartition(":")
    if not separator:
        return None
    try:
        return path, int(line)
    except ValueError:
        return None


def source_line(root: Path, location: str) -> str:
    parts = pointer_parts(location)
    if parts is None:
        return ""
    relative, line_number = parts
    path = root / relative
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return ""
    if line_number < 1 or line_number > len(lines):
        return ""
    return lines[line_number - 1].strip()


def entry_from(fact: Fact) -> Entry | None:
    if fact.kind == "http-entry":
        ts = TS_HTTP.match(fact.detail)
        if ts:
            method, _, route, handler = ts.groups()
            return Entry(fact.location, fact.detail, f"{method.upper()} {route} -> {handler}", handler)
        py = PY_HTTP.match(fact.detail)
        if py:
            _, method, _, route, handler = py.groups()
            return Entry(fact.location, fact.detail, f"{method.upper()} {route} -> {handler}", handler)
    if fact.kind == "worker-entry":
        ts_worker = TS_WORKER.match(fact.detail)
        if ts_worker:
            _, queue, handler = ts_worker.groups()
            return Entry(fact.location, fact.detail, f"queue {queue} -> {handler}", handler)
        py_worker = PY_WORKER.match(fact.detail)
        if py_worker:
            handler = next(value for value in py_worker.groups() if value)
            return Entry(fact.location, fact.detail, f"task -> {handler}", handler)
        return Entry(fact.location, fact.detail, fact.detail, None)
    return None


def exported_symbols(facts: list[Fact]) -> dict[str, list[Fact]]:
    symbols: dict[str, list[Fact]] = {}
    for fact in facts:
        if fact.kind == "exported-symbol":
            symbols.setdefault(fact.detail, []).append(fact)
    return {name: sorted(items, key=lambda item: item.location) for name, items in symbols.items()}


def ts_body(root: Path, relative: str, line_number: int) -> Body:
    path = root / relative
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return Body(relative, line_number, line_number)
    depth = 0
    seen_open = False
    for index in range(max(line_number - 1, 0), len(lines)):
        line = lines[index]
        depth += line.count("{")
        if "{" in line:
            seen_open = True
        depth -= line.count("}")
        if seen_open and depth <= 0:
            return Body(relative, line_number, index + 1)
    return Body(relative, line_number, min(len(lines), line_number + 40))


def py_body(root: Path, relative: str, line_number: int) -> Body:
    path = root / relative
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return Body(relative, line_number, line_number)
    if line_number < 1 or line_number > len(lines):
        return Body(relative, line_number, line_number)
    base_indent = len(lines[line_number - 1]) - len(lines[line_number - 1].lstrip(" "))
    end = line_number
    for index in range(line_number, len(lines)):
        line = lines[index]
        if not line.strip():
            end = index + 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= base_indent:
            break
        end = index + 1
    return Body(relative, line_number, end)


def body_for(root: Path, symbol_fact: Fact | None) -> Body | None:
    if symbol_fact is None:
        return None
    parts = pointer_parts(symbol_fact.location)
    if parts is None:
        return None
    relative, line_number = parts
    suffix = Path(relative).suffix
    if suffix == ".py":
        return py_body(root, relative, line_number)
    return ts_body(root, relative, line_number)


def in_body(location: str, body: Body | None) -> bool:
    if body is None:
        return False
    parts = pointer_parts(location)
    if parts is None:
        return False
    relative, line_number = parts
    return relative == body.path and body.start <= line_number <= body.end


def related(facts: list[Fact], kind: str, body: Body | None) -> list[Fact]:
    return sorted((fact for fact in facts if fact.kind == kind and in_body(fact.location, body)), key=lambda fact: (fact.location, fact.detail))


def schema_facts(facts: list[Fact]) -> list[Fact]:
    return sorted((fact for fact in facts if fact.kind in {"schema-table", "schema-constraint"}), key=lambda fact: (fact.location, fact.detail))


def render_fact(root: Path, fact: Fact, include_call_name: bool = False) -> str:
    snippet = source_line(root, fact.location) or fact.detail
    if include_call_name:
        return f"- `{fact.location}` — {fact.detail} — {snippet}"
    return f"- `{fact.location}` — {snippet}"


def render(root: Path, facts_path: Path, facts: list[Fact]) -> str:
    entries = sorted((entry for fact in facts if (entry := entry_from(fact)) is not None), key=lambda entry: (entry.location, entry.label))
    symbols = exported_symbols(facts)
    lines = [
        "# MAKE_BODY_FLOW_TRACES",
        "",
        f"Generated from: {facts_path.name}",
        "",
        "Trace limits:",
        "- lexical entrypoint trace only",
        "- handler symbol resolution uses exported-symbol facts",
        "- direct/effect calls are limited to the resolved handler body",
        "- not a call graph proof",
        "- not a Make Body candidate",
        "",
        "Project schema facts:",
    ]
    schema = schema_facts(facts)
    lines.extend(f"- `{fact.location}` — {fact.detail}" for fact in schema)
    if not schema:
        lines.append("- none")
    lines.append("")
    if not entries:
        lines.append("No entrypoint facts found.")
        return "\n".join(lines) + "\n"

    for index, entry in enumerate(entries, start=1):
        handler_fact = symbols.get(entry.handler or "", [None])[0]
        body = body_for(root, handler_fact)
        calls = related(facts, "direct-call", body)
        effects = related(facts, "effect-call", body)
        lines.extend((f"## FT-{index:03d} {entry.label}", "", "Entry:", f"- `{entry.location}` — {entry.detail}", "", "Handler:"))
        if handler_fact is None:
            lines.append(f"- unresolved: {entry.handler or 'unknown'}")
        else:
            lines.append(render_fact(root, handler_fact))
        lines.extend(("", "Calls:"))
        lines.extend(render_fact(root, fact, include_call_name=True) for fact in calls)
        if not calls:
            lines.append("- none")
        lines.extend(("", "Effects:"))
        lines.extend(render_fact(root, fact) for fact in effects)
        if not effects:
            lines.append("- none")
        lines.extend(("", "Trace limits:"))
        if body is None:
            lines.append("- handler body: unresolved")
        else:
            lines.append(f"- handler body: `{body.path}:{body.start}-{body.end}`")
        lines.extend(("- lexical 1-hop only", "- not a System UseCase candidate", ""))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("facts", type=Path, help="MAKE_BODY_CODE_FACTS.md")
    args = parser.parse_args()
    root = args.project_root.resolve()
    facts_path = args.facts.resolve()
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    if not facts_path.is_file():
        parser.error(f"fact index does not exist: {facts_path}")
    print(render(root, facts_path, parse_facts(facts_path)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

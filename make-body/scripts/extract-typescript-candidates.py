#!/usr/bin/env python3
"""Seed conservative System candidates from a Make Body TypeScript fact index."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from rejected_index import rejected_keys


FACT_LINE = re.compile(r"^- `([^`]+)` — (.+)$")
HTTP = re.compile(
    r"^\s*(?:app|router|server)\.(get|post|put|patch|delete|use)\(\s*(['\"])(.*?)\2\s*,\s*([A-Za-z_$][\w$]*)"
)
WORKER = re.compile(
    r"^\s*[A-Za-z_$][\w$]*\.process\(\s*(['\"])(.*?)\1\s*,\s*([A-Za-z_$][\w$]*)"
)


@dataclass(frozen=True)
class Fact:
    kind: str
    location: str
    detail: str


@dataclass(frozen=True)
class Candidate:
    candidate_type: str
    subject: str
    content: tuple[str, ...]
    location: str
    detail: str


def parse_facts(path: Path) -> list[Fact]:
    current_kind = ""
    facts: list[Fact] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_kind = line[3:].strip()
            continue
        match = FACT_LINE.match(line)
        if match and current_kind:
            facts.append(Fact(current_kind, match.group(1), match.group(2)))
    return facts


def title_words(value: str) -> str:
    words = re.sub(r"[^A-Za-z0-9]+", " ", value).split()
    return " ".join(word[:1].upper() + word[1:] for word in words) or "Unnamed"


def candidates_from(facts: list[Fact]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for fact in facts:
        if fact.kind == "schema-table":
            candidates.append(
                Candidate(
                    "system-domain",
                    f"{title_words(fact.detail)} Table",
                    (f"- [{{subject}}] is created by `CREATE TABLE {fact.detail}`.",),
                    fact.location,
                    f"CREATE TABLE {fact.detail}",
                )
            )
            continue

        if fact.kind == "http-entry":
            match = HTTP.match(fact.detail)
            if not match:
                continue
            method, _, path, handler = match.groups()
            candidates.append(
                Candidate(
                    "system-usecase",
                    f"{method.upper()} {path} Route",
                    (
                        "Given:",
                        f"- The `{method.upper()} {path}` route is registered.",
                        "",
                        "When:",
                        f"- The route dispatches `{handler}`.",
                        "",
                        "Then:",
                        "- The registered handler is invoked.",
                    ),
                    fact.location,
                    fact.detail,
                )
            )
            continue

        if fact.kind == "worker-entry":
            match = WORKER.match(fact.detail)
            if not match:
                continue
            _, queue, handler = match.groups()
            candidates.append(
                Candidate(
                    "system-usecase",
                    f"{title_words(queue)} Queue Process",
                    (
                        "Given:",
                        f"- The `{queue}` queue process is registered.",
                        "",
                        "When:",
                        f"- The process dispatches `{handler}`.",
                        "",
                        "Then:",
                        "- The registered handler is invoked.",
                    ),
                    fact.location,
                    fact.detail,
                )
            )

    return sorted(set(candidates), key=lambda item: (item.candidate_type, item.subject, item.location))


def render(candidates: list[Candidate]) -> str:
    output = ["# MAKE_BODY_CANDIDATES", ""]
    for number, candidate in enumerate(candidates, start=1):
        output.extend((f"## MB-{number:03d}", "", "Type:", candidate.candidate_type, "", "Subject:", candidate.subject, "", "Content:"))
        output.extend(line.replace("{subject}", candidate.subject) for line in candidate.content)
        output.extend(("", "Evidence:", f"- `{candidate.location}` — {candidate.detail}", "", "Blocked by:", "-", ""))
    return "\n".join(output)


def may_replace(path: Path, replace: bool) -> bool:
    if not path.exists() or replace:
        return True
    existing = path.read_text(encoding="utf-8").strip()
    return existing in {"", "# MAKE_BODY_CANDIDATES"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("facts", type=Path, help="MAKE_BODY_CODE_FACTS.md")
    parser.add_argument("output", type=Path, help="MAKE_BODY_CANDIDATES.md")
    parser.add_argument("--replace", action="store_true", help="replace a non-empty candidate queue")
    args = parser.parse_args()

    if not args.facts.is_file():
        parser.error(f"fact index does not exist: {args.facts}")
    if not may_replace(args.output, args.replace):
        print(f"refusing to replace non-empty candidate queue: {args.output}; use --replace", file=sys.stderr)
        return 2

    seeds = candidates_from(parse_facts(args.facts))
    rejected = rejected_keys(args.output.parent / "MAKE_BODY_REJECTED.md")
    seeds = [seed for seed in seeds if (seed.candidate_type, seed.subject, seed.location) not in rejected]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(seeds), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

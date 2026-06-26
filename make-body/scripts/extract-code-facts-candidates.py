#!/usr/bin/env python3
"""Seed conservative System candidates from combined Make Body fact indexes."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from rejected_index import rejected_keys


FACT = re.compile(r"^- `([^`]+)` — (.+)$")
TS_HTTP = re.compile(r"^\s*(?:app|router|server)\.(get|post|put|patch|delete)\(\s*(['\"])(.*?)\2\s*,\s*([A-Za-z_$][\w$]*)")
PY_HTTP = re.compile(r"^@(app|router)\.(get|post|put|patch|delete)\(\s*(['\"])(.*?)\3.*\)\s*->\s*([A-Za-z_]\w*)$")
TS_WORKER = re.compile(r"^\s*[A-Za-z_$][\w$]*\.process\(\s*(['\"])(.*?)\1\s*,\s*([A-Za-z_$][\w$]*)")
PY_WORKER = re.compile(r"^@(?:app|celery)\.task\s*->\s*([A-Za-z_]\w*)$|^@task\s*->\s*([A-Za-z_]\w*)$")


def title(value: str) -> str: return " ".join(part[:1].upper() + part[1:] for part in re.sub(r"[^A-Za-z0-9]+", " ", value).split()) or "Unnamed"
def facts(path: Path):
    kind = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "): kind = line[3:]
        elif kind and (match := FACT.match(line)): yield kind, match.group(1), match.group(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("facts", type=Path); parser.add_argument("output", type=Path); parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and args.output.read_text(encoding="utf-8").strip() not in {"", "# MAKE_BODY_CANDIDATES"} and not args.replace:
        print(f"refusing to replace non-empty candidate queue: {args.output}; use --replace", file=sys.stderr); return 2
    candidates = []
    for kind, location, detail in facts(args.facts):
        if kind == "schema-table": candidates.append(("system-domain", f"{title(detail)} Table", (f"- [{{subject}}] is created by `CREATE TABLE {detail}`.",), location, f"CREATE TABLE {detail}"))
        elif kind == "http-entry":
            match = TS_HTTP.match(detail) or PY_HTTP.match(detail)
            if match:
                groups = match.groups(); method, path, handler = groups[-4], groups[-2], groups[-1]
                candidates.append(("system-usecase", f"{method.upper()} {path} Route", ("Given:", f"- The `{method.upper()} {path}` route is registered.", "", "When:", f"- The route dispatches `{handler}`.", "", "Then:", "- The registered handler is invoked."), location, detail))
        elif kind == "worker-entry":
            match = TS_WORKER.match(detail)
            if match:
                _, queue, handler = match.groups(); subject = f"{title(queue)} Queue Process"; given = f"- The `{queue}` queue process is registered."; when = f"- The process dispatches `{handler}`."
            else:
                py = PY_WORKER.match(detail)
                if not py: continue
                handler = next(value for value in py.groups() if value); subject = f"{title(handler)} Task"; given = f"- The `{handler}` task is registered."; when = "- The task is dispatched."
            candidates.append(("system-usecase", subject, ("Given:", given, "", "When:", when, "", "Then:", "- The registered handler is invoked."), location, detail))
    candidates = sorted(set(candidates), key=lambda item: (item[0], item[1], item[3]))
    rejected = rejected_keys(args.output.parent / "MAKE_BODY_REJECTED.md")
    candidates = [item for item in candidates if (item[0], item[1], item[3]) not in rejected]
    output = ["# MAKE_BODY_CANDIDATES", ""]
    for index, (kind, subject, content, location, detail) in enumerate(candidates, 1):
        output.extend((f"## MB-{index:03d}", "", "Type:", kind, "", "Subject:", subject, "", "Content:")); output.extend(line.replace("{subject}", subject) for line in content); output.extend(("", "Evidence:", f"- `{location}` — {detail}", "", "Blocked by:", "-", ""))
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text("\n".join(output), encoding="utf-8"); return 0


if __name__ == "__main__": raise SystemExit(main())

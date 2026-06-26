#!/usr/bin/env python3
"""Verify that a generated Make Body fact index still matches its project source."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


ADAPTERS = {
    "typescript-node-lexical-v1": "collect-typescript-facts.py",
    "python-lexical-v1": "collect-python-facts.py",
    "combined-lexical-v1": "collect-code-facts.py",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("facts", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve(); facts = args.facts.resolve()
    if not root.is_dir(): parser.error(f"project root is not a directory: {root}")
    if not facts.is_file(): parser.error(f"missing fact index: {facts}")
    adapter_line = next((line for line in facts.read_text(encoding="utf-8").splitlines() if line.startswith("Adapter: ")), "")
    if not adapter_line:
        print("SKIP -- code fact index has no generated adapter.")
        return 0
    adapter = adapter_line[len("Adapter: "):].split(" (", 1)[0]
    script = ADAPTERS.get(adapter)
    if script is None:
        parser.error(f"unsupported fact adapter: {adapter}")
    with tempfile.TemporaryDirectory() as temporary:
        regenerated = Path(temporary) / "MAKE_BODY_CODE_FACTS.md"
        result = subprocess.run([sys.executable, str(Path(__file__).with_name(script)), str(root), str(regenerated)])
        if result.returncode: return result.returncode
        if regenerated.read_bytes() != facts.read_bytes():
            print(f"STALE -- regenerate {facts.name} with {script}.")
            return 1
    print(f"OK -- {facts.name} matches {adapter} source facts.")
    return 0


if __name__ == "__main__": raise SystemExit(main())

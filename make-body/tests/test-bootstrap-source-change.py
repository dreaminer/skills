#!/usr/bin/env python3
"""Change a supported source after staged audit and verify bootstrap does not apply it."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path


def load(path: Path):
    spec = importlib.util.spec_from_file_location("bootstrap_make_body", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    bootstrap = load(Path(sys.argv[1]))
    fixture = Path(sys.argv[2])
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        project = root / "project"
        docs = root / "docs"
        shutil.copytree(fixture, project)
        original_run = bootstrap.run
        calls = 0

        def mutate_after_audit(command: list[str]) -> int:
            nonlocal calls
            result = original_run(command)
            calls += 1
            if calls == 4:
                source = project / "src" / "api.ts"
                source.write_text(source.read_text(encoding="utf-8") + "\n// concurrent change\n", encoding="utf-8")
            return result

        bootstrap.run = mutate_after_audit
        try:
            result, changes = bootstrap.execute_bootstrap(
                project,
                docs,
                Path(sys.argv[1]).parent,
                "collect-code-facts.py",
                "extract-code-facts-candidates.py",
            )
        finally:
            bootstrap.run = original_run
        if result != 2 or changes:
            raise AssertionError(f"expected source-change rejection, got result={result} changes={changes}")
        if docs.exists():
            raise AssertionError("source-change rejection wrote documents")
    print("OK bootstrap rejects staged source changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

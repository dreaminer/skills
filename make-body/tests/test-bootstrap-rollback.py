#!/usr/bin/env python3
"""Inject one staged-write failure and verify bootstrap restores its baseline."""

from __future__ import annotations

import importlib.util
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
    with tempfile.TemporaryDirectory() as temporary:
        docs = Path(temporary) / "docs"
        docs.mkdir()
        baseline = {}
        for name in bootstrap.MANAGED_FILES:
            contents = f"# baseline {name}\n".encode()
            (docs / name).write_bytes(contents)
            baseline[name] = contents
        with tempfile.TemporaryDirectory() as staged:
            stage = Path(staged)
            for name, contents in baseline.items():
                (stage / name).write_bytes(contents)
            (stage / "MAKE_BODY_CODE_FACTS.md").write_bytes(b"# changed facts\n")
            (stage / "MAKE_BODY_CANDIDATES.md").write_bytes(b"# changed candidates\n")
            original_replace = bootstrap.os.replace
            calls = 0

            def fail_second_replace(source: str | Path, target: str | Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected write failure")
                original_replace(source, target)

            bootstrap.os.replace = fail_second_replace
            try:
                result, changes = bootstrap.apply(stage, docs, baseline)
            finally:
                bootstrap.os.replace = original_replace
            if result != 1 or changes:
                raise AssertionError(f"expected failed rollback apply, got result={result} changes={changes}")
            for name, contents in baseline.items():
                if (docs / name).read_bytes() != contents:
                    raise AssertionError(f"rollback did not restore {name}")
    print("OK bootstrap rollback restores the baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

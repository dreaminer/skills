#!/usr/bin/env python3
"""Verify that the Make Body bootstrap lock rejects a concurrent holder."""

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
        with bootstrap.workspace_lock(docs):
            try:
                with bootstrap.workspace_lock(docs):
                    raise AssertionError("second lock unexpectedly acquired")
            except RuntimeError as error:
                if "already running" not in str(error):
                    raise
        with bootstrap.workspace_lock(docs):
            pass
    print("OK bootstrap lock rejects concurrent execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

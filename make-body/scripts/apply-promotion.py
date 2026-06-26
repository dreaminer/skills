#!/usr/bin/env python3
"""Apply an approved Make Body preview only if its source files are unchanged."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


FILES = (
    "ESSENTIAL_DOMAIN.md",
    "ESSENTIAL_USECASE.md",
    "SYSTEM_DOMAIN.md",
    "SYSTEM_USECASE.md",
    "MAKE_BODY_CANDIDATES.md",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest(path: Path) -> tuple[str, dict[str, str], dict[str, str], dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "make-body-promotion-v1":
        raise ValueError("invalid promotion manifest")
    candidate = ""
    base: dict[str, str] = {}
    preview: dict[str, str] = {}
    evidence: dict[str, str] = {}
    for line in lines[1:]:
        parts = line.split(" ")
        if len(parts) == 2 and parts[0] == "candidate":
            candidate = parts[1]
        elif len(parts) == 3 and parts[0] in {"base", "preview"} and parts[1] in FILES:
            (base if parts[0] == "base" else preview)[parts[1]] = parts[2]
        elif line.startswith("evidence "):
            record = json.loads(line[len("evidence ") :])
            if set(record) != {"path", "sha256"} or not isinstance(record["path"], str) or not isinstance(record["sha256"], str):
                raise ValueError("invalid evidence manifest entry")
            evidence[record["path"]] = record["sha256"]
    if not candidate or set(base) != set(FILES) or set(preview) != set(FILES):
        raise ValueError("incomplete promotion manifest")
    return candidate, base, preview, evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preview_dir", type=Path)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    preview = args.preview_dir.resolve()
    root = args.project_root.resolve()
    docs = args.docs_dir.resolve()
    try:
        candidate, base, preview_hashes, evidence = read_manifest(preview / "MAKE_BODY_PROMOTION_MANIFEST")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for name in FILES:
        if not (preview / name).is_file() or not (docs / name).is_file():
            parser.error(f"missing promotion file: {name}")
        if digest(preview / name) != preview_hashes[name]:
            parser.error(f"preview was modified: {name}")
        if digest(docs / name) != base[name]:
            parser.error(f"source changed since preview: {name}; prepare a new preview")
    if not root.is_dir():
        parser.error(f"project root is not a directory: {root}")
    for relative, expected_hash in evidence.items():
        source = (root / relative).resolve()
        try:
            source.relative_to(root)
        except ValueError:
            parser.error(f"evidence source is outside project root: {relative}")
        if not source.is_file() or digest(source) != expected_hash:
            parser.error(f"evidence source changed since preview: {relative}; prepare a new preview")

    temp_paths: list[tuple[Path, Path]] = []
    try:
        for name in FILES:
            descriptor, temporary = tempfile.mkstemp(prefix=f".{name}.", dir=docs)
            with os.fdopen(descriptor, "wb") as target, (preview / name).open("rb") as source:
                shutil.copyfileobj(source, target)
            temp_paths.append((Path(temporary), docs / name))
        for temporary, destination in temp_paths:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in temp_paths:
            temporary.unlink(missing_ok=True)
    for name in FILES:
        if digest(docs / name) != preview_hashes[name]:
            print(f"write verification failed: {name}", file=sys.stderr)
            return 1
    check_body = Path(__file__).with_name("check-body.sh")
    result = subprocess.run(["sh", str(check_body), str(docs)], text=True, capture_output=True)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode
    print(f"OK -- applied approved preview for {candidate}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

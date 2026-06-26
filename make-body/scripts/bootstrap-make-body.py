#!/usr/bin/env python3
"""Initialize documents, collect facts, and seed safe System candidates for one project."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import os
import shlex
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path


EXCLUDED = {".git", "node_modules", "vendor", "build", "dist", "coverage", ".cache", ".next", ".venv", "venv", "__pycache__"}
SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".sql"}
MANAGED_FILES = (
    "ESSENTIAL_DOMAIN.md", "ESSENTIAL_USECASE.md", "SYSTEM_DOMAIN.md", "SYSTEM_USECASE.md",
    "MAKE_BODY_CODE_FACTS.md", "MAKE_BODY_COVERAGE_IGNORE.md", "MAKE_BODY_CANDIDATES.md", "MAKE_BODY_CONFLICTS.md",
    "MAKE_BODY_REJECTED.md",
)


def has_extension(root: Path, extensions: set[str]) -> bool:
    return any(path.is_file() and path.suffix in extensions and not any(part in EXCLUDED for part in path.relative_to(root).parts) for path in root.rglob("*"))


def source_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS or any(part in EXCLUDED for part in path.relative_to(root).parts):
            continue
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def has_nonempty_queue(path: Path) -> bool:
    return path.exists() and path.read_text(encoding="utf-8").strip() not in {"", "# MAKE_BODY_CANDIDATES"}


@contextmanager
def workspace_lock(docs: Path):
    digest = hashlib.sha256(str(docs).encode()).hexdigest()
    path = Path(tempfile.gettempdir()) / f"make-body-bootstrap-{digest}.lock"
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f"bootstrap already running for {docs}") from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def snapshot(path: Path) -> bytes | None:
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f"managed document is not a file: {path}")
    return path.read_bytes()


def run(command: list[str]) -> int:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        print(f"FAIL BOOTSTRAP {shlex.join(command)}", file=sys.stderr)
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
    return result.returncode


def write_atomic(target: Path, contents: bytes) -> None:
    temporary = target.with_name(f".{target.name}.bootstrap-{os.getpid()}.tmp")
    try:
        temporary.write_bytes(contents)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def rollback(docs: Path, applied: list[str], baseline: dict[str, bytes | None]) -> bool:
    try:
        for name in reversed(applied):
            target = docs / name
            if baseline[name] is None:
                target.unlink(missing_ok=True)
            else:
                write_atomic(target, baseline[name])
    except OSError as error:
        print(f"bootstrap rollback failed: {error}", file=sys.stderr)
        return False
    return True


def apply(stage: Path, docs: Path, baseline: dict[str, bytes | None]) -> tuple[int, list[tuple[str, str]]]:
    changes = [(name, (stage / name).read_bytes()) for name in MANAGED_FILES if (stage / name).read_bytes() != baseline[name]]
    for name, _ in changes:
        try:
            current = snapshot(docs / name)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 2, []
        if current != baseline[name]:
            print(f"refusing bootstrap because managed document changed: {docs / name}", file=sys.stderr)
            return 2, []
    applied: list[str] = []
    try:
        docs.mkdir(parents=True, exist_ok=True)
        for name, contents in changes:
            write_atomic(docs / name, contents)
            applied.append(name)
    except OSError as error:
        restored = rollback(docs, applied, baseline)
        outcome = "restored prior documents" if restored else "rollback incomplete"
        print(f"bootstrap apply failed: {error}; {outcome}", file=sys.stderr)
        return 1, []
    return 0, [("CREATED" if baseline[name] is None else "UPDATED", name) for name, _ in changes]


def execute_bootstrap(root: Path, docs: Path, scripts: Path, collector: str, extractor: str, require_full_coverage: bool = False) -> tuple[int, list[tuple[str, str]]]:
    facts = docs / "MAKE_BODY_CODE_FACTS.md"
    candidates = docs / "MAKE_BODY_CANDIDATES.md"
    if has_nonempty_queue(candidates):
        print(f"refusing bootstrap with non-empty candidate queue: {candidates}", file=sys.stderr)
        return 2, []
    try:
        baseline = {name: snapshot(docs / name) for name in MANAGED_FILES}
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2, []
    source = source_fingerprint(root)
    with tempfile.TemporaryDirectory(prefix="make-body-bootstrap-") as temporary:
        stage = Path(temporary) / "docs"
        stage.mkdir()
        for name, contents in baseline.items():
            if contents is not None:
                (stage / name).write_bytes(contents)
        commands = [
            [sys.executable, str(scripts / "init-docs.py"), str(stage)],
            [sys.executable, str(scripts / collector), str(root), str(stage / facts.name)],
        ]
        if require_full_coverage:
            commands.append([sys.executable, str(scripts / "report-fact-coverage.py"), str(root), str(stage / facts.name), "--ignore", str(stage / "MAKE_BODY_COVERAGE_IGNORE.md"), "--fail-on-unrepresented"])
        commands.extend((
            [sys.executable, str(scripts / extractor), str(stage / facts.name), str(stage / candidates.name)],
            [sys.executable, str(scripts / "check-workspace.py"), str(root), str(stage)],
        ))
        for command in commands:
            if result := run(command):
                return result, []
        if source_fingerprint(root) != source:
            print("refusing bootstrap because project source changed during staging", file=sys.stderr)
            return 2, []
        return apply(stage, docs, baseline)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path); parser.add_argument("docs_dir", type=Path)
    parser.add_argument("--adapter", choices=("auto", "typescript", "python", "combined"), default="auto")
    parser.add_argument("--dry-run", action="store_true", help="print the selected adapter and commands without writing files")
    parser.add_argument("--require-full-coverage", action="store_true", help="reject bootstrap when supported source lacks a fact")
    args = parser.parse_args(); root = args.project_root.resolve(); docs = args.docs_dir.resolve()
    if not root.is_dir(): parser.error(f"project root is not a directory: {root}")
    ts = has_extension(root, {".ts", ".tsx", ".js", ".jsx"}); py = has_extension(root, {".py"}); sql = has_extension(root, {".sql"})
    adapter = args.adapter
    if adapter == "auto":
        if ts and py: adapter = "combined"
        elif py: adapter = "python"
        elif ts or sql: adapter = "typescript"
        else: parser.error("no supported TypeScript, JavaScript, Python, or SQL source found")
    supported = {
        "typescript": ts or sql,
        "python": py,
        "combined": ts and py,
    }
    if not supported[adapter]:
        requirements = {
            "typescript": "TypeScript, JavaScript, or SQL source",
            "python": "Python source",
            "combined": "both TypeScript/JavaScript and Python source",
        }
        parser.error(f"adapter {adapter} requires {requirements[adapter]}")
    scripts = Path(__file__).parent
    collector = {"typescript": "collect-typescript-facts.py", "python": "collect-python-facts.py", "combined": "collect-code-facts.py"}[adapter]
    extractor = {"typescript": "extract-typescript-candidates.py", "python": "extract-python-candidates.py", "combined": "extract-code-facts-candidates.py"}[adapter]
    facts = docs / "MAKE_BODY_CODE_FACTS.md"; candidates = docs / "MAKE_BODY_CANDIDATES.md"
    if args.dry_run:
        commands = [
            [sys.executable, str(scripts / "init-docs.py"), str(docs)],
            [sys.executable, str(scripts / collector), str(root), str(facts)],
        ]
        if args.require_full_coverage:
            commands.append([sys.executable, str(scripts / "report-fact-coverage.py"), str(root), str(facts), "--ignore", str(docs / "MAKE_BODY_COVERAGE_IGNORE.md"), "--fail-on-unrepresented"])
        commands.extend((
            [sys.executable, str(scripts / extractor), str(facts), str(candidates)],
            [sys.executable, str(scripts / "check-workspace.py"), str(root), str(docs)],
        ))
        print(f"PLAN BOOTSTRAP adapter={adapter} docs={docs}")
        for command in commands:
            print(f"PLAN {shlex.join(command)}")
        return 0
    try:
        with workspace_lock(docs):
            result, changes = execute_bootstrap(root, docs, scripts, collector, extractor, args.require_full_coverage)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 2
    if result:
        return result
    print(f"OK BOOTSTRAP adapter={adapter} docs={docs}")
    for action, name in changes:
        print(f"{action} {name}")
    return 0


if __name__ == "__main__": raise SystemExit(main())

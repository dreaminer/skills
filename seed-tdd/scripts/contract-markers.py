#!/usr/bin/env python3
"""Print current Acceptance markers using seed-system's canonical hash code."""

import argparse
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def load_checker(path):
    spec = importlib.util.spec_from_file_location("seed_system_check_acceptance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load seed-system checker: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", default="docs", help="target project docs directory")
    parser.add_argument(
        "--checker",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "seed-system"
        / "scripts"
        / "check-acceptance.py",
        help="path to seed-system's canonical checker",
    )
    args = parser.parse_args()

    acceptance = Path(args.docs) / "ACCEPTANCE.md"
    if not acceptance.is_file():
        print(f"cannot run: {acceptance} not found", file=sys.stderr)
        return 2
    if not args.checker.is_file():
        print(f"cannot run: canonical checker not found at {args.checker}", file=sys.stderr)
        return 2

    try:
        checker = load_checker(args.checker)
        checker.failures.clear()
        checker.warnings.clear()
        contracts = checker.check_acceptance(acceptance)
    except (OSError, RuntimeError) as error:
        print(f"cannot run: {error}", file=sys.stderr)
        return 2

    if checker.failures:
        for failure in checker.failures:
            print(failure, file=sys.stderr)
        return 1

    for ac_id, contract in contracts.items():
        marker = f"@acceptance: {ac_id} sha256:{contract['hash']}"
        print(f"{ac_id} | {marker} | [{contract['subject']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

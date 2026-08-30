#!/usr/bin/env python3
"""Print current realization markers using seed-system's canonical hash code."""

import argparse
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def load_checker(path):
    spec = importlib.util.spec_from_file_location("seed_system_check_acceptance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load checker: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", default="docs")
    parser.add_argument("--checker")
    args = parser.parse_args()

    docs = Path(args.docs)
    proposal = docs / "SEED_SYSTEM_IMPL_PROPOSAL.md"
    checker_path = (
        Path(args.checker)
        if args.checker
        else Path(__file__).resolve().parents[2] / "seed-system" / "scripts" / "check-acceptance.py"
    )
    if not proposal.is_file() or not checker_path.is_file():
        print("cannot run: proposal or seed-system checker not found", file=sys.stderr)
        return 2

    try:
        checker = load_checker(checker_path)
        proposals = checker.check_proposals(proposal)
    except (OSError, RuntimeError, SyntaxError) as error:
        print(f"cannot run: {error}", file=sys.stderr)
        return 2
    if checker.failures:
        for line in checker.failures:
            print(line, file=sys.stderr)
        return 1

    for ip_id, item in proposals.items():
        if item["deferred"]:
            continue
        default = " ".join(checker.norm_line(x) for x in item["fields"].get("Default", []))
        print(f"{ip_id} | @realization: {ip_id} sha256:{item['hash']} | {default}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

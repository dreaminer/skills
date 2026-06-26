#!/usr/bin/env python3
"""Create missing Make Body documents without replacing existing project files."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATES = {
    "ESSENTIAL_DOMAIN.md": "# ESSENTIAL_DOMAIN\n",
    "ESSENTIAL_USECASE.md": "# ESSENTIAL_USECASE\n",
    "SYSTEM_DOMAIN.md": "# SYSTEM_DOMAIN\n",
    "SYSTEM_USECASE.md": "# SYSTEM_USECASE\n",
    "MAKE_BODY_CODE_FACTS.md": "# MAKE_BODY_CODE_FACTS\n",
    "MAKE_BODY_COVERAGE_IGNORE.md": "# MAKE_BODY_COVERAGE_IGNORE\n",
    "MAKE_BODY_CANDIDATES.md": "# MAKE_BODY_CANDIDATES\n",
    "MAKE_BODY_CONFLICTS.md": "# MAKE_BODY_CONFLICTS\n",
    "MAKE_BODY_REJECTED.md": "# MAKE_BODY_REJECTED\n",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    docs = args.docs_dir.resolve()
    docs.mkdir(parents=True, exist_ok=True)
    created = []
    preserved = []
    for name, content in TEMPLATES.items():
        target = docs / name
        if target.exists():
            preserved.append(name)
        else:
            target.write_text(content, encoding="utf-8")
            created.append(name)
    for name in created:
        print(f"CREATED {name}")
    for name in preserved:
        print(f"PRESERVED {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Create missing R6 Make Body documents without replacing existing files."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATES = {
    "ESSENTIAL_DOMAIN.md": "# ESSENTIAL_DOMAIN\n",
    "ESSENTIAL_USECASE.md": "# ESSENTIAL_USECASE\n",
    "MAKE_BODY_ESSENTIAL_HYPOTHESES.md": "# MAKE_BODY_ESSENTIAL_HYPOTHESES\n",
    "MAKE_BODY_CONFLICTS.md": "# MAKE_BODY_CONFLICTS\n",
    "MAKE_BODY_REJECTED.md": "# MAKE_BODY_REJECTED\n",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    docs = args.docs_dir.resolve()
    docs.mkdir(parents=True, exist_ok=True)
    for name, content in TEMPLATES.items():
        target = docs / name
        if target.exists():
            print(f"PRESERVED {name}")
        else:
            target.write_text(content, encoding="utf-8")
            print(f"CREATED {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

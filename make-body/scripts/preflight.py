#!/usr/bin/env python3
"""Check Make Body runtime requirements without changing project files."""

from __future__ import annotations

import shutil
import sys


MIN_VERSION = (3, 10)


def main() -> int:
    ok = True
    version = sys.version_info
    if version < MIN_VERSION:
        print(
            "FAIL python3 "
            f"{MIN_VERSION[0]}.{MIN_VERSION[1]}+ required; "
            f"found {version.major}.{version.minor}.{version.micro}",
            file=sys.stderr,
        )
        ok = False
    else:
        print(f"OK python3 {version.major}.{version.minor}.{version.micro}")

    shell = shutil.which("sh")
    if shell is None:
        print("FAIL POSIX sh not found on PATH", file=sys.stderr)
        ok = False
    else:
        print(f"OK sh {shell}")

    print("OK no third-party Python packages required")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Read rejected (Type, Subject, location) keys from MAKE_BODY_REJECTED.md.

Used by the candidate extractors to suppress re-seeding a scaffold a human has
explicitly rejected, and by check-rejected.py to flag a resurrected candidate.
An absent archive suppresses nothing (returns an empty set).
"""

from __future__ import annotations

import re
from pathlib import Path


RECORD = re.compile(r"^## (MR-\d{3,})\s*$")
FIELD = re.compile(r"^(Type|Subject|Reason|Evidence|Replacement):\s*(.*)$")
LOCATION = re.compile(r"^- `([^`]+:\d+)`")


def rejected_keys(rejected_path: Path) -> set[tuple[str, str, str]]:
    """Return {(candidate_type, subject, "path:line")} for every rejected record.

    Each record contributes one key per Evidence pointer it cites. A record with
    no Type, Subject, or Evidence pointer contributes nothing.
    """
    keys: set[tuple[str, str, str]] = set()
    if not rejected_path.is_file():
        return keys

    section = ""
    ctype = ""
    subject = ""
    locations: list[str] = []

    def flush() -> None:
        for location in locations:
            if ctype and subject:
                keys.add((ctype, subject, location))

    for raw in rejected_path.read_text(encoding="utf-8").splitlines():
        if RECORD.match(raw):
            flush()
            section, ctype, subject, locations = "", "", "", []
            continue
        match = FIELD.match(raw)
        if match:
            section, inline = match.groups()
            inline = inline.strip()
            if section == "Type" and inline:
                ctype = inline
            elif section == "Subject" and inline:
                subject = inline
            elif section == "Evidence":
                pointer = LOCATION.match(inline)
                if pointer:
                    locations.append(pointer.group(1))
            continue
        body = raw.strip()
        if not body:
            continue
        if section == "Type" and not ctype:
            ctype = body
        elif section == "Subject" and not subject:
            subject = body
        elif section == "Evidence":
            pointer = LOCATION.match(body)
            if pointer:
                locations.append(pointer.group(1))
    flush()
    return keys

#!/usr/bin/env python3
"""Mechanical verifier for seed-system output documents.

Checks structure, hash-marker linkage, and coverage of ACCEPTANCE.md and
SEED_SYSTEM_TESTS.md. Implements the canonical contract-hash computation
defined in references/artifacts.md and is its executable reference.

It does NOT judge semantics: whether an AC faithfully completes an Essential
use case, or whether a test faithfully asserts a Then, stays a human/agent duty.

Usage:
    python3 check-acceptance.py [--docs DIR] [--complete]

  --docs DIR    project docs directory (default: docs)
  --complete    additionally require every AC record to be green
                (completion audit; without it red/gap are legitimate states)

Exit codes: 0 = no failures, 1 = failures reported, 2 = cannot run.
"""

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

AC_ID_RE = re.compile(r"^AC-\d{3,}$")
MARKER_RE = re.compile(r"@acceptance:\s*(AC-\d{3,})\s+sha256:([0-9a-f]{64})")
FIELD_NAMES = ("ID", "Basis", "Seam", "Given", "When", "Then", "Evidence")
HASH_FIELDS = ("Seam", "Given", "When", "Then")  # plus ID and Subject, see contract_hash
BASIS_VALUES = {"inherited", "proposed"}
LAYER_VALUES = {"unit", "integration", "browser", "observability"}
TEST_FIELD_NAMES = ("Acceptance", "Risk", "Layer", "Status", "Test", "Marker", "Notes")

failures = []
warnings = []


def fail(check, msg):
    failures.append(f"FAIL [{check}] {msg}")


def warn(check, msg):
    warnings.append(f"WARN [{check}] {msg}")


def parse_sections(text, field_names):
    """Split a document on '## ' headers; parse 'Field:' blocks inside each."""
    sections = []
    current = None
    field = None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^## (.+)$", line)
        if m:
            current = {"_subject_raw": m.group(1).strip(), "_fields": {}, "_order": []}
            sections.append(current)
            field = None
            continue
        if current is None:
            continue
        fm = re.match(r"^([A-Za-z]+):\s*$", line)
        if fm and fm.group(1) in field_names:
            field = fm.group(1)
            current["_fields"].setdefault(field, [])
            current["_order"].append(field)
            continue
        if field is not None and line.strip():
            current["_fields"][field].append(line.strip())
    return sections


def norm_line(line):
    line = re.sub(r"^- ", "", line).strip()
    return re.sub(r"\s+", " ", line)


def contract_hash(subject, fields):
    parts = ["ID"] + [norm_line(x) for x in fields.get("ID", [])]
    parts += ["Subject", norm_line(subject)]
    for name in HASH_FIELDS:
        parts.append(name)
        parts += [norm_line(x) for x in fields.get(name, []) if norm_line(x)]
    payload = unicodedata.normalize("NFC", "\n".join(parts)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def subject_of(section):
    m = re.match(r"^\[(.+)\]$", section["_subject_raw"])
    return m.group(1) if m else None


def check_acceptance(path):
    text = path.read_text(encoding="utf-8")
    if re.search(r"\{[^}\s][^}]*\}", text):
        fail("canonical", f"{path.name} contains unratified '{{term}}' markers")
    for label in ("[assumption]", "[conflict]", "[unclassified-layer]", "[deferred]"):
        if label in text:
            fail("canonical", f"{path.name} contains queue label {label}")

    acs = {}
    for sec in parse_sections(text, FIELD_NAMES):
        subject = subject_of(sec)
        if subject is None:
            fail("structure", f"header '## {sec['_subject_raw']}' is not '## [Subject]' form")
            continue
        f = sec["_fields"]
        ac_id = (f.get("ID") or [""])[0]
        label = ac_id or f"[{subject}]"
        if not AC_ID_RE.match(ac_id):
            fail("structure", f"{label}: ID missing or not AC-nnn form")
        elif ac_id in acs:
            fail("structure", f"{ac_id}: duplicate ID")
        for name in FIELD_NAMES:
            if not f.get(name):
                fail("structure", f"{label}: missing or empty field '{name}'")
        basis = norm_line((f.get("Basis") or [""])[0])
        if basis and basis not in BASIS_VALUES:
            fail("structure", f"{label}: Basis '{basis}' not in {sorted(BASIS_VALUES)}")
        if AC_ID_RE.match(ac_id):
            acs[ac_id] = {
                "subject": subject,
                "fields": f,
                "hash": contract_hash(subject, f),
            }
    if not acs:
        fail("structure", f"{path.name} contains no parseable AC scenarios")
    return acs


def check_tests(path, acs, complete):
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^Test command:\s*$", text, re.M):
        fail("tests", f"{path.name}: 'Test command:' not declared")
    test_dir = None
    dm = re.search(r"^Test directory:\s*\n-\s*(.+)$", text, re.M)
    if dm:
        test_dir = dm.group(1).strip()
    else:
        fail("tests", f"{path.name}: 'Test directory:' not declared")

    seen = {}
    for sec in parse_sections(text, TEST_FIELD_NAMES):
        f = sec["_fields"]
        rec = sec["_subject_raw"]
        ac_id = norm_line((f.get("Acceptance") or [""])[0])
        if not ac_id:
            fail("tests", f"{rec}: missing Acceptance reference")
            continue
        if ac_id not in acs:
            fail("tests", f"{rec}: references unknown {ac_id}")
            continue
        if ac_id in seen:
            fail("tests", f"{rec}: duplicate record for {ac_id}")
        seen[ac_id] = True

        for name in ("Risk", "Layer"):
            if not f.get(name):
                fail("tests", f"{rec} ({ac_id}): missing '{name}'")
        layer = norm_line((f.get("Layer") or [""])[0])
        if layer and layer not in LAYER_VALUES:
            fail("tests", f"{rec} ({ac_id}): Layer '{layer}' not in {sorted(LAYER_VALUES)}")

        status = norm_line((f.get("Status") or [""])[0])
        is_gap = status.startswith("gap —") or status.startswith("gap -")
        if status not in ("red", "green") and not is_gap:
            fail("tests", f"{rec} ({ac_id}): Status '{status}' not red/green/'gap — <reason>'")
            continue
        if complete and status != "green":
            fail("complete", f"{ac_id}: status '{status}' — completion requires green")
        if is_gap:
            continue

        test_path = norm_line((f.get("Test") or [""])[0])
        marker = " ".join(norm_line(x) for x in f.get("Marker") or [])
        if not test_path:
            fail("tests", f"{rec} ({ac_id}): {status} record without Test path")
        mm = MARKER_RE.search(marker)
        if not mm:
            fail("tests", f"{rec} ({ac_id}): {status} record without valid @acceptance marker")
            continue
        if mm.group(1) != ac_id:
            fail("linkage", f"{rec}: marker names {mm.group(1)} but record is for {ac_id}")
        if mm.group(2) != acs[ac_id]["hash"]:
            fail("linkage", f"{ac_id}: marker hash is stale (contract changed; relink required)")
        if test_path:
            tp = Path(test_path)
            if not tp.exists():
                fail("linkage", f"{ac_id}: test file '{test_path}' does not exist")
            elif f"sha256:{acs[ac_id]['hash']}" not in tp.read_text(encoding="utf-8"):
                fail("linkage", f"{ac_id}: '{test_path}' lacks a marker with the current hash")

    for ac_id in acs:
        if ac_id not in seen:
            fail("tests", f"{ac_id}: no lifecycle record in {path.name}")
    return test_dir


def check_coverage(euc_path, acs):
    subjects = []
    for sec in parse_sections(euc_path.read_text(encoding="utf-8"), ()):
        s = subject_of(sec)
        if s:
            subjects.append(s)
    for subject in subjects:
        covered = False
        for ac in acs.values():
            for line in ac["fields"].get("Evidence", []):
                if "ESSENTIAL_USECASE" in line and subject in line:
                    covered = True
        if not covered:
            fail("coverage", f"inherited use case '[{subject}]' is named in no AC Evidence")
    known = set(subjects)
    for ac_id, ac in acs.items():
        for line in ac["fields"].get("Evidence", []):
            m = re.search(r"ESSENTIAL_USECASE\s*#\d+\s*\(([^)]+)\)", line)
            if m and m.group(1).strip() not in known:
                warn("coverage", f"{ac_id}: names unknown use case '({m.group(1).strip()})' — subject governs")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--complete", action="store_true")
    args = ap.parse_args()
    docs = Path(args.docs)

    acceptance = docs / "ACCEPTANCE.md"
    if not acceptance.exists():
        print(f"cannot run: {acceptance} not found", file=sys.stderr)
        return 2

    for legacy in ("SYSTEM_DOMAIN.md", "SYSTEM_USECASE.md"):
        if (docs / legacy).exists():
            fail("mixed-mode", f"{legacy} coexists with ACCEPTANCE.md — route it through human review")

    acs = check_acceptance(acceptance)

    tests = docs / "SEED_SYSTEM_TESTS.md"
    if tests.exists():
        check_tests(tests, acs, args.complete)
    else:
        fail("tests", "SEED_SYSTEM_TESTS.md not found — every AC needs a lifecycle record")

    euc = docs / "ESSENTIAL_USECASE.md"
    if euc.exists():
        check_coverage(euc, acs)

    for line in warnings:
        print(line)
    for line in failures:
        print(line)
    print(f"checked {len(acs)} AC(s): {len(failures)} failure(s), {len(warnings)} warning(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

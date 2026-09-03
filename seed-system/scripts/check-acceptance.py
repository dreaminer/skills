#!/usr/bin/env python3
"""Mechanical verifier for seed-system output documents.

Checks Acceptance and implementation-proposal structure, lifecycle linkage,
artifact-definition links, Essential coverage, and delivery closure. Implements the canonical
Acceptance and realization hash computations defined in references/artifacts.md
and is their executable reference.

It does NOT judge semantics: whether an AC faithfully completes an Essential
use case, whether a Closes test traverses a supported delivery path, whether a
test faithfully asserts a Then, or whether realization evidence proves the
selected Default stays a human/agent duty.

Usage:
    python3 check-acceptance.py [--docs DIR] [--complete [SCOPE] | --links-only]

  --docs DIR    project docs directory (default: docs)
  --complete acceptance   require current-hash GREEN ACs, Essential coverage, and closure
  --complete realization  require every non-deferred IP to be verified
  --complete all          require both axes (plain --complete means all)

Exit codes: 0 = no failures, 1 = failures reported, 2 = cannot run.
"""

import argparse
import hashlib
import re
import string
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

AC_ID_RE = re.compile(r"^AC-\d{3,}$")
MARKER_RE = re.compile(r"@acceptance:\s*(AC-\d{3,})\s+sha256:([0-9a-f]{64})")
IP_ID_RE = re.compile(r"^IP-\d{3,}$")
IP_LINK_RE = re.compile(
    r"\[([^\]\n]*\b(IP-\d{3,})\b[^\]\n]*)\]\(\s*"
    r"(?:<([^>\n]+)>|([^\s)]+))\s*\)"
)
REALIZATION_MARKER_RE = re.compile(
    r"@realization:\s*(IP-\d{3,})\s+sha256:([0-9a-f]{64})"
)
FIELD_NAMES = ("ID", "Basis", "Seam", "Given", "When", "Then", "Closes", "Evidence")
REQUIRED_FIELD_NAMES = ("ID", "Basis", "Seam", "Given", "When", "Then", "Evidence")
HASH_FIELDS = ("Seam", "Given", "When", "Then")  # plus ID, Subject, and semantic Closes subjects
BASIS_VALUES = {"inherited", "proposed"}
LAYER_VALUES = {"unit", "integration", "browser", "observability"}
TEST_FIELD_NAMES = ("Acceptance", "Risk", "Layer", "Status", "Test", "Marker", "Notes")
PROPOSAL_FIELD_NAMES = (
    "Area",
    "Default",
    "Why",
    "Alternatives",
    "Status",
    "Deferred values",
)
REALIZATION_FIELD_NAMES = ("Proposal", "Status", "Marker", "Evidence", "Notes")
REALIZATION_PATH_KINDS = {
    "artifact",
    "code",
    "config",
    "integration",
    "migration",
    "deployment",
}
MATERIALIZED_SEED_FILES = frozenset(
    {
        "ESSENTIAL_DOMAIN.md",
        "ESSENTIAL_USECASE.md",
        "SEED_BODY_SYSTEM_PARKING.md",
        "SEED_BODY_LATER.md",
        "SEED_BODY_QUESTIONS.md",
        "SEED_BODY_CRITERIA.md",
        "SEED_BODY_REJECTED.md",
        "ACCEPTANCE.md",
        "SEED_SYSTEM_TESTS.md",
        "SEED_SYSTEM_IMPL_PROPOSAL.md",
        "SEED_SYSTEM_NOTES.md",
    }
)
ARTIFACT_LINK_RE = re.compile(
    r"(?<!!)\[([^\]\n]+)\]\(\s*(?:<([^>\n]+)>|([^\s)]+))\s*\)"
)
ESSENTIAL_USECASE_LABEL_RE = re.compile(
    r"^ESSENTIAL_USECASE\s*#\d+\s*\((.+)\)$"
)
FIELD_HEADER_RE = re.compile(r"^([A-Za-z][A-Za-z ]*):(?:\s*(.*))?$")
POINTER_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(?:"
    r"ESSENTIAL_USECASE(?:\s*#\d+(?:\s*,\s*#?\d+)*(?:\s*\([^)]+\))?)?"
    r"|(?:AC|SF|IP)-\d{3,})(?![A-Za-z0-9_-])"
)
SCRATCH_EF_RE = re.compile(r"(?<![A-Za-z0-9_-])EF-\d{3,}(?![A-Za-z0-9_-])")
REFERENCE_FIELDS = {
    "SEED_BODY_SYSTEM_PARKING.md": frozenset({"Trace"}),
    "ACCEPTANCE.md": frozenset({"Closes", "Evidence"}),
    "SEED_SYSTEM_TESTS.md": frozenset({"Proposal"}),
    "SEED_SYSTEM_IMPL_PROPOSAL.md": frozenset({"Why"}),
}

failures = []
warnings = []


def fail(check, msg):
    failures.append(f"FAIL [{check}] {msg}")


def warn(check, msg):
    warnings.append(f"WARN [{check}] {msg}")


def unfenced_lines(text):
    """Yield (line number, line) outside Markdown fenced code blocks."""
    fence_char = None
    fence_len = 0
    for line_no, line in enumerate(text.splitlines(), 1):
        opening = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", line)
        if fence_char is None:
            if opening:
                fence_char = opening.group(1)[0]
                fence_len = len(opening.group(1))
                continue
            yield line_no, line
            continue

        closing = re.match(
            rf"^[ \t]{{0,3}}{re.escape(fence_char)}{{{fence_len},}}[ \t]*$", line
        )
        if closing:
            fence_char = None
            fence_len = 0


def gfm_heading_slug(heading):
    """Return the GFM-style slug used by materialized Seed headings."""
    value = unicodedata.normalize("NFC", heading.strip()).lower()
    ascii_punctuation = set(string.punctuation) - {"-", "_"}
    value = "".join(
        ch
        for ch in value
        if ch not in ascii_punctuation
        and (ch in "-_" or not unicodedata.category(ch).startswith("P"))
    )
    return re.sub(r"\s", "-", value)


def heading_anchor_index(path):
    """Index existing level-two headings, including GFM duplicate suffixes."""
    anchors = set()
    for _line_no, line in unfenced_lines(path.read_text(encoding="utf-8")):
        match = re.match(r"^##[ \t]+(.+?)[ \t]*$", line)
        if not match:
            continue
        heading = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(1))
        base = gfm_heading_slug(heading)
        anchor = base
        suffix = 0
        while anchor in anchors:
            suffix += 1
            anchor = f"{base}-{suffix}"
        anchors.add(anchor)
    return anchors


def reference_blocks(path):
    """Return only the schema slots allowed to carry Seed artifact links."""
    text = path.read_text(encoding="utf-8")
    if path.name == "SEED_BODY_CRITERIA.md":
        blocks = []
        context = None
        buffer = []
        for line_no, line in unfenced_lines(text):
            if "→" in line:
                if buffer:
                    blocks.append((context, "\n".join(buffer)))
                context = f"line {line_no}"
                buffer = [line]
            elif buffer and line[:1].isspace() and line.strip():
                buffer.append(line)
            elif buffer:
                blocks.append((context, "\n".join(buffer)))
                context = None
                buffer = []
        if buffer:
            blocks.append((context, "\n".join(buffer)))
        return blocks

    selected_fields = REFERENCE_FIELDS.get(path.name)
    if not selected_fields:
        return []

    blocks = []
    subject = "document"
    field = None
    buffer = []

    def flush():
        nonlocal buffer
        if field in selected_fields and buffer:
            blocks.append((f"{subject} {field}", "\n".join(buffer)))
        buffer = []

    for _line_no, line in unfenced_lines(text):
        heading = re.match(r"^##[ \t]+(.+?)\s*$", line)
        if heading:
            flush()
            subject = heading.group(1).strip()
            field = None
            continue

        header = FIELD_HEADER_RE.match(line)
        if header:
            flush()
            field = header.group(1) if header.group(1) in selected_fields else None
            if field is not None and header.group(2):
                buffer.append(header.group(2))
            continue

        if field is not None and line.strip():
            buffer.append(line)

    flush()
    return blocks


def check_artifact_links(docs):
    """Check explicit Seed definition links without touching parsed/hash fields."""
    docs_root = docs.resolve()
    known_targets = {}
    for filename in MATERIALIZED_SEED_FILES:
        target = docs / filename
        resolved = target.resolve()
        known_targets[resolved] = target

    sources = [docs / "SEED_BODY_CRITERIA.md"]
    sources.extend(docs / filename for filename in REFERENCE_FIELDS)
    for source in sources:
        if not source.is_file():
            continue
        for context, block in reference_blocks(source):
            definition_link_spans = []
            for link in ARTIFACT_LINK_RE.finditer(block):
                destination = link.group(2) or link.group(3)
                try:
                    parsed = urlsplit(destination)
                    decoded_path = unquote(parsed.path, errors="strict")
                except (UnicodeDecodeError, ValueError):
                    if POINTER_RE.search(link.group(1)):
                        definition_link_spans.append(link.span())
                        fail(
                            "artifact-link",
                            f"{source.name} {context}: invalid encoded destination: '{destination}'",
                        )
                    continue

                # External links and links to non-Seed documents are outside this contract.
                if parsed.scheme or parsed.netloc:
                    continue
                target_name = Path(decoded_path).name if decoded_path else source.name
                is_definition_link = (
                    target_name in MATERIALIZED_SEED_FILES
                    or POINTER_RE.search(link.group(1)) is not None
                )
                if not is_definition_link:
                    continue

                definition_link_spans.append(link.span())
                if target_name not in MATERIALIZED_SEED_FILES:
                    fail(
                        "artifact-link",
                        f"{source.name} {context}: materialized target not found: '{destination}'",
                    )
                    continue
                target = (source.parent / decoded_path).resolve() if decoded_path else source.resolve()
                try:
                    target.relative_to(docs_root)
                except ValueError:
                    fail(
                        "artifact-link",
                        f"{source.name} {context}: target escapes docs: '{destination}'",
                    )
                    continue

                declared_target = known_targets.get(target)
                if declared_target is None or not declared_target.is_file():
                    fail(
                        "artifact-link",
                        f"{source.name} {context}: materialized target not found: '{destination}'",
                    )
                    continue
                if not parsed.fragment:
                    fail(
                        "artifact-link",
                        f"{source.name} {context}: definition link has no ## fragment: '{destination}'",
                    )
                    continue
                try:
                    fragment = unicodedata.normalize(
                        "NFC", unquote(parsed.fragment, errors="strict")
                    )
                except UnicodeDecodeError:
                    fail(
                        "artifact-link",
                        f"{source.name} {context}: invalid encoded fragment: '{destination}'",
                    )
                    continue
                if fragment not in heading_anchor_index(declared_target):
                    fail(
                        "artifact-link",
                        f"{source.name} {context}: ## fragment '#{fragment}' not found in {declared_target.name}",
                    )

            for pointer in POINTER_RE.finditer(block):
                if any(start <= pointer.start() and pointer.end() <= end for start, end in definition_link_spans):
                    continue
                warn(
                    "link-format",
                    f"{source.name} {context}: bare pointer '{pointer.group(0)}' should be an inline definition link",
                )
            if source.name == "SEED_BODY_SYSTEM_PARKING.md" and not definition_link_spans:
                for pointer in SCRATCH_EF_RE.finditer(block):
                    warn(
                        "link-format",
                        f"{source.name} {context}: scratch pointer '{pointer.group(0)}' cannot be the sole Trace",
                    )


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
        fm = re.match(r"^([A-Za-z][A-Za-z ]*):\s*$", line)
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


def essential_usecase_subjects_in_links(line):
    """Yield subjects from valid Essential definition-link labels in one line."""
    for link in ARTIFACT_LINK_RE.finditer(line):
        label = ESSENTIAL_USECASE_LABEL_RE.fullmatch(link.group(1).strip())
        if label:
            yield label.group(1).strip()


def exact_essential_usecase_link_subject(line):
    """Return the subject when the whole line is one Essential definition link."""
    link = ARTIFACT_LINK_RE.fullmatch(norm_line(line))
    if not link:
        return None
    label = ESSENTIAL_USECASE_LABEL_RE.fullmatch(link.group(1).strip())
    return label.group(1).strip() if label else None


def contract_hash(subject, fields):
    parts = ["ID"] + [norm_line(x) for x in fields.get("ID", [])]
    parts += ["Subject", norm_line(subject)]
    for name in HASH_FIELDS:
        values = [norm_line(x) for x in fields.get(name, []) if norm_line(x)]
        if not values:
            continue
        parts.append(name)
        parts += values
    closes_subjects = sorted(
        {
            unicodedata.normalize("NFC", norm_line(subject))
            for line in fields.get("Closes", [])
            if (subject := exact_essential_usecase_link_subject(line))
        }
    )
    if closes_subjects:
        parts.append("Closes")
        parts += closes_subjects
    payload = unicodedata.normalize("NFC", "\n".join(parts)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def proposal_hash(ip_id, fields):
    """Hash only the selected implementation choice, not its rationale."""
    parts = ["ID", ip_id, "Default"]
    parts += [norm_line(x) for x in fields.get("Default", []) if norm_line(x)]
    payload = unicodedata.normalize("NFC", "\n".join(parts)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def proposal_status(fields):
    return norm_line((fields.get("Status") or [""])[0])


def is_deferred_proposal(fields):
    return proposal_status(fields).lower().startswith("deferred")


def check_proposals(path):
    """Return the closed-world set of ratified implementation proposals."""
    proposals = {}
    for sec in parse_sections(path.read_text(encoding="utf-8"), PROPOSAL_FIELD_NAMES):
        ip_id = sec["_subject_raw"]
        fields = sec["_fields"]
        if not IP_ID_RE.match(ip_id):
            fail("proposal", f"header '## {ip_id}' is not IP-nnn form")
            continue
        if ip_id in proposals:
            fail("proposal", f"{ip_id}: duplicate proposal")
            continue
        for name in PROPOSAL_FIELD_NAMES:
            if not fields.get(name):
                fail("proposal", f"{ip_id}: missing or empty field '{name}'")
        status = proposal_status(fields).lower()
        if not (
            status.startswith("accepted")
            or status.startswith("changed")
            or status.startswith("alternative accepted")
            or status.startswith("deferred")
        ):
            fail("proposal", f"{ip_id}: unsupported Status '{proposal_status(fields)}'")
        proposals[ip_id] = {
            "fields": fields,
            "hash": proposal_hash(ip_id, fields),
            "deferred": is_deferred_proposal(fields),
        }
    if not proposals:
        fail("proposal", f"{path.name} contains no parseable IP proposals")
    return proposals


def proposal_id_from_link(value):
    match = IP_LINK_RE.search(value)
    if not match:
        return None
    ip_id = match.group(2)
    destination = match.group(3) or match.group(4)
    try:
        parsed = urlsplit(destination)
        target_name = Path(unquote(parsed.path, errors="strict")).name
        fragment = unicodedata.normalize("NFC", unquote(parsed.fragment, errors="strict"))
    except (UnicodeDecodeError, ValueError):
        return None
    if target_name != "SEED_SYSTEM_IMPL_PROPOSAL.md" or fragment != gfm_heading_slug(ip_id):
        return None
    return ip_id


def check_realizations(path, proposals, complete):
    """Validate optional IP lifecycle records stored beside AC lifecycle records."""
    seen = {}
    text = path.read_text(encoding="utf-8")
    for sec in parse_sections(text, REALIZATION_FIELD_NAMES):
        fields = sec["_fields"]
        if not fields.get("Proposal"):
            if IP_ID_RE.match(sec["_subject_raw"]):
                fail("realization", f"{sec['_subject_raw']}: missing Proposal definition link")
            continue
        rec = sec["_subject_raw"]
        proposal_value = " ".join(norm_line(x) for x in fields["Proposal"])
        ip_id = proposal_id_from_link(proposal_value)
        if not ip_id:
            fail(
                "realization",
                f"{rec}: Proposal must link an IP-nnn definition in SEED_SYSTEM_IMPL_PROPOSAL.md",
            )
            continue
        if rec != ip_id:
            fail("realization", f"{rec}: realization heading must be '## {ip_id}'")
        if ip_id not in proposals:
            fail("realization", f"{rec}: references unknown {ip_id}")
            continue
        if proposals[ip_id]["deferred"]:
            fail("realization", f"{rec}: {ip_id} is deferred and must not have a lifecycle record")
            continue
        if ip_id in seen:
            fail("realization", f"{rec}: duplicate realization record for {ip_id}")
            continue
        seen[ip_id] = True

        status = norm_line((fields.get("Status") or [""])[0])
        if status not in {"pending", "verified"}:
            fail("realization", f"{rec} ({ip_id}): Status must be pending or verified")
            continue
        if status == "pending":
            if fields.get("Marker") or fields.get("Evidence"):
                fail("realization", f"{rec} ({ip_id}): pending record must omit Marker and Evidence")
            if complete:
                fail("complete-realization", f"{ip_id}: status pending — completion requires verified")
            continue

        marker = " ".join(norm_line(x) for x in fields.get("Marker") or [])
        marker_match = REALIZATION_MARKER_RE.search(marker)
        if not marker_match:
            fail("realization", f"{rec} ({ip_id}): verified record lacks valid @realization marker")
        else:
            if marker_match.group(1) != ip_id:
                fail("realization", f"{rec}: marker names {marker_match.group(1)} but record is for {ip_id}")
            if marker_match.group(2) != proposals[ip_id]["hash"]:
                fail("realization", f"{ip_id}: realization marker stale (Default changed; reverify required)")

        evidence = [norm_line(x) for x in fields.get("Evidence") or []]
        paths = []
        commands = []
        for item in evidence:
            match = re.match(r"^([a-z]+):\s*(.+)$", item)
            if not match:
                fail("realization", f"{rec} ({ip_id}): malformed Evidence '{item}'")
                continue
            kind, value = match.groups()
            if kind in REALIZATION_PATH_KINDS:
                paths.append((kind, value))
            elif kind == "command":
                commands.append(value)
            else:
                fail("realization", f"{rec} ({ip_id}): unsupported Evidence kind '{kind}'")
        if not paths:
            fail("realization", f"{rec} ({ip_id}): verified record needs artifact-path Evidence")
        if not commands:
            fail("realization", f"{rec} ({ip_id}): verified record needs command Evidence")
        for command in commands:
            if not re.search(r"\(exit\s+0\)\s*$", command):
                fail(
                    "realization",
                    f"{rec} ({ip_id}): command Evidence must record an observed '(exit 0)'",
                )
        for kind, value in paths:
            evidence_path = Path(value)
            if evidence_path.is_absolute() or ".." in evidence_path.parts:
                fail("realization", f"{ip_id}: {kind} Evidence must be a project-relative path: '{value}'")
            elif not evidence_path.exists():
                fail("realization", f"{ip_id}: {kind} Evidence path does not exist: '{value}'")

    if complete:
        for ip_id, proposal in proposals.items():
            if not proposal["deferred"] and ip_id not in seen:
                fail("complete-realization", f"{ip_id}: no realization record — completion requires verified")
    return seen


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
        for name in REQUIRED_FIELD_NAMES:
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
        if IP_ID_RE.match(rec):
            continue
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


def check_coverage(euc_path, acs, complete):
    subjects = []
    for sec in parse_sections(euc_path.read_text(encoding="utf-8"), ()):
        s = subject_of(sec)
        if s:
            subjects.append(s)
    if not subjects:
        message = f"{euc_path.name} contains no parseable '## [Subject]' use cases"
        if complete:
            fail("coverage", f"{message} — completion requires an Essential inventory")
        else:
            warn("coverage", f"{message} — delivery closure cannot be designed")
        return

    known = set(subjects)
    closed_by = {subject: [] for subject in subjects}
    evidence_by_ac = {}
    for ac_id, ac in acs.items():
        evidence_subjects = set()
        for line in ac["fields"].get("Evidence", []):
            evidence_subjects.update(essential_usecase_subjects_in_links(line))
        evidence_by_ac[ac_id] = evidence_subjects
        for line in ac["fields"].get("Closes", []):
            subject = exact_essential_usecase_link_subject(line)
            if subject is None:
                fail(
                    "closure",
                    f"{ac_id}: Closes entry must be one exact ESSENTIAL_USECASE definition link",
                )
                continue
            if subject not in known:
                fail("closure", f"{ac_id}: Closes names unknown use case '({subject})'")
                continue
            if subject not in evidence_subjects:
                fail(
                    "closure",
                    f"{ac_id}: Closes '({subject})' but Evidence does not link that use case",
                )
                continue
            closed_by[subject].append(ac_id)

    for subject in subjects:
        covered = any(subject in evidence for evidence in evidence_by_ac.values())
        if not covered:
            # Mid-design an uncovered use case is a question, not a blocker: it may be
            # deliberately deferred from v1. Only the completion audit demands coverage.
            if complete:
                fail("coverage", f"inherited use case '[{subject}]' is named in no AC Evidence")
            else:
                warn("coverage", f"inherited use case '[{subject}]' is named in no AC Evidence — deferred from v1, or still missing?")

        if not closed_by[subject]:
            message = f"inherited use case '[{subject}]' is named in no AC Closes"
            if complete:
                fail("closure", f"{message} — completion requires supported-entry proof")
            else:
                warn("closure", f"{message} — delivery closure still missing?")

    for ac_id, evidence_subjects in evidence_by_ac.items():
        for subject in evidence_subjects:
            if subject not in known:
                warn("coverage", f"{ac_id}: names unknown use case '({subject})' — subject governs")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docs", default="docs")
    ap.add_argument(
        "--complete",
        nargs="?",
        const="all",
        choices=("acceptance", "realization", "all"),
        help="require acceptance, realization, or aggregate completion",
    )
    ap.add_argument("--links-only", action="store_true")
    args = ap.parse_args()
    docs = Path(args.docs)

    if args.complete and args.links_only:
        ap.error("--complete and --links-only are mutually exclusive")
    if not docs.is_dir():
        print(f"cannot run: {docs} is not a directory", file=sys.stderr)
        return 2

    if args.links_only:
        check_artifact_links(docs)
        for line in warnings:
            print(line)
        for line in failures:
            print(line)
        print(
            f"checked artifact links: {len(failures)} failure(s), "
            f"{len(warnings)} warning(s)"
        )
        return 1 if failures else 0

    acceptance = docs / "ACCEPTANCE.md"
    if not acceptance.exists():
        print(f"cannot run: {acceptance} not found", file=sys.stderr)
        return 2

    for legacy in ("SYSTEM_DOMAIN.md", "SYSTEM_USECASE.md"):
        if (docs / legacy).exists():
            fail("mixed-mode", f"{legacy} coexists with ACCEPTANCE.md — route it through human review")

    acceptance_complete = args.complete in {"acceptance", "all"}
    realization_complete = args.complete in {"realization", "all"}

    acs = check_acceptance(acceptance)
    check_artifact_links(docs)

    tests = docs / "SEED_SYSTEM_TESTS.md"
    if tests.exists():
        check_tests(tests, acs, acceptance_complete)
    else:
        fail("tests", "SEED_SYSTEM_TESTS.md not found — every AC needs a lifecycle record")

    euc = docs / "ESSENTIAL_USECASE.md"
    if euc.exists():
        check_coverage(euc, acs, acceptance_complete)
    elif acceptance_complete:
        fail(
            "coverage",
            "ESSENTIAL_USECASE.md not found — completion requires an Essential inventory and delivery closure",
        )
    else:
        warn(
            "coverage",
            "ESSENTIAL_USECASE.md not found — route through seed-body before designing delivery closure",
        )

    proposals = {}
    proposal_path = docs / "SEED_SYSTEM_IMPL_PROPOSAL.md"
    if proposal_path.exists():
        proposals = check_proposals(proposal_path)
        if tests.exists():
            check_realizations(tests, proposals, realization_complete)
    else:
        fail("proposal", "SEED_SYSTEM_IMPL_PROPOSAL.md not found — implementation choices are not closed")

    for line in warnings:
        print(line)
    for line in failures:
        print(line)
    non_deferred = sum(not proposal["deferred"] for proposal in proposals.values())
    print(
        f"checked {len(acs)} AC(s), {non_deferred} non-deferred IP(s): "
        f"{len(failures)} failure(s), {len(warnings)} warning(s)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

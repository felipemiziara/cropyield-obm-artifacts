#!/usr/bin/env python3
"""AGROVOC Ontology Audit Script (Replication Package).

Verifies that all AGROVOC concept codes (c_XXXX) referenced in the executable
metamodel files (models/*.use, models/*.soil) are registered in the canonical
ontological anchor registry (models/agrovoc_anchors.csv). Optionally validates
the registry against a local FAO AGROVOC SKOS-XL CSV dump if provided via --dump.

Exit codes:
  0 - All AGROVOC anchors and model references are valid.
  1 - Missing or inconsistent AGROVOC code detected.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANCHORS_CSV = ROOT / "models" / "agrovoc_anchors.csv"
SCAN_TARGETS = [
    ROOT / "models" / "cropyield.use",
    ROOT / "models" / "scenarios.soil",
]

CODE_RE = re.compile(r"\bc_(\d+)\b")


def load_anchors() -> dict[str, dict[str, str]]:
    with ANCHORS_CSV.open(newline="", encoding="utf-8") as fh:
        return {row["code"]: row for row in csv.DictReader(fh)}


def load_agrovoc_dump(dump_path: pathlib.Path) -> dict[str, tuple[str, str]]:
    uri_re = re.compile(r"http://aims\.fao\.org/aos/agrovoc/(c_\d+)")
    index: dict[str, tuple[str, str]] = {}
    with dump_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for row in reader:
            if not row:
                continue
            m = uri_re.search(row[0])
            if m:
                index[m.group(1)] = (
                    row[2] if len(row) > 2 else "",
                    row[24] if len(row) > 24 else "",
                )
    return index


def scan_files(anchors: dict[str, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for target in SCAN_TARGETS:
        if not target.exists():
            errors.append(f"[ERROR] Missing expected model file: {target.relative_to(ROOT)}")
            continue
        text = target.read_text(encoding="utf-8", errors="ignore")
        for match in CODE_RE.finditer(text):
            code = f"c_{match.group(1)}"
            if code not in anchors:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{target.relative_to(ROOT)}:{line}: code {code} not registered in models/agrovoc_anchors.csv"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AGROVOC ontological anchors across OBM artifacts.")
    parser.add_argument(
        "--dump",
        type=pathlib.Path,
        default=None,
        help="Optional path to the full FAO AGROVOC SKOS-XL CSV dump for external cross-checking.",
    )
    args = parser.parse_args()

    if not ANCHORS_CSV.exists():
        print(f"[ERROR] Missing canonical anchor table: {ANCHORS_CSV}", file=sys.stderr)
        return 1

    anchors = load_anchors()
    errors: list[str] = []

    if args.dump:
        if not args.dump.exists():
            print(f"[ERROR] Specified AGROVOC dump not found: {args.dump}", file=sys.stderr)
            return 1
        agrovoc = load_agrovoc_dump(args.dump)
        for code, meta in anchors.items():
            if code not in agrovoc:
                errors.append(f"[agrovoc_anchors.csv] Code {code} DOES NOT EXIST in {args.dump}")
                continue
            pref_en, _ = agrovoc[code]
            if pref_en.lower() != meta["prefLabel_en"].lower():
                errors.append(
                    f"[agrovoc_anchors.csv] {code}: expected prefLabel_en='{pref_en}', "
                    f"found '{meta['prefLabel_en']}'"
                )

    errors.extend(scan_files(anchors))

    if errors:
        print("AGROVOC validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(anchors)} canonical AGROVOC concepts verified across "
        f"{len(SCAN_TARGETS)} executable model files (0 divergences)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

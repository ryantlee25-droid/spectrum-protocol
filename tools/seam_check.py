#!/usr/bin/env python3
"""
seam_check.py — Convoy seam-check tool for Claude Code Mayor (Phase 4 Integration)

Usage:
    python3 ~/.claude/hooks/seam_check.py /path/to/convoy/dir/ [--json]

Importable:
    from seam_check import run_seam_check
    result = run_seam_check("/path/to/convoy/dir/")
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── Files to skip when scanning for rider mailboxes ──────────────────────────
SKIP_FILES = {
    "MANIFEST.md",
    "CONTRACT.md",
    "SEAM-CHECK.md",
    "MERGE-PLAN.md",
    "README.md",
    "AMENDMENT.md",
    "LESSONS.md",
}


# ── Simple frontmatter parser ─────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Parse YAML-ish frontmatter from a markdown file.

    Returns (frontmatter_dict, body_text).
    Returns ({}, text) if no valid frontmatter block is found.

    Handles:
      - Scalar values: key: value
      - Lists of scalars:
            key:
              - value1
              - value2
      - Lists of objects (e.g. seams, assumptions):
            seams:
              - id: s1
                target_rider: rider-ui
                ...
    """
    if not text.lstrip().startswith("---"):
        return {}, text

    lines = text.splitlines()
    # Find opening ---
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            start = i
            break
    if start is None:
        return {}, text

    # Find closing ---
    end = None
    for i in range(start + 1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text

    fm_lines = lines[start + 1:end]
    body = "\n".join(lines[end + 1:])

    result = _parse_yaml_block(fm_lines)
    return result, body


def _parse_yaml_block(lines: list[str]) -> dict:
    """
    Minimal line-by-line YAML parser sufficient for the rider mailbox schema.
    Handles scalars, flat lists, and lists-of-objects at one level of nesting.
    """
    result: dict = {}
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        # Top-level key: value or key: (start of a block)
        m = re.match(r'^(\w[\w_-]*):\s*(.*)', line)
        if not m:
            i += 1
            continue

        key = m.group(1)
        raw_val = m.group(2).strip()

        if raw_val:
            # Inline scalar value
            result[key] = _cast_scalar(raw_val)
            i += 1
        else:
            # Block value — collect indented child lines
            i += 1
            child_lines: list[str] = []
            while i < len(lines):
                child = lines[i]
                if child.strip() == "" or child.strip().startswith("#"):
                    i += 1
                    continue
                # If not indented, we're back at the top level
                if not child.startswith(" ") and not child.startswith("\t"):
                    break
                child_lines.append(child)
                i += 1

            result[key] = _parse_block_value(child_lines)

    return result


def _parse_block_value(lines: list[str]) -> Any:
    """
    Parse a block of indented lines as either:
      - A list of scalars  (lines starting with "- value")
      - A list of objects  (lines starting with "- key: value" or continuing object props)
      - A nested dict (lines "  key: value" without leading dash)
    """
    if not lines:
        return None

    # Detect list vs dict by first meaningful line
    first = next((l for l in lines if l.strip()), "")
    stripped_first = first.strip()

    if stripped_first.startswith("- "):
        return _parse_list(lines)
    else:
        return _parse_yaml_block([l.lstrip() for l in lines])


def _parse_list(lines: list[str]) -> list:
    """
    Parse indented list lines into a list of scalars or objects.
    Each item starts with "- "; continuation lines are indented further.
    """
    items: list = []
    current_item_lines: list[str] = []
    base_indent: Optional[int] = None

    def flush_item():
        if not current_item_lines:
            return
        first_line = current_item_lines[0]
        # Strip the leading "- " (preserving the rest)
        body_first = re.sub(r'^\s*-\s*', '', first_line, count=1)
        rest = current_item_lines[1:]

        # Check if the item is a scalar or an object
        if re.match(r'^\w[\w_-]*:', body_first.strip()):
            # It's an object — de-indent continuation lines to match first line's content level
            # The content after "- " starts at (base_indent + 2).
            # Continuation lines are indented to align with that content.
            content_indent = (base_indent or 0) + 2
            dedented = []
            for l in rest:
                if len(l) > content_indent and l[:content_indent].strip() == '':
                    dedented.append(l[content_indent:])
                else:
                    dedented.append(l.lstrip())
            obj_lines = [body_first] + dedented
            items.append(_parse_yaml_block(obj_lines))
        else:
            # It's a scalar
            items.append(_cast_scalar(body_first.strip()))

    for line in lines:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if stripped.startswith("- "):
            if base_indent is None:
                base_indent = indent
            if indent == base_indent:
                # New top-level list item
                flush_item()
                current_item_lines = [line]
            else:
                # Nested list item — treat as continuation
                current_item_lines.append(line)
        else:
            # Continuation of current item
            current_item_lines.append(line)

    flush_item()
    return items


def _cast_scalar(value: str) -> Any:
    """Cast a string value to the most appropriate Python type."""
    if value in ("true", "True", "yes"):
        return True
    if value in ("false", "False", "no"):
        return False
    if value in ("null", "None", "~", ""):
        return None
    # Quoted string
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    # Integer
    try:
        return int(value)
    except ValueError:
        pass
    # Float
    try:
        return float(value)
    except ValueError:
        pass
    return value


# ── Load mailbox files ────────────────────────────────────────────────────────

def load_mailboxes(convoy_dir: Path) -> list[dict]:
    """
    Read all .md files in convoy_dir, skip known non-mailbox files,
    parse frontmatter, and return list of dicts with keys:
      filename, frontmatter, body
    Only files with non-empty frontmatter AND a 'rider' key are included.
    """
    mailboxes = []
    for path in sorted(convoy_dir.glob("*.md")):
        if path.name in SKIP_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, body = _parse_frontmatter(text)
        if fm and "rider" in fm:
            mailboxes.append({"filename": path.name, "frontmatter": fm, "body": body})
    return mailboxes


# ── Seam-check algorithm ──────────────────────────────────────────────────────

def _files_for_rider(fm: dict) -> list[str]:
    created = fm.get("files_created") or []
    modified = fm.get("files_modified") or []
    if not isinstance(created, list):
        created = []
    if not isinstance(modified, list):
        modified = []
    return created + modified


def _keyword_match(what: str, fm: dict, body: str) -> bool:
    """Return True if any significant keyword from `what` appears in rider's files or body."""
    # Extract meaningful tokens (skip short words)
    tokens = [t for t in re.split(r'[\s,./\\@]+', what) if len(t) >= 3]
    if not tokens:
        return False
    search_corpus = " ".join(_files_for_rider(fm)) + " " + body
    return any(token.lower() in search_corpus.lower() for token in tokens)


def check_seams(mailboxes: list[dict]) -> list[dict]:
    """
    Cross-reference all seams declared in mailbox frontmatters.
    Returns list of result dicts.
    """
    # Build index: rider_name -> mailbox entry
    rider_index: dict[str, dict] = {}
    for mb in mailboxes:
        rider_name = mb["frontmatter"].get("rider", "")
        if rider_name:
            rider_index[rider_name] = mb

    results = []

    for mb in mailboxes:
        fm = mb["frontmatter"]
        declared_by = fm.get("rider", mb["filename"])
        seams = fm.get("seams") or []
        if not isinstance(seams, list):
            continue

        for seam in seams:
            if not isinstance(seam, dict):
                continue

            seam_id = seam.get("id", "?")
            target = seam.get("target_rider", "")
            where = seam.get("where", "")
            what = seam.get("what", "")

            # Determine status
            if target not in rider_index:
                status = "MISSING"
                notes = f"Rider '{target}' not found in mailboxes"
            else:
                target_mb = rider_index[target]
                target_fm = target_mb["frontmatter"]
                target_status = str(target_fm.get("status", "")).lower()
                compliance = str(target_fm.get("contract_compliance", "full")).lower()

                if target_status in ("failed", "blocked"):
                    status = "BLOCKED"
                    notes = f"Target rider status: {target_status}"
                else:
                    target_files = _files_for_rider(target_fm)
                    file_found = any(
                        where.lower() in f.lower() for f in target_files
                    ) if where else False

                    if file_found:
                        status = "CONFIRMED" if compliance != "none" else "WARNING"
                        notes = f"{where} in {target}'s files"
                        if compliance == "none":
                            notes += " (compliance=none — downgraded)"
                    else:
                        if compliance in ("full", "partial"):
                            status = "UNCONFIRMED"
                            notes = f"{where or 'target file'} not found in {target}'s file lists — verify in diff"
                        elif compliance == "none":
                            status = "WARNING"
                            notes = f"compliance=none on {target}; {where or 'target file'} not found"
                        else:
                            status = "UNCONFIRMED"
                            notes = f"{where or 'target file'} not found in {target}'s file lists — verify in diff"

            results.append({
                "seam_id": seam_id,
                "declared_by": declared_by,
                "target_rider": target,
                "status": status,
                "notes": notes,
            })

    return results


def check_assumptions(mailboxes: list[dict]) -> list[dict]:
    """
    Cross-reference all assumptions declared in mailbox frontmatters.
    Returns list of result dicts.
    """
    rider_index: dict[str, dict] = {}
    for mb in mailboxes:
        rider_name = mb["frontmatter"].get("rider", "")
        if rider_name:
            rider_index[rider_name] = mb

    results = []

    for mb in mailboxes:
        fm = mb["frontmatter"]
        declared_by = fm.get("rider", mb["filename"])
        assumptions = fm.get("assumptions") or []
        if not isinstance(assumptions, list):
            continue

        for assumption in assumptions:
            if not isinstance(assumption, dict):
                continue

            assump_id = assumption.get("id", "?")
            about_rider = assumption.get("about_rider", "")
            what = assumption.get("what", "")

            if about_rider not in rider_index:
                status = "UNVALIDATED"
                notes = f"Rider '{about_rider}' not found in mailboxes"
            else:
                target_mb = rider_index[about_rider]
                target_fm = target_mb["frontmatter"]
                body = target_mb["body"]
                if _keyword_match(what, target_fm, body):
                    status = "VALIDATED"
                    notes = f"keyword match in {about_rider} narrative"
                else:
                    status = "UNVALIDATED"
                    notes = f"no keyword match found in {about_rider} — verify manually"

            results.append({
                "assumption_id": assump_id,
                "declared_by": declared_by,
                "about_rider": about_rider,
                "status": status,
                "notes": notes,
            })

    return results


def check_file_overlap(mailboxes: list[dict]) -> list[dict]:
    """
    Detect any file path claimed by more than one rider.
    Returns list of conflict dicts.
    """
    file_to_riders: dict[str, list[str]] = {}

    for mb in mailboxes:
        fm = mb["frontmatter"]
        rider_name = fm.get("rider", mb["filename"])
        for f in _files_for_rider(fm):
            if f not in file_to_riders:
                file_to_riders[f] = []
            file_to_riders[f].append(rider_name)

    conflicts = []
    for path, riders in sorted(file_to_riders.items()):
        if len(riders) > 1:
            conflicts.append({"path": path, "riders": riders})
    return conflicts


def check_confidence(mailboxes: list[dict]) -> list[dict]:
    """Return confidence summary per rider."""
    rows = []
    for mb in mailboxes:
        fm = mb["frontmatter"]
        rider_name = fm.get("rider", mb["filename"])
        confidence = fm.get("confidence", "unknown")
        warnings = fm.get("warnings") or []
        open_exits = fm.get("open_exits") or []
        notes_parts = []
        if isinstance(warnings, list) and warnings:
            notes_parts.append(f"{len(warnings)} warning(s)")
        if isinstance(open_exits, list) and open_exits:
            notes_parts.append(f"{len(open_exits)} open exit(s)")
        notes = ", ".join(notes_parts) if notes_parts else "—"
        rows.append({"rider": rider_name, "confidence": str(confidence), "notes": notes})
    return rows


# ── Output generation ─────────────────────────────────────────────────────────

def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    # Build column widths
    widths = [max(len(h), *(len(str(r[i])) for r in rows), 3)
              for i, h in enumerate(headers)] if rows else [max(len(h), 3) for h in headers]
    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    header_row = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |"
    data_rows = [
        "| " + " | ".join(str(c).ljust(w) for c, w in zip(row, widths)) + " |"
        for row in rows
    ]
    return "\n".join([header_row, sep] + data_rows)


def build_seam_check_md(
    convoy_id: str,
    seam_results: list[dict],
    assumption_results: list[dict],
    overlap_results: list[dict],
    confidence_rows: list[dict],
    blockers: list[str],
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        f"# Seam Check: {convoy_id}",
        f"Generated: {now}",
        "",
        "## Seam Results",
        "",
    ]

    if seam_results:
        rows = [
            [r["seam_id"], r["declared_by"], r["target_rider"], r["status"], r["notes"]]
            for r in seam_results
        ]
        lines.append(_md_table(
            ["Seam ID", "Declared By", "Target Rider", "Status", "Notes"], rows
        ))
    else:
        lines.append("_No seams declared._")

    lines += ["", "## Assumption Results", ""]

    if assumption_results:
        rows = [
            [r["assumption_id"], r["declared_by"], r["about_rider"], r["status"], r["notes"]]
            for r in assumption_results
        ]
        lines.append(_md_table(
            ["Assumption ID", "Declared By", "About Rider", "Status", "Notes"], rows
        ))
    else:
        lines.append("_No assumptions declared._")

    lines += ["", "## File Overlap Check", ""]

    if overlap_results:
        rows = [
            [c["path"], ", ".join(c["riders"])]
            for c in overlap_results
        ]
        lines.append(_md_table(["Path", "Claimed By"], rows))
    else:
        lines.append("No conflicts detected.")

    lines += ["", "## Confidence Summary", ""]

    if confidence_rows:
        rows = [[r["rider"], r["confidence"], r["notes"]] for r in confidence_rows]
        lines.append(_md_table(["Rider", "Confidence", "Notes"], rows))
    else:
        lines.append("_No riders found._")

    lines += ["", "## Blockers", ""]

    if blockers:
        for b in blockers:
            lines.append(f"- {b}")
    else:
        lines.append("None")

    # Summary stats
    total_seams = len(seam_results)
    confirmed_seams = sum(1 for r in seam_results if r["status"] == "CONFIRMED")
    total_assumptions = len(assumption_results)
    validated_assumptions = sum(1 for r in assumption_results if r["status"] == "VALIDATED")
    n_conflicts = len(overlap_results)
    n_warnings = sum(
        1 for r in confidence_rows
        if r["notes"] != "—" and "warning" in r["notes"].lower()
    )
    low_confidence = [r["rider"] for r in confidence_rows if r["confidence"] == "low"]

    lines += [
        "",
        "## Summary",
        "",
        f"- {confirmed_seams}/{total_seams} seams confirmed"
        + (f", {total_seams - confirmed_seams} unconfirmed/missing" if total_seams - confirmed_seams else ""),
        f"- {validated_assumptions}/{total_assumptions} assumptions validated",
        f"- {n_conflicts} file ownership conflict(s)",
        f"- {n_warnings} rider(s) with warnings"
        + (f" (low confidence: {', '.join(low_confidence)})" if low_confidence else ""),
    ]

    return "\n".join(lines) + "\n"


# ── Main entry point ──────────────────────────────────────────────────────────

def run_seam_check(convoy_dir_path: str) -> dict:
    """
    Run the full seam-check pipeline.

    Returns a structured result dict:
    {
      "convoy_id": str,
      "convoy_dir": str,
      "mailboxes": [...],
      "seam_results": [...],
      "assumption_results": [...],
      "overlap_results": [...],
      "confidence_rows": [...],
      "blockers": [...],
      "has_blockers": bool,
      "seam_check_md": str,
    }
    """
    convoy_dir = Path(convoy_dir_path).expanduser().resolve()
    if not convoy_dir.is_dir():
        raise ValueError(f"Not a directory: {convoy_dir}")

    # Derive convoy_id from directory name
    convoy_id = convoy_dir.name

    mailboxes = load_mailboxes(convoy_dir)

    # Try to get convoy_id from frontmatter if all agree
    convoy_ids_fm = {mb["frontmatter"].get("convoy") for mb in mailboxes if mb["frontmatter"].get("convoy")}
    if len(convoy_ids_fm) == 1:
        convoy_id = convoy_ids_fm.pop()

    seam_results = check_seams(mailboxes)
    assumption_results = check_assumptions(mailboxes)
    overlap_results = check_file_overlap(mailboxes)
    confidence_rows = check_confidence(mailboxes)

    # Collect blockers
    blockers = []
    for r in seam_results:
        if r["status"] in ("BLOCKED", "MISSING", "CONFLICT"):
            blockers.append(
                f"[SEAM {r['seam_id']}] {r['declared_by']} → {r['target_rider']}: {r['status']} — {r['notes']}"
            )
    for c in overlap_results:
        blockers.append(
            f"[FILE CONFLICT] {c['path']} claimed by: {', '.join(c['riders'])}"
        )

    seam_check_md = build_seam_check_md(
        convoy_id, seam_results, assumption_results, overlap_results, confidence_rows, blockers
    )

    result = {
        "convoy_id": convoy_id,
        "convoy_dir": str(convoy_dir),
        "mailboxes": [mb["filename"] for mb in mailboxes],
        "seam_results": seam_results,
        "assumption_results": assumption_results,
        "overlap_results": overlap_results,
        "confidence_rows": confidence_rows,
        "blockers": blockers,
        "has_blockers": len(blockers) > 0,
        "seam_check_md": seam_check_md,
    }
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Convoy seam-check tool — validates seams and assumptions across rider mailboxes."
    )
    parser.add_argument(
        "convoy_dir",
        help="Path to the convoy directory (e.g. ~/.claude/convoy/auth-refactor-0329/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON to stdout instead of the summary",
    )
    args = parser.parse_args()

    try:
        result = run_seam_check(args.convoy_dir)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Write SEAM-CHECK.md
    convoy_dir = Path(args.convoy_dir).expanduser().resolve()
    output_path = convoy_dir / "SEAM-CHECK.md"
    output_path.write_text(result["seam_check_md"], encoding="utf-8")

    if args.json:
        # seam_check_md is large — omit from JSON output, it's on disk
        json_result = {k: v for k, v in result.items() if k != "seam_check_md"}
        print(json.dumps(json_result, indent=2))
    else:
        # Human-readable summary
        print(f"\nSeam Check: {result['convoy_id']}")
        print(f"Mailboxes scanned: {len(result['mailboxes'])}")
        print(f"  {', '.join(result['mailboxes']) or 'none'}")
        print()

        seams = result["seam_results"]
        if seams:
            confirmed = sum(1 for r in seams if r["status"] == "CONFIRMED")
            print(f"Seams:       {confirmed}/{len(seams)} confirmed")
            for r in seams:
                icon = "✓" if r["status"] == "CONFIRMED" else ("✗" if r["status"] in ("BLOCKED", "MISSING") else "?")
                print(f"  [{icon}] {r['seam_id']} ({r['declared_by']} → {r['target_rider']}): {r['status']} — {r['notes']}")
        else:
            print("Seams:       none declared")

        print()
        assumptions = result["assumption_results"]
        if assumptions:
            validated = sum(1 for r in assumptions if r["status"] == "VALIDATED")
            print(f"Assumptions: {validated}/{len(assumptions)} validated")
            for r in assumptions:
                icon = "✓" if r["status"] == "VALIDATED" else "?"
                print(f"  [{icon}] {r['assumption_id']} ({r['declared_by']} about {r['about_rider']}): {r['status']} — {r['notes']}")
        else:
            print("Assumptions: none declared")

        print()
        overlaps = result["overlap_results"]
        if overlaps:
            print(f"File conflicts: {len(overlaps)} CONFLICT(S) FOUND")
            for c in overlaps:
                print(f"  [!] {c['path']} — claimed by: {', '.join(c['riders'])}")
        else:
            print("File conflicts: none")

        print()
        low_conf = [r for r in result["confidence_rows"] if r["confidence"] == "low"]
        if low_conf:
            print(f"Low-confidence riders: {', '.join(r['rider'] for r in low_conf)}")

        print()
        blockers = result["blockers"]
        if blockers:
            print(f"BLOCKERS ({len(blockers)}):")
            for b in blockers:
                print(f"  - {b}")
        else:
            print("Blockers: none")

        print()
        print(f"SEAM-CHECK.md written to: {output_path}")

    sys.exit(1 if result["has_blockers"] else 0)


if __name__ == "__main__":
    main()

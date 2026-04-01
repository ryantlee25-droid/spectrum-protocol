"""Output parser for Gold agent responses.

Parses raw LLM output into structured dicts using regex + heuristics.
NOT LLM-assisted — avoids circular evaluation.

parse_confidence scoring:
  1.0 = all fields extracted via exact regex match
  0.8-0.99 = most fields exact, minor fallbacks used
  <0.8 = at least one field extracted via fallback heuristic
"""

import re
from typing import Any


# ---------------------------------------------------------------------------
# Muster parser
# ---------------------------------------------------------------------------

def _parse_file_ownership_markdown_table(text: str) -> list[dict]:
    """Parse a markdown table of file ownership.

    Matches tables like:
    | File | Howler | Action |
    |------|--------|--------|
    | path/to/file.ts | howler-name | CREATES |
    """
    rows: list[dict] = []
    # Find table blocks: header row + separator + data rows
    table_pattern = re.compile(
        r"\|[^\n]*File[^\n]*\|[^\n]*Howler[^\n]*\|[^\n]*Action[^\n]*\|\s*\n"
        r"\|[-| ]+\|\s*\n"
        r"((?:\|[^\n]+\|\s*\n?)+)",
        re.IGNORECASE,
    )
    for table_match in table_pattern.finditer(text):
        body = table_match.group(1)
        for row_match in re.finditer(r"\|([^|]+)\|([^|]+)\|([^|]+)\|[^\n]*", body):
            file_val = row_match.group(1).strip()
            howler_val = row_match.group(2).strip()
            action_val = row_match.group(3).strip().upper()
            if file_val and howler_val and action_val in ("CREATES", "MODIFIES"):
                rows.append({"file": file_val, "howler": howler_val, "action": action_val})
    return rows


def _parse_file_ownership_bullet_list(text: str) -> list[dict]:
    """Parse bullet-list format of file ownership.

    Matches patterns like:
    - `path/to/file.ts` → howler-name (CREATES)
    * path/to/file.ts — howler-name: CREATES
    - path/to/file.ts: howler-name [CREATES]
    """
    rows: list[dict] = []
    # Pattern: bullet + file path + separator + howler + optional action
    bullet_pattern = re.compile(
        r"^[ \t]*[-*]\s+"                          # bullet
        r"`?([^\s`→—:\[\]]+\.\w+)`?"               # file path (has extension)
        r"(?:\s*[→—:]\s*|\s+)"                    # separator
        r"([a-z][a-z0-9-]*)"                       # howler name
        r"(?:[^\n]*)?"                             # rest of line
        r"(CREATES|MODIFIES)?",                    # optional action
        re.MULTILINE | re.IGNORECASE,
    )
    for m in bullet_pattern.finditer(text):
        file_val = m.group(1).strip()
        howler_val = m.group(2).strip()
        action_val = (m.group(3) or "CREATES").upper()
        if file_val and howler_val:
            rows.append({"file": file_val, "howler": howler_val, "action": action_val})
    return rows


def _parse_file_ownership_indented(text: str) -> list[dict]:
    """Parse indented/plain-text format of file ownership.

    Matches patterns like:
      howler-auth:
        - src/auth/middleware.ts (CREATES)
        - src/auth/types.ts (CREATES)

    or:
      CREATES: src/auth/middleware.ts (howler-auth)
    """
    rows: list[dict] = []

    # Pattern A: howler-name: followed by indented file list
    howler_header = re.compile(
        r"^[ \t]*([a-z][a-z0-9-]+):\s*$", re.MULTILINE
    )
    file_item = re.compile(
        r"^[ \t]+[-*]?\s+([^\s()\n]+\.\w+)"
        r"(?:\s*\(?(CREATES|MODIFIES)?\)?)?\s*$",
        re.MULTILINE | re.IGNORECASE,
    )

    for header_m in howler_header.finditer(text):
        howler_val = header_m.group(1)
        # Look ahead for indented file items until next non-indented line
        after = text[header_m.end():]
        for item_m in file_item.finditer(after):
            # Stop if we hit a non-indented howler header
            line_start = after.rfind("\n", 0, item_m.start()) + 1
            if line_start > 0 and not after[line_start].isspace():
                break
            file_val = item_m.group(1).strip()
            action_val = (item_m.group(2) or "CREATES").upper()
            rows.append({"file": file_val, "howler": howler_val, "action": action_val})

    # Pattern B: ACTION: file (howler)
    action_file_pattern = re.compile(
        r"(CREATES|MODIFIES):\s*([^\s()\n]+\.\w+)"
        r"(?:\s*\(([a-z][a-z0-9-]+)\))?",
        re.IGNORECASE,
    )
    for m in action_file_pattern.finditer(text):
        action_val = m.group(1).upper()
        file_val = m.group(2).strip()
        howler_val = m.group(3).strip() if m.group(3) else "unknown"
        rows.append({"file": file_val, "howler": howler_val, "action": action_val})

    return rows


def _parse_dag_edges(text: str) -> list[dict]:
    """Extract DAG edges from muster output.

    Handles both YAML block format and inline format.
    """
    edges: list[dict] = []

    # YAML block: dag_edges: / - from: ... / to: ... / type: ...
    yaml_block = re.compile(
        r"dag_edges:\s*\n((?:[ \t]*-[^\n]+\n(?:[ \t]+[^\n]+\n)*)+)",
        re.IGNORECASE,
    )
    edge_item = re.compile(
        r"from:\s*([a-z][a-z0-9-]+)",
        re.IGNORECASE,
    )
    to_item = re.compile(r"to:\s*([a-z][a-z0-9-]+)", re.IGNORECASE)
    type_item = re.compile(r"type:\s*(\w+)", re.IGNORECASE)

    for block_m in yaml_block.finditer(text):
        block = block_m.group(1)
        # Split into individual edge entries
        entries = re.split(r"\n[ \t]*-\s+", block)
        for entry in entries:
            from_m = edge_item.search(entry)
            to_m = to_item.search(entry)
            type_m = type_item.search(entry)
            if from_m and to_m:
                edges.append({
                    "from": from_m.group(1),
                    "to": to_m.group(1),
                    "type": type_m.group(1) if type_m else "depends",
                })

    # Inline format: "howler-b depends on howler-a (types)"
    if not edges:
        inline = re.compile(
            r"([a-z][a-z0-9-]+)\s+depends\s+on\s+([a-z][a-z0-9-]+)"
            r"(?:\s*\((\w+)\))?",
            re.IGNORECASE,
        )
        for m in inline.finditer(text):
            edges.append({
                "from": m.group(1),
                "to": m.group(2),
                "type": m.group(3) if m.group(3) else "depends",
            })

    return edges


def _parse_contract_sections(text: str) -> list[dict]:
    """Extract CONTRACT.md sections from muster output."""
    sections: list[dict] = []

    # Look for markdown headers that introduce contract-like sections
    section_pattern = re.compile(
        r"#{1,4}\s+(Shared Types|Per-Howler|Preconditions?|Postconditions?|Invariants?|Design-by-Contract[^\n]*)\s*\n"
        r"([\s\S]+?)(?=\n#{1,4}\s|\Z)",
        re.IGNORECASE,
    )
    for m in section_pattern.finditer(text):
        section_name = m.group(1).strip().lower().replace(" ", "_")
        content = m.group(2).strip()
        if content:
            sections.append({"section": section_name, "content": content})

    return sections


def parse_muster_output(raw: str) -> dict:
    """Parse raw muster-phase Gold output.

    Tries multiple format variations for file ownership tables.
    Returns parse_confidence based on extraction quality.

    Returns:
        dict with keys:
          - file_ownership: list of {file, howler, action}
          - dag_edges: list of {from, to, type}
          - contract_sections: list of {section, content}
          - parse_confidence: float 0.0-1.0
    """
    confidence_hits: list[bool] = []

    # Try format 1: markdown table (highest confidence)
    file_ownership = _parse_file_ownership_markdown_table(raw)
    if file_ownership:
        confidence_hits.append(True)
    else:
        # Try format 2: bullet list
        file_ownership = _parse_file_ownership_bullet_list(raw)
        if file_ownership:
            confidence_hits.append(False)  # fallback used
        else:
            # Try format 3: indented/plain text
            file_ownership = _parse_file_ownership_indented(raw)
            confidence_hits.append(False)  # fallback used

    dag_edges = _parse_dag_edges(raw)
    confidence_hits.append(bool(dag_edges))

    contract_sections = _parse_contract_sections(raw)
    confidence_hits.append(bool(contract_sections))

    # Compute confidence: fraction of fields extracted via primary method
    n_exact = sum(1 for h in confidence_hits if h)
    n_total = len(confidence_hits)
    parse_confidence = round(n_exact / n_total, 2) if n_total else 0.0

    return {
        "file_ownership": file_ownership,
        "dag_edges": dag_edges,
        "contract_sections": contract_sections,
        "parse_confidence": parse_confidence,
    }


# ---------------------------------------------------------------------------
# Pax parser
# ---------------------------------------------------------------------------

def parse_pax_output(raw: str) -> dict:
    """Parse raw pax-phase Gold output.

    Extracts deviation flags from the structured DEVIATION blocks.

    Returns:
        dict with keys:
          - deviation_flags: list of {howler, deviation_type, description, severity}
          - parse_confidence: float 0.0-1.0
    """
    deviation_flags: list[dict] = []
    confidence_hits: list[bool] = []

    # Primary: structured DEVIATION blocks
    # Regex captures: Howler, Type, Severity, Description (in that order)
    deviation_block = re.compile(
        r"DEVIATION\s*\n"
        r"[ \t]*Howler:\s*([^\n]+)\n"
        r"[ \t]*Type:\s*([^\n]+)\n"
        r"[ \t]*Severity:\s*([^\n]+)\n"
        r"[ \t]*Description:\s*([^\n]+)",
        re.IGNORECASE,
    )
    for m in deviation_block.finditer(raw):
        deviation_flags.append({
            "howler": m.group(1).strip(),
            "deviation_type": m.group(2).strip().lower().replace(" ", "_"),
            "severity": m.group(3).strip().lower(),
            "description": m.group(4).strip(),
        })

    if deviation_flags:
        confidence_hits.append(True)
    else:
        # Fallback: look for lines mentioning deviations
        fallback_pattern = re.compile(
            r"([a-z][a-z0-9-]+).*?(postcondition_violation|seam_mismatch|ownership_violation|contract_breach)"
            r".*?(blocker|warning|observation)",
            re.IGNORECASE,
        )
        for m in fallback_pattern.finditer(raw):
            deviation_flags.append({
                "howler": m.group(1).strip(),
                "deviation_type": m.group(2).strip().lower(),
                "severity": m.group(3).strip().lower(),
                "description": f"(extracted via heuristic from line context)",
            })
        confidence_hits.append(False)

    parse_confidence = 1.0 if all(confidence_hits) else (0.7 if deviation_flags else 0.0)

    return {
        "deviation_flags": deviation_flags,
        "parse_confidence": parse_confidence,
    }


# ---------------------------------------------------------------------------
# Forge parser
# ---------------------------------------------------------------------------

def parse_forge_output(raw: str) -> dict:
    """Parse raw forge-phase Gold output.

    Extracts failure classification, recovery action, and circuit breaker flag.

    Returns:
        dict with keys:
          - classification: str
          - recovery_action: str
          - circuit_breaker_triggered: bool
          - parse_confidence: float 0.0-1.0
    """
    confidence_hits: list[bool] = []

    VALID_CLASSIFICATIONS = {
        "transient", "logical", "structural", "environmental", "conflict"
    }
    VALID_RECOVERY_ACTIONS = {"resume", "retry", "skip", "restructure"}

    # Primary: structured block format
    classification_match = re.search(
        r"CLASSIFICATION:\s*(transient|logical|structural|environmental|conflict)",
        raw,
        re.IGNORECASE,
    )
    recovery_match = re.search(
        r"RECOVERY_ACTION:\s*(resume|retry|skip|restructure)",
        raw,
        re.IGNORECASE,
    )
    circuit_match = re.search(
        r"CIRCUIT_BREAKER_TRIGGERED:\s*(true|false|yes|no)",
        raw,
        re.IGNORECASE,
    )

    if classification_match:
        classification = classification_match.group(1).lower()
        confidence_hits.append(True)
    else:
        # Fallback: look for classification keywords in context
        classification = _heuristic_extract_classification(raw, VALID_CLASSIFICATIONS)
        confidence_hits.append(False)

    if recovery_match:
        recovery_action = recovery_match.group(1).lower()
        confidence_hits.append(True)
    else:
        recovery_action = _heuristic_extract_recovery(raw, VALID_RECOVERY_ACTIONS)
        confidence_hits.append(False)

    if circuit_match:
        raw_val = circuit_match.group(1).lower()
        circuit_breaker_triggered = raw_val in ("true", "yes")
        confidence_hits.append(True)
    else:
        # Heuristic: look for mentions of circuit breaker being triggered
        circuit_breaker_triggered = bool(
            re.search(r"circuit.breaker.*(trigger|activat|escalat)", raw, re.IGNORECASE)
        )
        confidence_hits.append(False)

    n_exact = sum(1 for h in confidence_hits if h)
    n_total = len(confidence_hits)
    parse_confidence = round(n_exact / n_total, 2) if n_total else 0.0

    return {
        "classification": classification,
        "recovery_action": recovery_action,
        "circuit_breaker_triggered": circuit_breaker_triggered,
        "parse_confidence": parse_confidence,
    }


def _heuristic_extract_classification(
    text: str, valid: set[str]
) -> str:
    """Heuristically find a failure classification keyword in text."""
    # Look for classification-related sentences
    for word in ("structural", "logical", "transient", "environmental", "conflict"):
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            return word
    return "unknown"


def _heuristic_extract_recovery(text: str, valid: set[str]) -> str:
    """Heuristically find a recovery action keyword in text."""
    for word in ("restructure", "resume", "retry", "skip"):
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            return word
    return "unknown"

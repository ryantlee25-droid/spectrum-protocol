"""Tests for harness/output_parser.py.

The most important test file — validates that parsers handle multiple
format variations and extract structured data correctly.
"""

import pytest

from harness.output_parser import (
    _parse_file_ownership_bullet_list,
    _parse_file_ownership_indented,
    _parse_file_ownership_markdown_table,
    _parse_dag_edges,
    _parse_contract_sections,
    parse_forge_output,
    parse_muster_output,
    parse_pax_output,
)


# ===========================================================================
# File Ownership — Format 1: Markdown Table
# ===========================================================================

MARKDOWN_TABLE_OUTPUT = """
# File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| src/auth/middleware.ts | howler-auth | CREATES |
| src/auth/types.ts | howler-auth | CREATES |
| src/api/routes.ts | howler-api | CREATES |
| src/app/layout.tsx | howler-ui | MODIFIES |
"""

MARKDOWN_TABLE_LOWER_CASE_HEADERS = """
| file | howler | action |
|------|--------|--------|
| src/db/schema.ts | howler-db | CREATES |
| src/db/migrations.ts | howler-db | CREATES |
"""

MARKDOWN_TABLE_EXTRA_COLUMNS = """
## Ownership

| File | Howler | Action | Notes |
|------|--------|--------|-------|
| src/types/shared.ts | howler-auth | CREATES | Shared interface |
| src/api/handlers.ts | howler-api | CREATES | REST endpoints |
"""


class TestMarkdownTableParser:
    def test_basic_markdown_table(self):
        rows = _parse_file_ownership_markdown_table(MARKDOWN_TABLE_OUTPUT)
        assert len(rows) == 4
        files = {r["file"] for r in rows}
        assert "src/auth/middleware.ts" in files
        assert "src/api/routes.ts" in files
        assert "src/app/layout.tsx" in files

    def test_markdown_table_actions(self):
        rows = _parse_file_ownership_markdown_table(MARKDOWN_TABLE_OUTPUT)
        layout_row = next(r for r in rows if r["file"] == "src/app/layout.tsx")
        assert layout_row["action"] == "MODIFIES"

    def test_markdown_table_lowercase_headers(self):
        rows = _parse_file_ownership_markdown_table(MARKDOWN_TABLE_LOWER_CASE_HEADERS)
        assert len(rows) == 2
        assert rows[0]["howler"] == "howler-db"

    def test_markdown_table_extra_columns(self):
        rows = _parse_file_ownership_markdown_table(MARKDOWN_TABLE_EXTRA_COLUMNS)
        assert len(rows) == 2
        files = {r["file"] for r in rows}
        assert "src/types/shared.ts" in files

    def test_markdown_table_empty_text(self):
        rows = _parse_file_ownership_markdown_table("No table here")
        assert rows == []

    def test_markdown_table_result_structure(self):
        rows = _parse_file_ownership_markdown_table(MARKDOWN_TABLE_OUTPUT)
        for row in rows:
            assert "file" in row
            assert "howler" in row
            assert "action" in row
            assert row["action"] in ("CREATES", "MODIFIES")


# ===========================================================================
# File Ownership — Format 2: Bullet List
# ===========================================================================

BULLET_LIST_OUTPUT = """
## File Assignments

- `src/auth/middleware.ts` → howler-auth (CREATES)
- `src/auth/types.ts` → howler-auth (CREATES)
- `src/api/routes.ts` → howler-api (CREATES)
"""

BULLET_LIST_ALT_SEPARATORS = """
* src/db/schema.ts — howler-db CREATES
* src/db/migrations.ts — howler-db CREATES
* src/utils/helpers.ts - howler-utils CREATES
"""

BULLET_LIST_COLON_FORMAT = """
- src/auth/session.ts: howler-auth [CREATES]
- src/api/middleware.ts: howler-api [CREATES]
"""


class TestBulletListParser:
    def test_basic_bullet_list_arrow_format(self):
        rows = _parse_file_ownership_bullet_list(BULLET_LIST_OUTPUT)
        assert len(rows) >= 2
        files = {r["file"] for r in rows}
        assert "src/auth/middleware.ts" in files or any("middleware" in f for f in files)

    def test_bullet_list_dash_separator(self):
        rows = _parse_file_ownership_bullet_list(BULLET_LIST_ALT_SEPARATORS)
        assert len(rows) >= 1
        howlers = {r["howler"] for r in rows}
        assert "howler-db" in howlers or "howler-utils" in howlers

    def test_bullet_list_result_structure(self):
        rows = _parse_file_ownership_bullet_list(BULLET_LIST_OUTPUT)
        for row in rows:
            assert "file" in row
            assert "howler" in row
            assert "action" in row

    def test_bullet_list_empty_text(self):
        rows = _parse_file_ownership_bullet_list("No bullets here.")
        assert rows == []


# ===========================================================================
# File Ownership — Format 3: Indented / Plain Text
# ===========================================================================

INDENTED_OUTPUT = """
## Howler Assignments

howler-auth:
  - src/auth/middleware.ts (CREATES)
  - src/auth/types.ts (CREATES)

howler-api:
  - src/api/routes.ts (CREATES)
  - src/api/handlers.ts (CREATES)
"""

ACTION_FILE_FORMAT = """
CREATES: src/types/shared.ts (howler-auth)
CREATES: src/api/client.ts (howler-api)
MODIFIES: src/app/page.tsx (howler-ui)
"""

MIXED_INDENTED = """
Assignments:

howler-db:
  * src/db/schema.ts (CREATES)
  * src/db/seed.ts (CREATES)
"""


class TestIndentedParser:
    def test_indented_howler_header_format(self):
        rows = _parse_file_ownership_indented(INDENTED_OUTPUT)
        assert len(rows) >= 2
        files = {r["file"] for r in rows}
        assert any("middleware" in f for f in files)

    def test_action_file_format(self):
        rows = _parse_file_ownership_indented(ACTION_FILE_FORMAT)
        assert len(rows) >= 2
        files = {r["file"] for r in rows}
        assert "src/types/shared.ts" in files or "src/api/client.ts" in files

    def test_action_file_modifies(self):
        rows = _parse_file_ownership_indented(ACTION_FILE_FORMAT)
        modifies_rows = [r for r in rows if r["action"] == "MODIFIES"]
        assert len(modifies_rows) >= 1

    def test_indented_result_structure(self):
        rows = _parse_file_ownership_indented(INDENTED_OUTPUT)
        for row in rows:
            assert "file" in row
            assert "howler" in row
            assert "action" in row

    def test_mixed_bullet_in_indented(self):
        rows = _parse_file_ownership_indented(MIXED_INDENTED)
        assert len(rows) >= 1
        howlers = {r["howler"] for r in rows}
        assert "howler-db" in howlers


# ===========================================================================
# parse_muster_output — Integration Tests
# ===========================================================================

FULL_MUSTER_OUTPUT_TABLE = """
# Gold Muster Plan

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| src/auth/middleware.ts | howler-auth | CREATES |
| src/auth/types.ts | howler-auth | CREATES |
| src/api/routes.ts | howler-api | CREATES |

## Dependency DAG

```yaml
dag_edges:
  - from: howler-api
    to: howler-auth
    type: types
```

## Shared Types

```typescript
export interface UserSession {
  userId: string;
  token: string;
}
```

## Per-Howler Design-by-Contract

### howler-auth

Preconditions: None
Postconditions: Exports authMiddleware, exports UserSession type
Invariants: Type safety maintained
"""

FULL_MUSTER_OUTPUT_BULLETS = """
## Howler Assignments

- `src/auth/middleware.ts` → howler-auth (CREATES)
- `src/api/routes.ts` → howler-api (CREATES)
- `src/ui/components.tsx` → howler-ui (CREATES)

## Dependencies

howler-api depends on howler-auth (types)
howler-ui depends on howler-auth (types)

## Contract Sections

### Shared Types

UserSession interface: { userId: string, token: string }

### Per-Howler Design-by-Contract

Preconditions for howler-api: howler-auth must be STABLE
"""


class TestParseMusterOutput:
    def test_markdown_table_format_parse(self):
        result = parse_muster_output(FULL_MUSTER_OUTPUT_TABLE)
        assert "file_ownership" in result
        assert "dag_edges" in result
        assert "contract_sections" in result
        assert "parse_confidence" in result

    def test_markdown_table_extracts_files(self):
        result = parse_muster_output(FULL_MUSTER_OUTPUT_TABLE)
        files = {r["file"] for r in result["file_ownership"]}
        assert "src/auth/middleware.ts" in files
        assert "src/api/routes.ts" in files

    def test_markdown_table_extracts_dag_edges(self):
        result = parse_muster_output(FULL_MUSTER_OUTPUT_TABLE)
        assert len(result["dag_edges"]) >= 1
        edge = result["dag_edges"][0]
        assert "from" in edge
        assert "to" in edge
        assert "type" in edge

    def test_markdown_table_extracts_contract(self):
        result = parse_muster_output(FULL_MUSTER_OUTPUT_TABLE)
        assert len(result["contract_sections"]) >= 1

    def test_bullet_format_parse(self):
        result = parse_muster_output(FULL_MUSTER_OUTPUT_BULLETS)
        assert "file_ownership" in result
        assert len(result["file_ownership"]) >= 2

    def test_parse_confidence_present(self):
        result = parse_muster_output(FULL_MUSTER_OUTPUT_TABLE)
        assert 0.0 <= result["parse_confidence"] <= 1.0

    def test_high_confidence_for_structured_output(self):
        result = parse_muster_output(FULL_MUSTER_OUTPUT_TABLE)
        # All three fields extracted, so confidence should be high
        assert result["parse_confidence"] >= 0.6

    def test_empty_output_returns_empty_lists(self):
        result = parse_muster_output("This output has no structured data.")
        assert result["file_ownership"] == []
        assert result["dag_edges"] == []
        assert "parse_confidence" in result


# ===========================================================================
# parse_pax_output
# ===========================================================================

PAX_OUTPUT_STRUCTURED = """
## Deviation Report

DEVIATION
  Howler: howler-api
  Type: postcondition_violation
  Severity: blocker
  Description: Claims to export validateRequest but function is named validateReq

DEVIATION
  Howler: howler-ui
  Type: seam_mismatch
  Severity: warning
  Description: Imports getSession from wrong path '@/auth' instead of '@/lib/auth'

CLEAN: howler-auth — no deviations found
"""

PAX_OUTPUT_MULTIPLE_BLOCKERS = """
## Validation Results

DEVIATION
  Howler: howler-db
  Type: ownership_violation
  Severity: blocker
  Description: Modified src/types/shared.ts which belongs to howler-auth

DEVIATION
  Howler: howler-api
  Type: contract_breach
  Severity: blocker
  Description: Uses UserSession.user_id instead of UserSession.userId (camelCase required)

CLEAN: howler-auth — postconditions met
CLEAN: howler-ui — all seams confirmed
"""

PAX_OUTPUT_NO_DEVIATIONS = """
## Validation Results

CLEAN: howler-auth — no deviations found
CLEAN: howler-api — all postconditions met
CLEAN: howler-ui — seams confirmed
"""


class TestParsePaxOutput:
    def test_extracts_deviation_flags(self):
        result = parse_pax_output(PAX_OUTPUT_STRUCTURED)
        assert "deviation_flags" in result
        assert len(result["deviation_flags"]) == 2

    def test_deviation_howler_names(self):
        result = parse_pax_output(PAX_OUTPUT_STRUCTURED)
        howlers = {d["howler"] for d in result["deviation_flags"]}
        assert "howler-api" in howlers
        assert "howler-ui" in howlers

    def test_deviation_types(self):
        result = parse_pax_output(PAX_OUTPUT_STRUCTURED)
        dev_types = {d["deviation_type"] for d in result["deviation_flags"]}
        assert "postcondition_violation" in dev_types
        assert "seam_mismatch" in dev_types

    def test_deviation_severities(self):
        result = parse_pax_output(PAX_OUTPUT_STRUCTURED)
        severities = {d["severity"] for d in result["deviation_flags"]}
        assert "blocker" in severities
        assert "warning" in severities

    def test_multiple_blockers(self):
        result = parse_pax_output(PAX_OUTPUT_MULTIPLE_BLOCKERS)
        blockers = [d for d in result["deviation_flags"] if d["severity"] == "blocker"]
        assert len(blockers) == 2

    def test_no_deviations_returns_empty_list(self):
        result = parse_pax_output(PAX_OUTPUT_NO_DEVIATIONS)
        assert result["deviation_flags"] == []

    def test_parse_confidence_present(self):
        result = parse_pax_output(PAX_OUTPUT_STRUCTURED)
        assert "parse_confidence" in result
        assert 0.0 <= result["parse_confidence"] <= 1.0

    def test_high_confidence_for_structured_format(self):
        result = parse_pax_output(PAX_OUTPUT_STRUCTURED)
        assert result["parse_confidence"] >= 0.8

    def test_deviation_description_extracted(self):
        result = parse_pax_output(PAX_OUTPUT_STRUCTURED)
        api_dev = next(
            d for d in result["deviation_flags"] if d["howler"] == "howler-api"
        )
        assert len(api_dev["description"]) > 5  # Has meaningful content


# ===========================================================================
# parse_forge_output
# ===========================================================================

FORGE_OUTPUT_STRUCTURED = """
Based on the HOOK.md and error context, here is my analysis:

```
CLASSIFICATION: transient
RECOVERY_ACTION: resume
CIRCUIT_BREAKER_TRIGGERED: false
RATIONALE: The failure is a network timeout — flaky, not a code bug. Safe to resume.
```
"""

FORGE_OUTPUT_STRUCTURAL = """
After analyzing the failure history (2 prior failures on same locus), I must escalate:

```
CLASSIFICATION: structural
RECOVERY_ACTION: restructure
CIRCUIT_BREAKER_TRIGGERED: true
RATIONALE: Two failures on src/db/connection.ts trigger the circuit breaker. The decomposition is wrong.
```
"""

FORGE_OUTPUT_LOGICAL = """
CLASSIFICATION: logical
RECOVERY_ACTION: retry
CIRCUIT_BREAKER_TRIGGERED: false
RATIONALE: The Howler misunderstood the interface contract. A fresh retry with corrected instructions should work.
"""

FORGE_OUTPUT_ENVIRONMENTAL = """
CLASSIFICATION: environmental
RECOVERY_ACTION: skip
CIRCUIT_BREAKER_TRIGGERED: false
RATIONALE: Missing npm package in the environment. Skip until environment is fixed.
"""

FORGE_OUTPUT_PROSE_STYLE = """
Looking at the failure, this appears to be a structural issue with the task decomposition.
The Howler should restructure the work. The circuit breaker has been triggered since there
were 2 prior logical failures on the same locus.
"""


class TestParseForgeOutput:
    def test_extracts_classification(self):
        result = parse_forge_output(FORGE_OUTPUT_STRUCTURED)
        assert result["classification"] == "transient"

    def test_extracts_recovery_action(self):
        result = parse_forge_output(FORGE_OUTPUT_STRUCTURED)
        assert result["recovery_action"] == "resume"

    def test_circuit_breaker_false(self):
        result = parse_forge_output(FORGE_OUTPUT_STRUCTURED)
        assert result["circuit_breaker_triggered"] is False

    def test_structural_with_circuit_breaker(self):
        result = parse_forge_output(FORGE_OUTPUT_STRUCTURAL)
        assert result["classification"] == "structural"
        assert result["recovery_action"] == "restructure"
        assert result["circuit_breaker_triggered"] is True

    def test_logical_classification(self):
        result = parse_forge_output(FORGE_OUTPUT_LOGICAL)
        assert result["classification"] == "logical"
        assert result["recovery_action"] == "retry"

    def test_environmental_classification(self):
        result = parse_forge_output(FORGE_OUTPUT_ENVIRONMENTAL)
        assert result["classification"] == "environmental"
        assert result["recovery_action"] == "skip"

    def test_parse_confidence_present(self):
        result = parse_forge_output(FORGE_OUTPUT_STRUCTURED)
        assert "parse_confidence" in result
        assert 0.0 <= result["parse_confidence"] <= 1.0

    def test_high_confidence_structured_format(self):
        result = parse_forge_output(FORGE_OUTPUT_STRUCTURED)
        assert result["parse_confidence"] >= 0.8

    def test_heuristic_fallback_prose_style(self):
        result = parse_forge_output(FORGE_OUTPUT_PROSE_STYLE)
        # Should extract something via heuristics
        assert result["classification"] in (
            "structural", "logical", "transient", "environmental", "conflict", "unknown"
        )
        # Confidence should reflect fallback usage
        assert result["parse_confidence"] < 1.0

    def test_circuit_breaker_true_text(self):
        output_with_yes = """
CLASSIFICATION: logical
RECOVERY_ACTION: resume
CIRCUIT_BREAKER_TRIGGERED: yes
RATIONALE: test
"""
        result = parse_forge_output(output_with_yes)
        assert result["circuit_breaker_triggered"] is True

    def test_all_required_keys_present(self):
        result = parse_forge_output(FORGE_OUTPUT_STRUCTURED)
        assert "classification" in result
        assert "recovery_action" in result
        assert "circuit_breaker_triggered" in result
        assert "parse_confidence" in result


# ===========================================================================
# DAG Edge Parser Tests
# ===========================================================================

DAG_YAML_OUTPUT = """
```yaml
dag_edges:
  - from: howler-api
    to: howler-auth
    type: types
  - from: howler-ui
    to: howler-auth
    type: types
  - from: howler-ui
    to: howler-api
    type: integration
```
"""

DAG_INLINE_OUTPUT = """
howler-api depends on howler-auth (types)
howler-ui depends on howler-auth (types)
"""


class TestDagEdgeParser:
    def test_yaml_block_format(self):
        edges = _parse_dag_edges(DAG_YAML_OUTPUT)
        assert len(edges) >= 2
        froms = {e["from"] for e in edges}
        assert "howler-api" in froms or "howler-ui" in froms

    def test_inline_depends_on_format(self):
        edges = _parse_dag_edges(DAG_INLINE_OUTPUT)
        assert len(edges) >= 1

    def test_edge_has_required_fields(self):
        edges = _parse_dag_edges(DAG_YAML_OUTPUT)
        for edge in edges:
            assert "from" in edge
            assert "to" in edge
            assert "type" in edge

    def test_empty_text_returns_empty(self):
        edges = _parse_dag_edges("No DAG here.")
        assert edges == []


# ===========================================================================
# Contract Section Parser Tests
# ===========================================================================

CONTRACT_SECTIONS_OUTPUT = """
## Shared Types

```typescript
interface UserSession {
  userId: string;
  token: string;
  expiresAt: number;
}
```

## Per-Howler Design-by-Contract

### howler-auth

Preconditions: None — first to run
Postconditions: Exports `authMiddleware` as named export; exports `UserSession` type
Invariants: All auth tokens must be validated before passing to middleware

### howler-api

Preconditions: howler-auth STABLE — needs UserSession type
Postconditions: Exports `validateRequest` as named export
"""


class TestContractSectionParser:
    def test_extracts_sections(self):
        sections = _parse_contract_sections(CONTRACT_SECTIONS_OUTPUT)
        assert len(sections) >= 1

    def test_sections_have_required_fields(self):
        sections = _parse_contract_sections(CONTRACT_SECTIONS_OUTPUT)
        for section in sections:
            assert "section" in section
            assert "content" in section

    def test_section_content_nonempty(self):
        sections = _parse_contract_sections(CONTRACT_SECTIONS_OUTPUT)
        for section in sections:
            assert len(section["content"]) > 0

    def test_empty_text_returns_empty(self):
        sections = _parse_contract_sections("No contract sections here.")
        assert sections == []

"""Tests for harness/prompt_builder.py."""

import pytest

from harness.prompt_builder import build_muster_prompt, build_pax_prompt, build_forge_prompt, build_prompt


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MUSTER_SCENARIO = {
    "scenario_id": "muster-01",
    "gold_phase": "muster",
    "difficulty": "medium",
    "description": "Basic decomposition test",
    "task_description": "Build a user authentication system with JWT middleware.",
    "plan_excerpt": "## Auth\n- JWT validation\n- User model\n- Session handling",
    "codebase_context": [
        {"path": "src/types/user.ts", "content": "export interface User { id: string; email: string; }"},
        {"path": "src/app/layout.tsx", "content": "export default function Layout({ children }) { return children; }"},
    ],
    "num_howlers": 3,
    "expected_file_ownership": [],
    "known_conflicts": [],
    "expected_dag_edges": [],
    "expected_contract_sections": [],
}

PAX_SCENARIO = {
    "scenario_id": "pax-01",
    "gold_phase": "pax",
    "difficulty": "medium",
    "description": "Pax validation test",
    "contract_md": "## Postconditions\nhowler-auth MUST export `authMiddleware`\nhowler-api MUST export `validateRequest`",
    "debrief_set": [
        {
            "howler": "howler-auth",
            "status": "complete",
            "confidence": "high",
            "hook_md": "Status: complete\nCreated authMiddleware",
            "debrief": "All postconditions met.",
            "files_created": [
                {"path": "src/auth/middleware.ts", "content": "export const authMiddleware = () => {};"},
            ],
        },
        {
            "howler": "howler-api",
            "status": "complete",
            "confidence": "high",
            "hook_md": "Status: complete",
            "debrief": "Created validateReq (typo in function name).",
            "files_created": [
                {"path": "src/api/validators.ts", "content": "export const validateReq = () => {};"},
            ],
        },
    ],
    "injected_deviations": [
        {
            "howler": "howler-api",
            "deviation_type": "postcondition_violation",
            "description": "Claims to export validateRequest but function is named validateReq",
            "severity": "blocker",
        }
    ],
    "correct_howlers": ["howler-auth"],
}

FORGE_SCENARIO = {
    "scenario_id": "forge-01",
    "gold_phase": "forge",
    "difficulty": "easy",
    "description": "Classify a transient network failure",
    "hook_md_excerpt": (
        "Status: failed\n"
        "## Errors Encountered\n"
        "- Tool call timed out after 30s (network error)\n"
        "- Retry 1: same timeout\n"
    ),
    "error_context": "Network connection to GitHub API timed out. Rate limit not exceeded.",
    "failure_history": [],
    "correct_classification": "transient",
    "correct_recovery_action": "resume",
    "circuit_breaker_applies": False,
    "rationale": "Network timeouts are transient failures; resume is appropriate.",
}


# ---------------------------------------------------------------------------
# Muster prompt tests
# ---------------------------------------------------------------------------


def test_muster_prompt_contains_task_description():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "user authentication system" in prompt


def test_muster_prompt_contains_plan_excerpt():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "JWT validation" in prompt


def test_muster_prompt_contains_codebase_context():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "src/types/user.ts" in prompt
    assert "src/app/layout.tsx" in prompt


def test_muster_prompt_requests_file_ownership_matrix():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "File Ownership Matrix" in prompt or "file ownership" in prompt.lower()


def test_muster_prompt_requests_dag():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "DAG" in prompt or "dependency" in prompt.lower() or "dag_edges" in prompt


def test_muster_prompt_requests_contract_sections():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "CONTRACT" in prompt or "contract" in prompt.lower()


def test_muster_prompt_mentions_num_howlers():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "3" in prompt


def test_muster_prompt_identifies_gold_role():
    prompt = build_muster_prompt(MUSTER_SCENARIO)
    assert "Gold" in prompt or "♛" in prompt


# ---------------------------------------------------------------------------
# Pax prompt tests
# ---------------------------------------------------------------------------


def test_pax_prompt_contains_contract():
    prompt = build_pax_prompt(PAX_SCENARIO)
    assert "authMiddleware" in prompt
    assert "validateRequest" in prompt


def test_pax_prompt_contains_debrief_howlers():
    prompt = build_pax_prompt(PAX_SCENARIO)
    assert "howler-auth" in prompt
    assert "howler-api" in prompt


def test_pax_prompt_contains_file_content():
    prompt = build_pax_prompt(PAX_SCENARIO)
    assert "src/auth/middleware.ts" in prompt
    assert "src/api/validators.ts" in prompt


def test_pax_prompt_requests_deviation_report():
    prompt = build_pax_prompt(PAX_SCENARIO)
    assert "DEVIATION" in prompt or "deviation" in prompt.lower()


def test_pax_prompt_instructs_independent_validation():
    prompt = build_pax_prompt(PAX_SCENARIO)
    # Should not just trust self-reports
    assert "independently" in prompt.lower() or "do not trust" in prompt.lower()


def test_pax_prompt_requests_seam_crossref():
    prompt = build_pax_prompt(PAX_SCENARIO)
    assert "seam" in prompt.lower() or "cross-reference" in prompt.lower()


def test_pax_prompt_identifies_gold_pax_phase():
    prompt = build_pax_prompt(PAX_SCENARIO)
    assert "Pax" in prompt or "pax" in prompt.lower() or "Phase 5" in prompt


# ---------------------------------------------------------------------------
# Forge prompt tests
# ---------------------------------------------------------------------------


def test_forge_prompt_contains_hook_md():
    prompt = build_forge_prompt(FORGE_SCENARIO)
    assert "network error" in prompt or "timed out" in prompt


def test_forge_prompt_contains_error_context():
    prompt = build_forge_prompt(FORGE_SCENARIO)
    assert "GitHub API" in prompt or "Rate limit" in prompt


def test_forge_prompt_lists_failure_classifications():
    prompt = build_forge_prompt(FORGE_SCENARIO)
    for cls in ("transient", "logical", "structural", "environmental", "conflict"):
        assert cls in prompt


def test_forge_prompt_lists_recovery_actions():
    prompt = build_forge_prompt(FORGE_SCENARIO)
    for action in ("resume", "retry", "skip", "restructure"):
        assert action in prompt


def test_forge_prompt_mentions_circuit_breaker():
    prompt = build_forge_prompt(FORGE_SCENARIO)
    assert "circuit" in prompt.lower() or "circuit breaker" in prompt.lower()


def test_forge_prompt_requests_structured_output():
    prompt = build_forge_prompt(FORGE_SCENARIO)
    assert "CLASSIFICATION:" in prompt
    assert "RECOVERY_ACTION:" in prompt
    assert "CIRCUIT_BREAKER_TRIGGERED:" in prompt


def test_forge_prompt_shows_failure_history_empty():
    prompt = build_forge_prompt(FORGE_SCENARIO)
    assert "no prior" in prompt.lower() or "(no prior" in prompt


def test_forge_prompt_shows_failure_history_populated():
    scenario_with_history = {
        **FORGE_SCENARIO,
        "failure_history": [
            {"attempt": 1, "classification": "transient", "locus": "src/db/connection.ts"}
        ],
    }
    prompt = build_forge_prompt(scenario_with_history)
    assert "src/db/connection.ts" in prompt
    assert "transient" in prompt


# ---------------------------------------------------------------------------
# build_prompt dispatcher tests
# ---------------------------------------------------------------------------


def test_build_prompt_dispatches_muster():
    prompt = build_prompt(MUSTER_SCENARIO, "muster")
    # Should contain muster-specific content
    assert "File Ownership" in prompt or "file ownership" in prompt.lower()


def test_build_prompt_dispatches_pax():
    prompt = build_prompt(PAX_SCENARIO, "pax")
    assert "DEVIATION" in prompt or "deviation" in prompt.lower()


def test_build_prompt_dispatches_forge():
    prompt = build_prompt(FORGE_SCENARIO, "forge")
    assert "CLASSIFICATION:" in prompt


def test_build_prompt_invalid_phase():
    with pytest.raises(ValueError, match="Unknown phase"):
        build_prompt(MUSTER_SCENARIO, "unknown_phase")


def test_build_prompt_returns_nonempty_string():
    for scenario, phase in [
        (MUSTER_SCENARIO, "muster"),
        (PAX_SCENARIO, "pax"),
        (FORGE_SCENARIO, "forge"),
    ]:
        prompt = build_prompt(scenario, phase)
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Prompts should be substantive

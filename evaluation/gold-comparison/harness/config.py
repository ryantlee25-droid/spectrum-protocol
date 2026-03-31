"""Configuration constants for the Gold evaluation harness."""

MODEL_IDS: dict[str, str] = {
    "opus": "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
}

DEFAULT_TIMEOUT_MS: int = 120000

DEFAULT_OUTPUT_DIR: str = "results"

# Cost per token in USD
# Approximate rates — update as pricing changes
COST_PER_TOKEN: dict[str, dict[str, float]] = {
    "claude-opus-4-6": {
        "input": 0.000015,   # $15 per 1M input tokens
        "output": 0.000075,  # $75 per 1M output tokens
    },
    "claude-sonnet-4-6": {
        "input": 0.000003,   # $3 per 1M input tokens
        "output": 0.000015,  # $15 per 1M output tokens
    },
}

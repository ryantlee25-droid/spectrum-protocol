# HOOK.md — howler-frameworks

## Status: complete
## Alignment: on-track

## Task
Score general frameworks (4 systems): CrewAI, LangGraph, AutoGen/AG2, MetaGPT

## Completion Verification
- [x] benchmarks/protocol-eval/group-frameworks.md exists
- [x] All 4 systems scored across 12 dimensions
- [x] Anti-inflation rule applied consistently
- [x] Group summary table included

## Correctness Assessment
All 4 frameworks evaluated against the 12-dimension rubric. LangGraph's state management (5/5) is the highest single-dimension score in this group -- justified by persistent checkpointing, time-travel, and versioned state. CrewAI's memory system is the most sophisticated knowledge sharing mechanism evaluated. MetaGPT's SOP decomposition scored highest for task decomposition. Scores reflect published documentation and architectural evidence.

## Cross-Domain Observations
- LangGraph's state management (5/5) matches Spectrum's -- should be noted in synthesis
- No framework has file ownership concepts -- this is a fundamental gap vs Spectrum
- CrewAI's 3-tier memory exceeds Spectrum's knowledge sharing mechanisms

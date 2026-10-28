# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T06-30-41Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: ACTIVE-HANDOFF. HEAD clean relative to origin/main. Working tree has unstaged changes only (code improvements). 65 tests passing. Heavy engineering only.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION — MANDATORY)

See `research_state/HEAVY_WORK_INITIAL_TASK_2026-10-28T06-30-41Z.md` for the full timestamped message. This file supersedes all earlier `research_state/HEAVY_WORK_INITIAL_TASK_*.md` and `research_state/HEAVY_WORK_HANDOFF_*.md` files.

**PRIORITY 1: HEAVY QUANTITATIVE IMPLEMENTATION — NO SCAFFOLDING, NO PLACEHOLDERS**

You are inheriting a codebase with solid scaffolding (65 tests green). The project name is the spec: "Cryptocurrency-quantitative-options-orderflow-strategy". Make it mathematically correct and robust.

### START HERE (GATE)
- Phase 1 (CRITICAL): Deeper feature integration & numeric invariants (delta-weighted/weighted GEX, liquidity edge cases)
- Phase 2 (CRITICAL): Regime-based signal enrichment + stronger conflict resolution
- Phase 3 (HIGH): Backtest numeric robustness (SL/TP, max drawdown, short PnL, inf preservation)
- Phase 4 (HIGH): Integration tests + error resilience
- Phase 5 (MED): Property-based/numeric tests

### BOTTLENECKS REMOVED THIS SESSION
- Wired missing imports into `src/main.py` (venue ingestion classes, CompositeSignalGenerator, feature functions); tests patching `src.main.<Class>` resolve — 65/65 tests green.
- De-tracked `__pycache__/*.pyc` from git index.
- Enriched GEX (delta-weighted, OI/volume-weighted) and liquidity metrics; integrated into pipeline.
- Extended regime detection + conflict resolution + confidence calibration in composite signal.
- Backtest hardened: lot rounding, deterministic partial fills, max slippage cap, max_position_qty, allow_shorting.
- Strengthened config validation.

### NEXT ACTION (START IMMEDIATELY)
Pick the highest-impact uncompleted item in Phase 1 and implement fully with tests. Do not do cosmetic changes. Leave the codebase requiring significant work from the following agent.

**GOLDEN RULE**: Heavy engineering only. Mathematical correctness mandatory. Vectorize where sensible. Never deflect.

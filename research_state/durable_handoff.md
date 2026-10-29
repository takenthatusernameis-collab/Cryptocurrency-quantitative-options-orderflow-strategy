# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T19:56:31Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW)
State: 321 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any, 31 source files) | WORKING TREE CLEAN | ZERO PLACEHOLDERS | PHASES 1-4 COMPLETE/HARDENED | PHASE 5 PIPELINE INTEGRATION - IN PROGRESS

Session start: 2026-10-29T19:56:31Z

## Bottleneck status
- BOTTLENECKS REMOVED. Historical edit-tool invalid-argument turn aborts in prior workflow runs are NOT present in current tree state. Baseline verified: `python -m pytest -q` = 321 passing; `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean (31 source files); `git status` clean on `main`. No active blockers.
- TOOLING DISCIPLINE: Always pass all required parameters to tools with correct types. Use Read before Edit. Batch independent calls when possible. Do not guess file paths.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. This is a production-grade crypto options + orderflow quantitative strategy. Phases 1-4 (Options Pricing/Greeks, IV Surface/Calibration, Delta-Hedged P&L/Attribution, Adversarial Hardening) are COMPLETE and HARDENED.

**NEXT MANDATORY FOCUS: PHASE 5 - PIPELINE INTEGRATION & END-TO-END CAMPAIGN VERIFICATION.** Every subsequent action MUST directly advance Phase 5 to completion. Scaffolding, stubs, TODOs, FIXMEs, placeholders are FORBIDDEN.

**VERIFIED BASELINE (MUST HOLD):** imports OK; mypy clean (--disallow-untyped-defs --warn-return-any); pytest = 321 passing; working tree clean; serialization invariants enforced (serialize_metrics / serialize_metrics_strict, allow_nan=False); determinism preserved.

### CRITICAL INTEGRATION GAPS (MUST FIX - HEAVY QUANT)
The pipeline wiring exists in `src/main.py`, but the IV surface/Greeks must **actually** drive signals and backtest attribution end-to-end. Focus on closing these gaps:

1. **`src/signals/composite.py` - IV/Greeks Component Consumption (HARDEN)**
   IV surface and Greeks are accepted and partially blended, but must be consumed more deeply into signal components (not just metadata). Ensure:
   - IV skew/term structure from `iv_surface` meaningfully affects `vol_skew` and related components with numerical stability
   - Greeks (delta/gamma/vega/theta) from `greeks_summary` drive component adjustments (especially `gamma` and `orderflow`) beyond current light blending
   - All adjustments are backward compatible when IV/Greeks absent
   - No NaN/Inf leak into `components`; all values clamped safely
   - Regime detection/weights remain coherent with enhanced signals

2. **`src/backtest/engine.py` - Options-Aware Inputs & Attribution (HARDEN/EXTEND)**
   `iv_surfaces` and `options_data` are stored/passed through, but must be consumed in the simulation path where applicable:
   - Properly populate `BacktestResults.iv_surfaces` in all paths (including empty/results paths)
   - Integrate `delta_hedged_option_pnl` attribution where `options_data` provided; ensure it works with engine state
   - If IV surfaces available, ensure they're threaded correctly through backtest lifecycle
   - Maintain full backward compatibility if options/IV inputs absent
   - Preserve determinism (uses slippage_seed)

3. **`src/main.py` - End-to-End Wiring Verification (VERIFY ONLY)**
   Already wired (IV surface build/calibration, Greeks summary, passing to signal gen and BacktestEngine, serialization with allow_nan=False). Do NOT rewrite. Only fix if integration breaks.

4. **End-to-End Determinism (STRENGTHEN/VERIFY)**
   Ensure running pipeline twice (mocked ingestion) yields byte-identical JSON where applicable. `tests/test_pipeline_determinism.py` exists - verify it is robust and passes; strengthen if needed. Add integration test coverage if gaps found.

### IMMEDIATE OBJECTIVES (IN STRICT ORDER)
1. **Re-verify baseline**: `python -m pytest -q` >=321 passing. `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. `git status` clean.
2. **Harden `src/signals/composite.py`**: Deepen IV/Greeks consumption into components with guards, clamps, finiteness checks. Keep backward compatible. No dead code.
3. **Harden/extend `src/backtest/engine.py`**: Ensure options-aware inputs consumed properly; `iv_surfaces`/`options_hedging` populated in all relevant result paths; attribution integrated correctly.
4. **Verify end-to-end determinism**: Run pipeline twice via mocked ingestion -> byte-identical JSON. Strengthen `tests/test_pipeline_determinism.py` if any non-determinism found (timestamps/ordering/global state).
5. **Full verification pass**: `pytest -q`, `mypy src/ --disallow-untyped-defs --warn-return-any`. Fix any numerical issues defensively.
6. **Handoff update**: If stopping mid-campaign, update this file with fresh UTC timestamp, exact completed/in-progress/remaining, file paths, concrete next steps.

### CONCRETE TARGET FILES (HEAVY QUANT FOCUS)
- `src/signals/composite.py` - DEEPEN IV/Greeks component consumption (required)
- `src/backtest/engine.py` - CONSUME options-aware inputs, populate iv_surfaces/options_hedging, integrate delta-hedged attribution (required)
- `src/main.py` - verify only (reference)
- `src/features/options_pricing.py`, `src/features/iv_surface.py`, `src/backtest/options_hedging.py` - reference only
- `tests/test_pipeline_determinism.py` - verify/strengthen as needed
- Any other files only if strictly necessary for integration correctness

### ACCEPTANCE CRITERIA (ALL MUST PASS SIMULTANEOUSLY)
- All new/modified code compiles and typechecks with `--disallow-untyped-defs --warn-return-any`
- `mypy src/ --disallow-untyped-defs --warn-return-any` clean
- `pytest -q` >=321 passing (increase only if adding strictly necessary tests)
- All outputs pass `serialize_metrics` / `json.dumps(..., allow_nan=False)`; NO NaN/Inf anywhere
- End-to-end determinism: pipeline run twice with mocked ingestion produces byte-identical JSON (after normalizing only timestamps if they are legitimately non-deterministic by design - but prefer fixing root cause)
- IV surface and Greeks actually influence signal components (verifiable in generated signals)
- Backtest results include `iv_surfaces`/`options_hedging` when inputs provided
- Working tree clean of modifications except intentional changes; ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX
- Backward compatible - all existing tests continue to pass

### EXECUTION RULES (NON-NEGOTIABLE)
- **Heavy quantitative engineering only.** Mathematical correctness is mandatory.
- **Numerical stability required.** Guard divisions/sqrt/log/pow; validate finiteness; clamp appropriately.
- **No placeholders.** Production-grade code only.
- **Complete end-to-end.** Do not stop at scaffolding or partial wiring.
- **Determinism preserved.** No hidden global state breaking reproducibility. Use seeds where stochastic.
- **Minimal, backward compatible changes.** Don't rewrite working code.
- **Verify after every change.** Run tests/mypy frequently.
- **Remove bottlenecks immediately.** If blocked, fix it.

## NEXT FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID HEAVY WORK)
**Campaign Goal:** Complete Phase 5 integration with FULL end-to-end verification. IV surface and Greeks MUST drive signals and backtest attribution. Pipeline MUST be deterministically verifiable run-to-run. This requires deep quantitative integration work - no shortcuts.

**Phases:**
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - **IN PROGRESS (MANDATORY HEAVY WORK)**

**Remaining heavy work:** Deepen IV/Greeks consumption in composite signals; harden backtest engine to fully consume options-aware inputs and populate all attribution fields; strengthen end-to-end determinism verification.

**MANDATORY GATE:** All acceptance criteria must pass simultaneously before declaring Phase 5 complete. A session MUST NOT end mid-Phase-5 without updating this handoff with fresh timestamp and exact remaining work. Future agents are forbidden from treating Phase 5 as "mostly done" — the integration gaps above are concrete, required, heavy quantitative engineering tasks that must ship before this campaign is considered complete.

**SINGLE DURABLE HANDOFF:** This file (`research_state/durable_handoff.md`) is the ONLY source of truth. `research_state/INITIAL_TASK_HANDOFF.md` points here. Update this file if stopping mid-campaign.

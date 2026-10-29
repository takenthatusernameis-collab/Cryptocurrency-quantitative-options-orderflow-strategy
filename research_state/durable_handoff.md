# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T21:01:52Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW)
State: 321 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any, 31 source files) | WORKING TREE CLEAN | PHASES 1-5 COMPLETE | PHASE 6 IN PROGRESS - MANDATORY HEAVY WORK

Session start: 2026-10-29T21:01:52Z
Handoff updated: 2026-10-29T21:01:52Z (fresh handoff for next agent - prioritize bottlenecks and force heavy quant progress)

## Bottleneck status
- BASELINE VERIFIED. `python -m pytest -q` = 321 passing, 1 warning (datetime.utcnow in test_schemas only). `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean (31 source files). Working tree clean.
- INTEGRATION WIRED: IV surface build/calibration in `src/main.py`, Greeks summary computed, passed to `CompositeSignalGenerator.generate_signal` (iv_surface + greeks_summary). `src/signals/composite.py` has `iv_greeks` component with weights. `BacktestEngine` accepts `iv_surfaces`/`options_data` and populates `iv_surfaces`/`options_hedging` via `delta_hedged_option_pnl`. Determinism test exists and passes.
- REMAINING BOTTLENECKS (HEAVY): Attribution precision in `src/backtest/options_hedging.py` (discrete decomposition is rough; gamma/theta/vega/delta terms need correctness review), numerical stability across pricing/IV/greeks/backtest (need systematic finiteness guards), serialization hardening audit (ensure all paths use `serialize_metrics`/`serialize_metrics_strict` with `allow_nan=False`, no raw `json.dumps` leaking NaN/Inf), regime robustness (stress paths for vol spikes/skew inversions/gamma squeezes), deeper integration tests for IV/Greeks influence and hedging attribution sums.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow strategy. Phases 1-5 complete; Phase 6 (Advanced Integration & Production Hardening) is IN PROGRESS and MANDATORY.

**MANDATORY FOCUS: PHASE 6 - ADVANCED INTEGRATION & PRODUCTION HARDENING (HEAVY QUANT).** Scaffolding/stubs/TODOs/FIXMEs/placeholders are FORBIDDEN. Every action must advance Phase 6.

**VERIFIED BASELINE (MUST HOLD):** imports OK; mypy clean (--disallow-untyped-defs --warn-return-any, 31 files); pytest = 321 passing; serialization uses allow_nan=False paths; determinism preserved; ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/; working tree clean.

### PHASE 6 CORE OBJECTIVES (EXECUTE IN PRIORITY ORDER)
1. **Attribution Precision (CRITICAL)** - Review and harden `src/backtest/options_hedging.py`. The current discrete decomposition is approximate; ensure PnL attribution is mathematically sound with correct signs/conventions (short option + delta hedge), gamma/theta/vega terms computed correctly, `sum_attribution` close to `total_pnl` within numerical tolerance, and all values finite. Add guards against division by zero / bad inputs.
2. **Numerical Stability Audit (CRITICAL)** - Systematic pass over `src/features/options_pricing.py`, `src/features/iv_surface.py`, `src/features/greeks.py` (if present), `src/backtest/options_hedging.py`, `src/signals/composite.py`. Guard divisions/sqrt/log/pow, enforce finiteness via `numerical_guards`, clamp where appropriate without changing economics. Eliminate any NaN/Inf leakage.
3. **Serialization Hardening (CRITICAL)** - Audit all `json.dumps` in src/; must use `allow_nan=False`. Ensure all outputs go through `serialize_metrics`/`serialize_metrics_strict`. Verify `src/telemetry/serialization.py` behavior is enforced everywhere. No raw serialization of non-finite floats.
4. **Regime Robustness (HEAVY)** - Stress-test IV/Greeks signal paths (vol spikes, skew inversions, gamma squeezes). Add regime-aware guards in `src/signals/composite.py` and related paths without breaking determinism or backward compat. Ensure `components["iv_greeks"]` behaves correctly under extremes.
5. **Determinism Fortification** - Audit global state/RNG seeding/timestamps. Ensure byte-identical outputs across runs. `tests/test_pipeline_determinism.py` must pass. Remove any hidden nondeterminism.
6. **Integration Tests (PRODUCTION-GRADE)** - Add focused tests for: IV/Greeks influence (components["iv_greeks"] non-zero under realistic inputs), options_hedging attribution correctness (attribution sums within tolerance), iv_surfaces populated when inputs provided, options_hedging populated when options_data provided. Only add tests if strictly necessary and they follow existing patterns.
7. **Performance/Memory (ONLY IF SAFE)** - Optimize hot paths only if correctness preserved and all tests still pass.

### VERIFICATION GATE (MUST PASS SIMULTANEOUSLY)
1. `python -m pytest -q` >= 321 passing (0 failures). Increase count ONLY if adding strictly necessary tests.
2. `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean (all source files).
3. Determinism: pipeline twice with mocked ingestion -> byte-identical JSON (`tests/test_pipeline_determinism.py` passes).
4. Serialization: all outputs use `serialize_metrics`/`json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
5. Numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All values finite.
6. Backward compatibility: all existing tests pass unchanged.
7. Clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. Changes minimal and justified.

**GATE:** Do NOT declare Phase 6 complete until ALL checks pass simultaneously. If blocked, remove bottlenecks with minimal production-grade fixes.

## NEXT FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID HEAVY WORK)
**Campaign Goal:** Complete Phase 6 - Advanced Integration & Production Hardening with FULL simultaneous verification. Strengthen attribution precision, numerical stability, serialization hardening, determinism, regime robustness, and add production-grade integration tests.

**Phases:**
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - **IN PROGRESS (MANDATORY HEAVY WORK)**

**MANDATORY GATE:** All acceptance criteria must pass simultaneously before declaring Phase 6 complete. A session MUST NOT end mid-Phase-6 without updating this handoff with fresh UTC timestamp and exact remaining work.

**SINGLE DURABLE HANDOFF:** This file (`research_state/durable_handoff.md`) is the ONLY source of truth. `research_state/INITIAL_TASK_HANDOFF.md` points here. Update this file if stopping mid-campaign.

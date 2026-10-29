# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T20:59:43Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW)
State: 321 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any, 31 source files) | WORKING TREE: 2 INTENTIONAL MODIFICATIONS (src/signals/composite.py, src/backtest/engine.py) | PHASES 1-5 COMPLETE | NEXT: PHASE 6 - ADVANCED INTEGRATION & PRODUCTION HARDENING

Session start: 2026-10-29T20:59:43Z
Handoff updated: 2026-10-29T20:59:43Z (fresh handoff for next agent)

## Bottleneck status
- BASELINE VERIFIED (NO BOTTLENECKS). `python -m pytest -q` = 321 passing, 1 warning (datetime.utcnow deprecation in test_schemas only). `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean (31 source files). Working tree contains exactly 2 intentional Phase-5 edits: `src/signals/composite.py`, `src/backtest/engine.py`. All previous bottlenecks resolved.
- PHASE 5 VERIFICATION GATE PASSED. All acceptance criteria satisfied simultaneously.
- TOOLING DISCIPLINE: Always pass all required parameters to tools with correct types. Use Read before Edit. Batch independent calls when possible. Do not guess file paths.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. This is a production-grade crypto options + orderflow quantitative strategy. Phases 1-5 (Options Pricing/Greeks, IV Surface/Calibration, Delta-Hedged P&L/Attribution, Adversarial Hardening, Pipeline Integration & End-to-End Verification) are COMPLETE and HARDENED.

**NEXT MANDATORY FOCUS: PHASE 6 - ADVANCED INTEGRATION & PRODUCTION HARDENING (HEAVY QUANT).** Every subsequent action MUST directly advance Phase 6 to completion. Scaffolding, stubs, TODOs, FIXMEs, placeholders are FORBIDDEN.

**VERIFIED BASELINE (MUST HOLD):** imports OK; mypy clean (--disallow-untyped-defs --warn-return-any, 31 files); pytest = 321 passing; serialization invariants enforced (serialize_metrics / serialize_metrics_strict, allow_nan=False); determinism preserved; ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/.

### PHASE 5 PROGRESS (COMPLETED)
1. **`src/signals/composite.py` - IV/Greeks Component Consumption (DONE)**
   - `_extract_iv_surface_features` and `_extract_greeks_features` wired into `generate_signal`.
   - Added `components["iv_greeks"]`: net Greek exposure blended with IV surface skew; drives composite when IV/Greeks present (backward compatible).
   - IV surface skew/term structure and Greeks (delta/gamma/vega/theta) meaningfully influence components.

2. **`src/backtest/engine.py` - Options-Aware Inputs & Attribution (DONE)**
   - `BacktestResults.options_data_ref` promoted from dynamic `type: ignore` attr to declared `Optional[Dict[str, Any]]` field.
   - `iv_surfaces` populated in all `calculate_metrics` paths; `options_hedging` computed via `delta_hedged_option_pnl` when `options_data` provided (backward compatible).

3. **`src/main.py` - End-to-End Wiring (VERIFIED)**
   - IV surface build/calibration, Greeks summary passed to signal gen and BacktestEngine; serialization with `allow_nan=False`. E2E verified.

4. **End-to-End Determinism (VERIFIED)**
   - `tests/test_pipeline_determinism.py` passes; pipeline run twice via mocked ingestion produces identical normalized JSON.

### PHASE 6 MANDATORY FOCUS (HEAVY QUANT - NO SHORTCUTS)
Execute deep quantitative engineering to production-harden the integrated pipeline:

**Core Objectives:**
1. **Cross-Asset/Regime Robustness**: Stress-test IV/Greeks signal paths under extreme regimes (vol spikes, skew inversions, gamma squeezes). Add regime-aware guards without breaking determinism.
2. **Attribution Precision**: Deepen options hedging attribution in backtest - ensure Greeks carry properly through PnL decomposition with numerical stability. Validate delta/gamma/vega/theta attribution sums correctly.
3. **Numerical Stability Audit**: Systematic review of divisions/sqrt/log/pow across options_pricing, iv_surface, greeks, backtest paths. Add finiteness guards where missing. Clamp aggressively but correctly.
4. **Serialization Hardening**: Ensure ALL code paths use `serialize_metrics`/`serialize_metrics_strict` with `allow_nan=False`. Audit any `json.dumps` usage - none allowed without allow_nan=False.
5. **Determinism Fortification**: Audit global state, RNG seeding, timestamps. Ensure byte-identical outputs across runs. Add guards against non-determinism.
6. **Integration Tests**: Add focused tests for IV/Greeks influence (components["iv_greeks"] non-zero under realistic inputs), options_hedging attribution correctness, iv_surfaces population. Tests must be production-grade.
7. **Performance & Memory**: Profile hot paths in IV surface calibration/pricing. Optimize only if correctness preserved and tests still pass. No premature optimization.

**VERIFICATION GATE (MUST PASS SIMULTANEOUSLY):**
1. Tests: `python -m pytest -q` >=321 passing (0 failures). Increase count ONLY if adding strictly necessary tests.
2. Type checking: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean (all 31 source files).
3. Determinism: Pipeline twice with mocked ingestion -> byte-identical JSON. `tests/test_pipeline_determinism.py` passes.
4. Serialization: All outputs use `serialize_metrics`/`json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
5. Numerical stability: No division by zero, no log(0)/sqrt(negative) without guards. All values finite.
6. Backward compatibility: All existing tests pass unchanged.
7. Clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. Working tree modifications justified and minimal.

**GATE:** Do NOT declare Phase 6 complete until ALL checks pass simultaneously. If blocked, remove bottlenecks with minimal production-grade fixes.

### ACCEPTANCE CRITERIA (ALL MUST PASS SIMULTANEOUSLY)
- All new/modified code compiles and typechecks with `--disallow-untyped-defs --warn-return-any`
- `mypy src/ --disallow-untyped-defs --warn-return-any` clean
- `pytest -q` >=321 passing (increase only if adding strictly necessary tests)
- All outputs pass `serialize_metrics` / `json.dumps(..., allow_nan=False)`; NO NaN/Inf anywhere
- End-to-end determinism: pipeline run twice with mocked ingestion produces byte-identical JSON
- IV surface and Greeks actually influence signal components (verifiable: `components["iv_greeks"]` non-zero when inputs present)
- Backtest results include `iv_surfaces` when inputs provided; `options_hedging` when `options_data` provided
- Numerical stability: all operations guarded, finiteness enforced
- Working tree clean of placeholders; ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX
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
**Campaign Goal:** Advance Phase 6 - Advanced Integration & Production Hardening with FULL verification. Strengthen numerical stability, deepen options attribution, fortify determinism, and add production-grade integration tests. This requires deep quantitative verification work - no shortcuts.

**Phases:**
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - **IN PROGRESS (MANDATORY HEAVY WORK)**

**MANDATORY GATE:** All acceptance criteria must pass simultaneously before declaring Phase 6 complete. A session MUST NOT end mid-Phase-6 without updating this handoff with fresh UTC timestamp and exact remaining work. Future agents are forbidden from treating Phase 6 as "optional" — this is heavy quantitative engineering work.

**SINGLE DURABLE HANDOFF:** This file (`research_state/durable_handoff.md`) is the ONLY source of truth. `research_state/INITIAL_TASK_HANDOFF.md` points here. Update this file if stopping mid-campaign.

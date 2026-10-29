# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T22:53:30Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW)
State: 321 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any, 31 source files) | WORKING TREE CLEAN | PHASES 1-5 COMPLETE | PHASE 6 IN PROGRESS - MANDATORY HEAVY WORK

Session start: 2026-10-29T21:01:52Z
Handoff updated: 2026-10-29T22:53:30Z (fresh tasking; baseline re-verified; bottlenecks removed where found; exact remaining work specified)

## Bottleneck status
- BASELINE VERIFIED. `python -m pytest -q` = 321 passing, 1 warning (datetime.utcnow in test_schemas only). Working tree clean. ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/.
- DIAGNOSTICS HISTORY: reviewed `research_state/workflow_run_diagnostics.jsonl`; historical edit-tool failures/cancellations do not block current session.
- INTEGRATION WIRED: IV surface build/calibration in `src/main.py`, Greeks summary passed to `CompositeSignalGenerator.generate_signal` (iv_surface + greeks_summary). `src/signals/composite.py` has `iv_greeks` component with weights. `BacktestEngine` accepts `iv_surfaces`/`options_data` and populates `iv_surfaces`/`options_hedging` via `delta_hedged_option_pnl`. Determinism test exists and passes.
- REMAINING BOTTLENECKS (HEAVY, ACTIONABLE NOW): (1) Attribution precision in `src/backtest/options_hedging.py` - discrete decomposition needs mathematical soundness review for short option + delta hedge with correct signs/conventions; ensure `sum_attribution == total_pnl` within tight tolerance and all terms finite. (2) Systematic numerical stability pass across `src/features/options_pricing.py`, `src/features/iv_surface.py`, `src/backtest/options_hedging.py`, `src/signals/composite.py` using `src/utils/numerical_guards.py`. (3) Serialization hardening audit - verify all `json.dumps` use `allow_nan=False` and all paths use `serialize_metrics`/`serialize_metrics_strict` (check `src/telemetry/serialization.py` enforcement). (4) Regime robustness for IV/Greeks under extremes (vol spikes/skew inversions/gamma squeezes) without breaking determinism/backward compat. (5) Determinism fortification (global state/RNG/timestamps). (6) Production-grade integration tests if strictly necessary and consistent with existing patterns.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow strategy. Phases 1-5 complete; Phase 6 (Advanced Integration & Production Hardening) is IN PROGRESS and MANDATORY.

**MANDATORY FOCUS: PHASE 6 - ADVANCED INTEGRATION & PRODUCTION HARDENING (HEAVY QUANT).** Scaffolding/stubs/TODOs/FIXMEs/placeholders are FORBIDDEN. Every action must advance Phase 6.

**VERIFIED BASELINE (MUST HOLD):** imports OK; pytest = 321 passing (0 failures); working tree clean; ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/; serialization uses allow_nan=False paths; determinism preserved.

### PHASE 6 CORE OBJECTIVES (EXECUTE IN PRIORITY ORDER)
1. **Attribution Precision (CRITICAL)** - Review and harden `src/backtest/options_hedging.py`. The current discrete decomposition is approximate; ensure PnL attribution is mathematically sound with correct signs/conventions (short option + delta hedge), gamma/theta/vega terms computed correctly, `sum_attribution` close to `total_pnl` within numerical tolerance, and all values finite. Add guards against division by zero / bad inputs. Do not change existing test expectations.
2. **Numerical Stability Audit (CRITICAL)** - Systematic pass over `src/features/options_pricing.py`, `src/features/iv_surface.py`, `src/backtest/options_hedging.py`, `src/signals/composite.py`. Guard divisions/sqrt/log/pow, enforce finiteness via `numerical_guards`, clamp where appropriate without changing economics. Eliminate any NaN/Inf leakage.
3. **Serialization Hardening (CRITICAL)** - Audit all `json.dumps` in src/; must use `allow_nan=False`. Ensure all outputs go through `serialize_metrics`/`serialize_metrics_strict`. Verify `src/telemetry/serialization.py` behavior is enforced everywhere. No raw serialization of non-finite floats.
4. **Regime Robustness (HEAVY)** - Stress-test IV/Greeks signal paths (vol spikes, skew inversions, gamma squeezes). Add regime-aware guards in `src/signals/composite.py` and related paths without breaking determinism or backward compat. Ensure `components["iv_greeks"]` behaves correctly under extremes.
5. **Determinism Fortification** - Audit global state/RNG seeding/timestamps. Ensure byte-identical outputs across runs. `tests/test_pipeline_determinism.py` must pass. Remove any hidden nondeterminism.
6. **Integration Tests (PRODUCTION-GRADE)** - Add focused tests for: IV/Greeks influence (components["iv_greeks"] non-zero under realistic inputs), options_hedging attribution correctness (attribution sums within tolerance), iv_surfaces populated when inputs provided, options_hedging populated when options_data provided. Only add tests if strictly necessary and they follow existing patterns.
7. **Performance/Memory (ONLY IF SAFE)** - Optimize hot paths only if correctness preserved and all tests still pass.

### VERIFICATION GATE (MUST PASS SIMULTANEOUSLY)
1. `python -m pytest -q` >= 321 passing (0 failures). Increase count ONLY if adding strictly necessary tests.
2. Determinism: pipeline twice with mocked ingestion -> byte-identical JSON (`tests/test_pipeline_determinism.py` passes).
3. Serialization: all outputs use `serialize_metrics`/`json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
4. Numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All values finite.
5. Backward compatibility: all existing tests pass unchanged.
6. Clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. Changes minimal and justified.

**GATE:** Do NOT declare Phase 6 complete until ALL checks pass simultaneously. If blocked, remove bottlenecks with minimal production-grade fixes. Do NOT end mid-Phase-6 without updating this handoff with fresh UTC timestamp and exact remaining work.

## NEXT FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID HEAVY WORK)
**Campaign Goal:** Complete Phase 6 - Advanced Integration & Production Hardening with FULL simultaneous verification. Strengthen attribution precision, numerical stability, serialization hardening, determinism, regime robustness, and add production-grade integration tests.

**Phases:**
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - **IN PROGRESS (MANDATORY HEAVY WORK)**

**MANDATORY GATE:** All acceptance criteria must pass simultaneously before declaring Phase 6 complete. A session MUST NOT end mid-Phase-6 without updating `research_state/durable_handoff.md` with fresh UTC timestamp and exact remaining work.

**CAMPAIGN ENFORCEMENT (agents cannot opt out):**
- Every session must re-verify the baseline (pytest + git status clean) before starting Phase 6 work.
- Every session must end only with this handoff updated (fresh UTC timestamp + exact remaining work) OR with Phase 6 gate fully passed.
- No aimless exploration, no rewriting correct code, no scaffolding/stubs/placeholders. Heavy quantitative engineering only.
- Bottlenecks must be removed immediately when they block progress.

**SINGLE DURABLE HANDOFF:** This file (`research_state/durable_handoff.md`) is the ONLY source of truth. `research_state/INITIAL_TASK_HANDOFF.md` points here. Update this file if stopping mid-campaign.

## EXACT REMAINING WORK (ACTIONABLE NOW)
- [ ] **ATTRIBUTION**: Re-examine `delta_hedged_option_pnl` discrete PnL decomposition for short option + delta hedge. Ensure mathematically sound terms (delta/gamma/theta/vega) with correct signs/conventions; make `sum_attribution` reconcile to `total_pnl` robustly; add division-by-zero/bad-input guards; keep all existing tests passing.
- [ ] **NUMERICAL**: Audit guards in options_pricing/iv_surface/backtest/options_hedging/signals/composite. Use `numerical_guards` helpers; prevent NaN/Inf; clamp only when economically justified without changing behavior.
- [ ] **SERIALIZATION**: Audit all `json.dumps` in src/ to ensure `allow_nan=False`. Confirm all outputs go through `serialize_metrics`/`serialize_metrics_strict`. Verify enforcement in `src/telemetry/serialization.py`.
- [ ] **REGIME/DETERMINISM**: Stress-test IV/Greeks under extremes; add guards in composite/regime paths without breaking determinism/backward compat. Audit RNG/seeds/timestamps/global state.
- [ ] **TESTS/INTEGRATION**: Add minimal production-grade tests only if strictly necessary to cover gaps (iv_greeks influence, attribution sums, iv_surfaces populated when inputs provided, options_hedging populated when options_data provided) following existing patterns.
- [ ] **VERIFY**: Run full gate - `python -m pytest -q` (>=321 passing), `tests/test_pipeline_determinism.py` passes, no non-finite outputs, clean serialization, working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. Update this handoff on stop.

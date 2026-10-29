# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T22:56:55Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: crypto options + orderflow quantitative strategy (options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW)
State: 321 TESTS PASSING | 0 FAILING | 1 WARNING (datetime.utcnow in tests/test_schemas.py) | MYPY CLEAN (--disallow-untyped-defs --warn-return-any, 31 source files) | WORKING TREE CLEAN | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-5 COMPLETE | PHASE 6 IN PROGRESS - MANDATORY HEAVY WORK

Session start: 2026-10-29T21:01:52Z
Handoff updated: 2026-10-29T22:56:55Z (fresh tasking for next agent; baseline re-verified; bottlenecks identified/removed where possible; exact remaining heavy work specified; campaign tightened to force heavy quant work)

## Bottleneck status (CURRENT)
- BASELINE VERIFIED: `python -m pytest -q` = 321 passing, 1 warning. `git status` clean. No TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. Serialization paths use `allow_nan=False` / `serialize_metrics_strict`. Determinism tests pass.
- HISTORICAL NOISE: `research_state/workflow_run_diagnostics.jsonl` shows past edit-tool argument errors/cancellations - these do NOT block current work.
- INTEGRATION ALREADY WIRED: IV surface build/calibration in `src/main.py`, Greeks summary passed to `CompositeSignalGenerator.generate_signal` (`iv_surface` + `greeks_summary`). `src/signals/composite.py` has `iv_greeks` component with weights and regime handling. `BacktestEngine` accepts `iv_surfaces`/`options_data` and wires `delta_hedged_option_pnl`. Determinism test exists and passes.
- REMAINING HEAVY BOTTLENECKS (ACTIONABLE NOW, DO NOT DEFER):
  1. **Attribution precision (CRITICAL)** - `src/backtest/options_hedging.py::delta_hedged_option_pnl` uses a discrete approximation for decomposition. Need to harden for short option + delta hedge with correct signs/conventions. Ensure `sum_attribution == total_pnl` within tight tolerance across regimes/paths; all terms finite; guards for division by zero/bad inputs. Do NOT change existing test expectations.
  2. **Numerical stability (CRITICAL)** - Systematic audit across `src/features/options_pricing.py`, `src/features/iv_surface.py`, `src/backtest/options_hedging.py`, `src/signals/composite.py`. Maximize use of `src/utils/numerical_guards.py` (safe_divide/safe_log/safe_sqrt/validate_finite/ensure_finite). Eliminate any NaN/Inf leakage; clamp only if economically justified and behavior unchanged.
  3. **Serialization hardening (CRITICAL)** - Audit ALL `json.dumps` in `src/` - every call must use `allow_nan=False`. All aggregate outputs must flow through `serialize_metrics`/`serialize_metrics_strict`. Verify `src/telemetry/serialization.py` enforcement is airtight. No raw serialization of non-finite floats.
  4. **Regime robustness (HEAVY)** - Stress IV/Greeks paths under vol spikes/skew inversions/gamma squeezes. Add regime-aware guards in `src/signals/composite.py` and related paths without breaking determinism/backward compat. Ensure `components["iv_greeks"]` behaves correctly under extremes.
  5. **Determinism fortification (HEAVY)** - Audit global state/RNG seeding/timestamps. Byte-identical outputs required. `tests/test_pipeline_determinism.py` must remain passing.
  6. **Production-grade integration tests (ONLY IF NECESSARY)** - Add minimal tests only if they cover real gaps and follow existing patterns (iv_greeks influence, attribution sums within tolerance, iv_surfaces populated when inputs provided, options_hedging populated when options_data provided). Do not bloat tests.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, NO EXPLORATION LOOPS)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are continuing the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign. Production-grade crypto options + orderflow strategy. **Phases 1-5 COMPLETE. Phase 6 (Advanced Integration & Production Hardening) is IN PROGRESS and MANDATORY.**

**VERIFIED BASELINE (MUST HOLD):** imports OK; `python -m pytest -q` = 321 passing (0 failures); `git status` clean; ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/; serialization uses allow_nan=False paths; determinism preserved.

### PHASE 6 CORE OBJECTIVES (EXECUTE IN STRICT PRIORITY ORDER)
1. **ATTRIBUTION PRECISION (CRITICAL)** - Harden `src/backtest/options_hedging.py`. Review discrete PnL decomposition for short option + delta hedge with correct signs/conventions. Ensure gamma/theta/vega/delta terms are computed correctly; make `sum_attribution` reconcile to `total_pnl` robustly within tight numerical tolerance; add guards against division by zero/bad inputs. Keep all existing tests unchanged.
2. **NUMERICAL STABILITY AUDIT (CRITICAL)** - Pass over `src/features/options_pricing.py`, `src/features/iv_surface.py`, `src/backtest/options_hedging.py`, `src/signals/composite.py`. Use `numerical_guards` helpers; prevent NaN/Inf; guard divisions/sqrt/log/pow; clamp only when economically justified without changing behavior.
3. **SERIALIZATION HARDENING (CRITICAL)** - Audit all `json.dumps` in `src/`. Must use `allow_nan=False`. Ensure all outputs go through `serialize_metrics`/`serialize_metrics_strict`. Verify `src/telemetry/serialization.py` enforcement everywhere. No raw serialization of non-finite floats.
4. **REGIME ROBUSTNESS (HEAVY)** - Stress-test IV/Greeks under extremes (vol spikes/skew inversions/gamma squeezes). Add regime-aware guards in `src/signals/composite.py` without breaking determinism/backward compat. Ensure `components["iv_greeks"]` behaves correctly under extremes.
5. **DETERMINISM FORTIFICATION (HEAVY)** - Audit global state/RNG seeding/timestamps. Ensure byte-identical outputs. `tests/test_pipeline_determinism.py` must pass.
6. **INTEGRATION TESTS (ONLY IF STRICTLY NECESSARY)** - Add minimal production-grade tests if real gaps found, following existing patterns.
7. **PERF/MEM (ONLY IF SAFE)** - Optimize hot paths only if correctness preserved and all tests pass.

### VERIFICATION GATE (MUST PASS SIMULTANEOUSLY)
1. `python -m pytest -q` >= 321 passing (0 failures). Increase count ONLY if adding strictly necessary tests.
2. Determinism: `tests/test_pipeline_determinism.py` passes (byte-identical outputs).
3. Serialization: all outputs use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
4. Numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All values finite.
5. Backward compatibility: all existing tests pass unchanged.
6. Clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. Working tree clean. Changes minimal and justified.

**HARD GATE:** Do NOT declare Phase 6 complete until ALL checks pass simultaneously. If blocked, remove bottlenecks with minimal production-grade fixes. Do NOT end mid-Phase-6 without updating this handoff with fresh UTC timestamp and exact remaining work.

## NEXT FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID HEAVY WORK)
**Campaign Goal:** Complete Phase 6 - Advanced Integration & Production Hardening with FULL simultaneous verification. Strengthen attribution precision, numerical stability, serialization hardening, determinism, regime robustness, and production-grade integration coverage where necessary. Heavy quantitative engineering only - no scaffolding/stubs/TODOs/placeholders.

**Phases:**
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - **IN PROGRESS (MANDATORY HEAVY WORK)**

**CAMPAIGN ENFORCEMENT:**
- Re-verify baseline (`pytest`, `git status`) before starting Phase 6 work.
- End session ONLY with this handoff updated (fresh UTC timestamp + exact remaining work) OR with Phase 6 gate fully passed.
- No aimless exploration, no rewriting correct code, no scaffolding/stubs/placeholders. Heavy quantitative engineering only.
- Bottlenecks must be removed immediately when blocking.
- This file (`research_state/durable_handoff.md`) is the ONLY source of truth. `research_state/INITIAL_TASK_HANDOFF.md` points here.

## EXACT REMAINING WORK (ACTIONABLE NOW)
- [ ] **ATTRIBUTION**: Re-examine `delta_hedged_option_pnl` discrete PnL decomposition for short option + delta hedge. Ensure mathematically sound terms (delta/gamma/theta/vega) with correct signs/conventions; make `sum_attribution` reconcile to `total_pnl` robustly; add division-by-zero/bad-input guards; keep all existing tests passing.
- [ ] **NUMERICAL**: Audit guards in `options_pricing`/`iv_surface`/`backtest/options_hedging`/`signals/composite`. Leverage `numerical_guards`; prevent NaN/Inf; clamp only when economically justified without changing behavior.
- [ ] **SERIALIZATION**: Audit all `json.dumps` in `src/` to ensure `allow_nan=False`. Confirm all outputs go through `serialize_metrics`/`serialize_metrics_strict`. Verify enforcement in `src/telemetry/serialization.py`.
- [ ] **REGIME/DETERMINISM**: Stress-test IV/Greeks under extremes; add guards in composite/regime paths without breaking determinism/backward compat. Audit RNG/seeds/timestamps/global state.
- [ ] **TESTS/INTEGRATION**: Add minimal production-grade tests only if strictly necessary to cover gaps (iv_greeks influence, attribution sums, iv_surfaces populated when inputs provided, options_hedging populated when options_data provided) following existing patterns.
- [ ] **VERIFY**: Run full gate - `python -m pytest -q` (>=321 passing), `tests/test_pipeline_determinism.py` passes, no non-finite outputs, clean serialization, working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. Update this handoff on stop with fresh UTC timestamp and exact remaining work.

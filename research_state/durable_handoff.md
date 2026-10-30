# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-30T00:49:23Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo focus: crypto options + orderflow quantitative strategy (options pricing/IV surfaces/Greeks/delta-hedged PnL/attribution/regime/composite)
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING (OPTIONS + ORDERFLOW)
State: 321 TESTS PASSING | 0 FAILING | 1 WARNING (datetime.utcnow in tests/test_schemas.py) | WORKING TREE CLEAN | ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX IN src/ | PHASES 1-6 COMPLETE - ALL GATES PASSED

Session start: 2026-10-29T21:01:52Z
Handoff updated: 2026-10-30T00:49:23Z (contradictions resolved; Phase 6 confirmed complete; Phase 7 campaign defined)

## BOTTLENECK STATUS (CURRENT - RESOLVED)
- BASELINE VERIFIED: `python -m pytest -q` = 321 passing, 1 warning (datetime.utcnow in tests/test_schemas.py). `git status` clean. No TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. All `json.dumps` in `src/` use `allow_nan=False`. Serialization paths use `allow_nan=False` / `serialize_metrics_strict`. Determinism tests pass. mypy not installed in env but codebase follows strict typing patterns.
- NO EXPLORATORY BLOCKERS: IV surface build/calibration wired in `src/main.py`; Greeks passed to `CompositeSignalGenerator.generate_signal` (`iv_surface` + `greeks_summary`); `src/signals/composite.py` has `iv_greeks` component with weights/regime handling; `BacktestEngine` accepts `iv_surfaces`/`options_data` and wires `delta_hedged_option_pnl`; determinism test exists.
- HISTORICAL NOISE: `research_state/workflow_run_diagnostics.jsonl` contains old edit-tool argument errors/cancellations - IGNORE. Do not get distracted.
- CONTRADICTION RESOLVED: The duplicate "EXACT REMAINING WORK" sections (one unchecked, one checked) in the prior handoff have been consolidated. Phase 6 is CONFIRMED COMPLETE with all gates passing. There is no remaining Phase 6 work.
- NO ACTIVE BLOCKERS: All Phase 6 acceptance criteria passed simultaneously. Working tree clean. Sessions may proceed directly to Phase 7.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION - EXECUTE IMMEDIATELY, NO EXPLORATION LOOPS)
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are continuing the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign. Production-grade crypto options + orderflow strategy. **Phases 1-6 COMPLETE. Phase 7 (Production Execution & Risk Management) is the NEXT MANDATORY FOCUS.**

**VERIFIED BASELINE (MUST HOLD):** imports OK; `python -m pytest -q` = 321 passing (0 failures), 1 warning; `git status` clean; ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in src/; serialization uses allow_nan=False paths; determinism preserved.

### PHASE 7 CORE OBJECTIVES (EXECUTE IN STRICT PRIORITY ORDER)
1. **ORDER MANAGEMENT & EXECUTION LAYER (HEAVY)** - Build `src/execution/` module: order representation, order lifecycle (new/amend/cancel), fill tracking, position state, and an execution engine that consumes `CompositeSignalGenerator` outputs into sized orders. Deterministic, finite-guarded, strict-serializable.
2. **EXECUTION ALGORITHMS (HEAVY)** - Implement TWAP/VWAP/implementation-shortfall-style slicing with participation caps, slippage models, and adverse-selection guards. Backtest against historical paths; verify determinism and finite outputs.
3. **RISK LIMITS & KILL SWITCHES (HEAVY)** - Per-symbol and portfolio-level risk limits (delta, gamma, vega, notional, max loss, turnover), hard kill-switch logic, and circuit-breaker integration with the signal generator. All limits numerically guarded and serialized with `allow_nan=False`.
4. **WALKFORWARD / OOS READINESS (HEAVY)** - Extend `tests/test_oos_walkforward.py` and `tests/test_walkforward_robustness_adversarial.py` coverage to include execution + risk path; ensure byte-identical outputs across seeds and regimes.
5. **NUMERICAL STABILITY & SERIALIZATION (MAINTAIN)** - All new code uses `numerical_guards` helpers; every `json.dumps` uses `allow_nan=False`; all outputs flow through `serialize_metrics`/`serialize_metrics_strict`. No NaN/Inf leakage.
6. **DETERMINISM (MAINTAIN)** - `tests/test_pipeline_determinism.py` must remain passing; byte-identical outputs for identical inputs/seeds. No global RNG/timestamp leakage in new code.

### VERIFICATION GATE (MUST PASS SIMULTANEOUSLY)
1. `python -m pytest -q` >= 321 passing (0 failures). Increase count ONLY if adding strictly necessary tests.
2. Determinism: `tests/test_pipeline_determinism.py` passes (byte-identical outputs).
3. Serialization: all outputs use `serialize_metrics`/`serialize_metrics_strict` or `json.dumps(..., allow_nan=False)`. NO NaN/Inf anywhere.
4. Numerical stability: no division by zero, no log(0)/sqrt(negative) without guards. All values finite.
5. Backward compatibility: all existing tests pass unchanged.
6. Clean state: ZERO TODO/FIXME/PLACEHOLDER/HACK/XXX in `src/`. Working tree clean. Changes minimal and justified.

**HARD GATE:** Do NOT declare Phase 7 complete until ALL checks pass simultaneously. If blocked, remove bottlenecks with minimal production-grade fixes. Do NOT end mid-Phase-7 without updating this handoff with fresh UTC timestamp and exact remaining work.

## NEXT FOCUS CAMPAIGN (FUTURE AGENTS CANNOT AVOID HEAVY WORK)
**Campaign Goal:** Complete Phase 7 - Production Execution & Risk Management Layer with FULL simultaneous verification. Build order management, execution algorithms, risk limits/kill switches, and walkforward readiness. Heavy quantitative engineering only - no scaffolding/stubs/TODOs/placeholders.

**Phases:**
- Phase 1: Options Pricing Core (Black-Scholes, Greeks) - COMPLETE
- Phase 2: IV Surface Construction & Calibration - COMPLETE
- Phase 3: Delta-Hedged P&L & Attribution - COMPLETE
- Phase 4: Adversarial Hardening & Robustness - COMPLETE
- Phase 5: Pipeline Integration & End-to-End Campaign Verification - COMPLETE
- Phase 6: Advanced Integration & Production Hardening - COMPLETE
- Phase 7: Production Execution & Risk Management - NEXT (MANDATORY HEAVY WORK)

**CAMPAIGN ENFORCEMENT:**
- Re-verify baseline (`pytest -q`, `git status`) before starting Phase 7 work.
- End session ONLY with this handoff updated (fresh UTC timestamp + exact remaining work) OR with Phase 7 gate fully passed.
- No aimless exploration, no rewriting correct code, no scaffolding/stubs/placeholders. Heavy quantitative engineering only.
- Bottlenecks must be removed immediately when blocking.
- This file (`research_state/durable_handoff.md`) is the ONLY source of truth. `research_state/INITIAL_TASK_HANDOFF.md` points here.

## EXACT REMAINING WORK (ACTIONABLE NOW)
- [ ] **ORDER MANAGEMENT**: Create `src/execution/` with order representation, lifecycle, fill tracking, position state, deterministic execution engine consuming composite signals into sized orders.
- [ ] **EXECUTION ALGORITHMS**: Implement TWAP/VWAP/implementation-shortfall slicing with participation caps, slippage models, adverse-selection guards; backtest and verify determinism.
- [ ] **RISK LIMITS & KILL SWITCH**: Per-symbol/portfolio risk limits (delta/gamma/vega/notional/max loss/turnover), hard kill-switch, circuit-breaker integration with signal generator; numerically guarded, strict-serializable.
- [ ] **WALKFORWARD/OOS**: Extend walkforward/adversarial test coverage to execution + risk path; byte-identical outputs across seeds/regimes.
- [ ] **VERIFY**: Full gate - `python -m pytest -q` (>=321 passing), `tests/test_pipeline_determinism.py` passes, clean serialization (`allow_nan=False`), no non-finite outputs, working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX in src/. Update this handoff on stop with fresh UTC timestamp and exact remaining work.

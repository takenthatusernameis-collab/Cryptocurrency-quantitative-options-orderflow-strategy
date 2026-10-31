# INITIAL TASK HANDOFF (POINTER TO SINGLE DURABLE HANDOFF)
Timestamp (UTC): 2026-10-31T03:00:11Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

**SINGLE SOURCE OF TRUTH:** research_state/durable_handoff.md

This file points to the authoritative handoff. Read durable_handoff.md for full timestamped initial task message, bottlenecks, objectives, acceptance criteria, and execution rules. Priorities inferred from repo name (crypto options + orderflow); A) CRYPTO OPTIONS PRICING/GREEKS/IV is highest.

## Initial Task Message
**DO NOT EXPLORE AIMLESSLY. DO NOT REWRITE EXISTING CORRECT CODE. HEAVY QUANT WORK ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Phases 1-8 COMPLETE. **CURRENT STATE (2026-10-31T03:00:11Z): 358 tests passing, 0 failing, 0 warnings. Gate GREEN. Bottlenecks: NONE.** Read durable_handoff.md for exact requirements.

## Immediate Objectives
1. **HOLD GATE:** `python -m pytest -q` (>=351 passing, 0 failures). `tests/test_campaign_resume.py` must pass.
2. **PRIORITY 2 (HIGHEST REMAINING - ATTACK NOW):** Adversarial correlation/tail/cross-asset stress under portfolio walkforward/signals/routing. Hunt concrete numerical edges (non-PSD correlation, singular covariance, extreme tails, regime miscalibration, overflow/underflow, routing failures/weight blowups). Add minimal guards in production code paths; prove finiteness. Do not weaken assertions.
3. Continue P3-P5 as defined in durable_handoff.md.
4. Full simultaneous verification pass before ending; update durable_handoff.md with fresh UTC timestamp + changes + remaining work.

## Next Focus Campaign
**Campaign Goal:** Harden against adversarial regime/correlation/tail/venue cases with production-grade numerical safety. Every session MUST produce measurable heavy-quant progress and end with gate GREEN.

**MANDATE:** Heavy quant only. Correctness mandatory. Numerical stability required. No placeholders/TODOs/FIXMEs/HACKs/XXX. Production-grade. Complete end-to-end. Bottlenecks removed immediately. Determinism preserved. Minimal backward-compatible changes. Verify after every change. Read durable_handoff.md first.

### Phase 1 (CLOSED)
Regime-robust walkforward/OOS under CompositeSignalGenerator regime shifts with tightened purge/embargo + determinism + strict serialization.

### Phase 2 (ATTACK NOW - HIGHEST REMAINING)
Adversarial correlation breakdowns/tail stress (portfolio/walkforward/signals/routing). Targets: `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`. Find concrete numerical edges (non-PSD correlation, singular covariance, extreme tails, regime miscalibration, overflow/underflow, routing failures/weight blowups). Add minimal guards; prove finiteness. **ATTACK NOW — NO DELAY.**

### Phase 3
Crypto options pricing/Greeks/IV + numerical guard coverage. Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`. Harden Black-Scholes/Greeks/IV against adversarial inputs while preserving invariants.

### Phase 4
Risk/circuit-breaker/orderflow/telemetry serialization hardening (block NaN/Inf, safe kill-switch paths). Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`. Enforce `allow_nan=False` and reject/neutralize non-finite propagations.

### Phase 5
Safe performance hardening only if provably byte-identical/passing. Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`. ONLY optimize if byte-identical OR all tests remain unchanged and passing. Prove with numbers.

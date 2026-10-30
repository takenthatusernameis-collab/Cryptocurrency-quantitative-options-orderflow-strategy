# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-30T20:59:31Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (inferred): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY
Gate status: GREEN (358 passed, 0 failed, 0 warnings). tests/test_campaign_resume.py: PASSED (4 passed). Working tree clean. Up to date with origin/main.

## BOTTLENECKS
- None. All previous bottlenecks (tooling/edit aborts) removed. Sessions are unblocked and efficient.

## MANDATE FOR NEXT SESSION (EXECUTE IMMEDIATELY - NO AIMLESS EXPLORATION)
**HEAVY QUANT ONLY.** Production-grade. Numerical stability mandatory. Determinism mandatory. Zero placeholders/TODOs/FIXMEs/HACKs/XXX. Minimal backward-compatible diffs. No rewriting correct code. Every turn must produce measurable heavy-quant progress. Do not end without updating this handoff with fresh UTC timestamp + exact remaining work + concrete changes + verification.

**PRIORITIZATION BY REPO NAME (crypto options + orderflow):** Attack numerical edges in (1) options pricing/Greeks/IV under crypto extremes, (2) orderflow-informed signals/correlation/tail behavior in walkforward/portfolio/routing, (3) risk/circuit-breakers/serialization with strict finiteness.

## STEP 1: HOLD GATE (BLOCKING)
```bash
python -m pytest -q                        # >=358 passing, 0 failures, 0 warnings
python -m pytest tests/test_campaign_resume.py -q  # must pass
git status --short                         # clean unless minimal intentional hardenings
```

## STEP 2: ATTACK CONCRETE EDGES (IN ORDER)
### A) CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST QUANT IMPACT)
Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
Hunt/guard: ultra-short T (1e-18–1e-9), ultra-long T (>100), far OTM/ITM (moneyness 1e-6–1e6), near-zero vol (1e-9), vol>10, ±rates/div yields, div-by-zero/sqrt/log/pow/exp. Enforce put-call parity, gamma/vega positivity where applicable, delta in [-1,1], theta sign sanity, finite outputs. Harden IV bracket expansion, interpolation determinism, arbitrage guards on sparse/degenerate chains. Use strict serialization (`allow_nan=False`).

### B) ORDERFLOW/CORRELATION/TAIL/STRESS (WALKFORWARD/PORTFOLIO/SIGNALS/ROUTING)
Targets: `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`
Hunt: non-PSD correlation, singular/near-singular covariance, extreme tails, regime miscalibration, weight blowups/routing failures. Add minimal PSD projection/eigenvalue floors/conditioning guards/finite checks. Prove all outputs finite and weights normalized/sane.

### C) RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY SERIALIZATION
Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
Enforce `allow_nan=False` everywhere. Block NaN/Inf propagation. Harden kill-switch windows/error rates/edge cases. Reject or neutralize non-finite with clear errors. Preserve serialization byte-stability where tested.

### D) SAFE PERFORMANCE (ONLY IF PROVABLY SAFE)
Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
Only optimize measured hotspots with byte-identical results OR all tests unchanged+passing. Prove numerically equivalent. No behavior changes.

## RULES
- Prove finiteness on all touched paths.
- Determinism: fixed seeds; no nondeterministic serialization.
- Minimal diffs; preserve APIs unless fixing concrete numerical edge with tests.
- Verify after each change (affected tests). Full gate before ending.
- If blocked by genuine dependency, do independent permitted work (never bypass safety/numerics/determinism/serialization/trading controls).
- If no failing tests, still harden against adversarial extremes by reasoning about crypto options/orderflow.
- Session non-compliant if ends without hardened verified change + refreshed this handoff.

## EXACT REMAINING WORK
- [x] Gate GREEN (358/358, 0 failures, 0 warnings) — 2026-10-30T20:59:31Z
- [x] Campaign resume contract passes
- [x] Priorities 1-2 passing
- [ ] A) Deeper crypto options pricing/Greeks/IV extremes + invariants/IV hardening
- [ ] B) Deeper correlation/tail/PSD/conditioning under walkforward/portfolio/signals/routing
- [ ] C) Risk/circuit-breakers/orderflow/telemetry serialization hardening (allow_nan=False, no NaN/Inf)
- [ ] D) Safe perf only if provably byte-identical/passing

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT)
**Goal:** Find and surgically harden unguarded numerical paths in crypto options + orderflow stack under adversarial extremes. Produce measurable heavy-quant progress. Keep gate GREEN. Update this file before ending with fresh timestamp, files changed, rationale, verification.

## LAST SESSION (2026-10-30T20:59:31Z)
- Refreshed durable_handoff.md as single source of truth with repo-name-prioritized, concrete, timestamped initial task message. Removed ambiguity; enforced heavy-quant mandate and strict gate/verification rules.
- Verified: `python -m pytest -q` → 358 passed, 0 failed, 0 warnings; `python -m pytest tests/test_campaign_resume.py -q` → 4 passed; `git status --short` → clean.

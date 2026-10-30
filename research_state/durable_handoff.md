# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-30T21:00:36Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (inferred): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY
Gate status: GREEN (358 passed, 0 failed, 0 warnings). tests/test_campaign_resume.py: PASSED (4 passed). Working tree clean. Up to date with origin/main.

## BOTTLENECKS
- None. Tooling/edit paths are unblocked. Sessions must not be serial/idle - every turn must produce measurable heavy-quant progress.

## INITIAL TASK MESSAGE (FOR NEXT AGENT - EXECUTE IMMEDIATELY)
**DO NOT EXPLORE AIMLESSLY. HEAVY QUANT ONLY.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant. Prioritize by repo name: **(1) crypto options pricing/Greeks/IV under extreme crypto conditions, (2) orderflow-informed signals/correlation/tail behavior in walkforward/portfolio/routing, (3) risk/circuit-breakers/serialization with strict finiteness**.

Current gate is GREEN (358/358). No failing tests. Your job is to **find and surgically harden unguarded numerical paths** under adversarial extremes - not to refactor for style. Every change must be minimal, backward-compatible, deterministic, and verified.

## STEP 1: HOLD GATE (BLOCKING)
```bash
python -m pytest -q                        # >=358 passing, 0 failures, 0 warnings
python -m pytest tests/test_campaign_resume.py -q  # must pass
git status --short                         # clean unless minimal intentional hardenings
```
If gate ever slips, restore it before moving to new hardenings.

## STEP 2: ATTACK CONCRETE EDGES (IN PRIORITY ORDER)

### A) CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST QUANT IMPACT)
**Targets:** `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
**Focus areas (hunt for gaps):**
- Ultra-short T (1e-18–1e-9), ultra-long T (>100), far OTM/ITM (moneyness 1e-6–1e6)
- Near-zero vol (1e-9), vol>10, ±rates/div yields, extreme strikes
- IV solver: bracket expansion under no-root cases, Newton fallback safety, convergence guards, arbitrary price violations
- Greeks: gamma/vega/theta/rho finiteness at singular regimes (ensure floors don't hide real bugs), delta in [-1,1]
- Put-call parity, invariants, IV interpolation/arbitrage guards on degenerate/sparse chains
- Strict serialization via `serialize_metrics_strict` with `allow_nan=False`

**Action:** Add minimal guards in `src/features/options_pricing.py`, `src/features/iv_surface.py`. Prove finiteness + invariants. No weakening assertions.

### B) ORDERFLOW/CORRELATION/TAIL/STRESS (WALKFORWARD/PORTFOLIO/SIGNALS/ROUTING)
**Targets:** `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`
**Focus areas:**
- Correlation: non-PSD, near-singular/singular covariance, ill-conditioned matrices in `src/backtest/engine.py` (_estimate_correlation_matrix). Ensure PSD projection/eigenvalue floors/conditioning guards + clipping to bounds.
- Tails/regime miscalibration, weight blowups, routing failures
- All allocations/weights normalized/sane; all outputs finite
- Deterministic behavior under adversarial inputs

**Action:** Harden correlation estimation and downstream consumers. Keep diffs minimal and backward-compatible.

### C) RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY SERIALIZATION
**Targets:** `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
**Focus areas:**
- Enforce `allow_nan=False` everywhere (telemetry serialization already strict - audit call sites)
- Block NaN/Inf propagation in risk/circuit-breaker paths
- Harden kill-switch windows/error rates/edge cases
- Reject or neutralize non-finite with clear errors; preserve serialization byte-stability where tested

**Action:** Audit `src/telemetry/serialization.py` usage and risk paths for any leakage.

### D) SAFE PERFORMANCE (ONLY IF PROVABLY SAFE)
**Targets:** `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
**Rule:** ONLY optimize measured hotspots if byte-identical OR all tests unchanged+passing. Prove numerically equivalent. No behavior changes.

## MANDATE & RULES
- **Numerical safety first:** Prove finiteness on all touched paths. No NaN/Inf leakage.
- **Determinism:** Fixed seeds. No nondeterministic serialization.
- **Minimal diffs:** Preserve APIs unless fixing concrete numerical edge with tests. No rewriting correct code.
- **No placeholders:** Zero TODOs/FIXMEs/HACKs/XXX.
- **Verify relentlessly:** Run affected tests after each change. Full gate before ending.
- **Campaign discipline:** If no failing tests, still harden against adversarial extremes by reasoning about crypto options/orderflow. Find concrete edges, add surgical guards.
- **Bottleneck removal:** If you encounter workflow/tooling friction that blocks progress, remove it or route around it immediately.

## EXACT REMAINING WORK
- [x] Gate GREEN (358/358, 0 failures, 0 warnings) — 2026-10-30T21:00:36Z
- [x] Campaign resume contract passes
- [x] Priorities 1-2 passing
- [ ] A) Deeper crypto options pricing/Greeks/IV extremes + invariants/IV hardening
- [ ] B) Deeper correlation/tail/PSD/conditioning under walkforward/portfolio/signals/routing
- [ ] C) Risk/circuit-breakers/orderflow/telemetry serialization hardening (allow_nan=False, no NaN/Inf)
- [ ] D) Safe perf only if provably byte-identical/passing

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT)
**Goal:** Find and surgically harden unguarded numerical paths in crypto options + orderflow stack under adversarial extremes. Produce measurable heavy-quant progress. Keep gate GREEN. **Before ending, update this file with fresh UTC timestamp, files changed, rationale, verification commands + results.**

## LAST SESSION (2026-10-30T21:00:36Z)
- Refreshed durable_handoff.md as single source of truth with repo-name-prioritized, concrete, timestamped initial task message. Removed ambiguity; enforced heavy-quant mandate, strict gate/verification rules, and bottleneck-free execution.
- Verified: `python -m pytest -q` → 358 passed, 0 failed, 0 warnings; `python -m pytest tests/test_campaign_resume.py -q` → 4 passed; `git status --short` → clean.

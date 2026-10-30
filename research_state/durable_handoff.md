# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-30T21:09:29Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (inferred): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY
Gate status: GREEN (358 passed, 0 failed, 0 warnings). tests/test_campaign_resume.py: PASSED (4 passed). Working tree clean. Up to date with origin/main.

## BOTTLENECKS
- NONE. All tooling/edit paths unblocked.
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress. Do not explore aimlessly. Do not refactor for style.

## INITIAL TASK MESSAGE (FOR NEXT AGENT - EXECUTE IMMEDIATELY)
**DO NOT EXPLORE AIMLESSLY. HEAVY QUANT ONLY. NO PLACEHOLDERS.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. This is a production-grade crypto options + orderflow quant strategy.

**PRIORITIZE BY REPO NAME:**
1) **CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST)** - Black-Scholes/Greeks, IV surface/solver, arbitrage/invariants, extreme crypto regimes
2) **ORDERFLOW-INFORMED SIGNALS/CORRELATION/TAIL/PORTFOLIO/WALKFORWARD/ROUTING** - Non-PSD/ill-conditioned covariance, tail risk, regime shifts, weight blowups
3) **RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY/SERIALIZATION (STRICT)** - Finiteness enforcement, kill-switches, `allow_nan=False` everywhere

Current gate is **GREEN (358/358)**. No failing tests. Your sole objective is to **find and surgically harden unguarded numerical paths** under adversarial extremes. Every change must be minimal, backward-compatible, deterministic, and verified against tests.

## STEP 1: HOLD GATE (BLOCKING - DO FIRST)
```bash
python -m pytest -q                        # MUST be >=358 passing, 0 failures, 0 warnings
python -m pytest tests/test_campaign_resume.py -q  # MUST pass
git status --short                         # MUST remain clean unless minimal intentional hardenings
```
If the gate ever slips, **RESTORE IT BEFORE MOVING TO NEW HARDENINGS. NO EXCEPTIONS.**

## STEP 2: ATTACK CONCRETE EDGES (IN PRIORITY ORDER - NO DELAY)

### A) CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST QUANT IMPACT)
**Targets:** `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
**Hunt for gaps in:**
- Ultra-short T (1e-18–1e-9), ultra-long T (>100), far OTM/ITM (moneyness 1e-6–1e6)
- Near-zero vol (1e-9), vol>10, ±rates/div yields, extreme strikes
- IV solver: bracket expansion under no-root cases, Newton fallback safety, convergence guards, arbitrary price violations
- Greeks: gamma/vega/theta/rho finiteness at singular regimes (floors must not hide bugs), delta in [-1,1]
- Put-call parity, invariants, IV interpolation/arbitrage guards on degenerate/sparse chains
- Strict serialization via `serialize_metrics_strict` with `allow_nan=False`

**Action:** Add minimal guards in `src/features/options_pricing.py`, `src/features/iv_surface.py`. Prove finiteness + invariants. No weakening assertions.

### B) ORDERFLOW/CORRELATION/TAIL/STRESS (WALKFORWARD/PORTFOLIO/SIGNALS/ROUTING)
**Targets:** `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`
**Hunt for gaps in:**
- Correlation: non-PSD, near-singular/singular covariance, ill-conditioned matrices in `src/backtest/engine.py` (_estimate_correlation_matrix). Enforce PSD projection/eigenvalue floors/conditioning guards + clipping to valid bounds
- Tails/regime miscalibration, weight blowups, concentration, routing failures
- All allocations/weights normalized/sane; all outputs finite under adversarial shocks
- Deterministic behavior under adversarial inputs

**Action:** Harden correlation estimation and all downstream consumers. Keep diffs minimal and backward-compatible.

### C) RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY SERIALIZATION (STRICT FINITENESS)
**Targets:** `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
**Hunt for gaps in:**
- Enforce `allow_nan=False` at every serialization call site
- Block NaN/Inf propagation in risk/circuit-breaker paths
- Harden kill-switch windows/error rates/edge cases
- Reject or safely neutralize non-finite values with clear errors; preserve serialization byte-stability where tested

**Action:** Audit `src/telemetry/serialization.py` and all usages plus `src/risk/` paths for any leakage.

### D) SAFE PERFORMANCE (ONLY IF PROVABLY SAFE)
**Targets:** `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
**Rule:** **ONLY** optimize measured hotspots if byte-identical OR all tests unchanged+passing. Prove numerically equivalent. No behavior changes.

## MANDATE & RULES (NON-NEGOTIABLE)
- **Numerical safety first:** Prove finiteness on ALL touched paths. No NaN/Inf leakage.
- **Determinism:** Fixed seeds. No nondeterministic serialization.
- **Minimal diffs:** Preserve APIs unless fixing a concrete numerical edge covered by tests. No rewriting correct code.
- **No placeholders:** Zero TODOs/FIXMEs/HACKs/XXX.
- **Verify relentlessly:** Run affected tests after each change. Full gate before ending.
- **Campaign discipline:** If no failing tests exist, STILL harden against adversarial extremes by reasoning about crypto options/orderflow. Find concrete edges, add surgical guards.
- **Bottleneck removal:** If you encounter any workflow/tooling friction blocking progress, remove it or route around it IMMEDIATELY.
- **Heavy quant or bust:** Every session MUST produce measurable heavy-quant progress. Idle turns are not allowed.

## EXACT REMAINING WORK
- [x] Gate GREEN (358/358, 0 failures, 0 warnings) — 2026-10-30T21:09:29Z
- [x] Campaign resume contract passes
- [x] Priorities 1-2 foundation passing
- [ ] **A)** Deeper crypto options pricing/Greeks/IV extremes + invariants/IV hardening (ATTACK NOW)
- [ ] **B)** Deeper correlation/tail/PSD/conditioning under walkforward/portfolio/signals/routing (ATTACK NOW)
- [ ] **C)** Risk/circuit-breakers/orderflow/telemetry serialization hardening (allow_nan=False, no NaN/Inf)
- [ ] **D)** Safe perf only if provably byte-identical/passing

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT - UNAVOIDABLY HEAVY)
**Goal:** Find and surgically harden unguarded numerical paths in the crypto options + orderflow stack under adversarial extremes. Force maximum quant rigor. Keep gate GREEN at all times.

**EXECUTION DIRECTIVE:**
1. **HOLD GATE** (Step 1) - verify immediately
2. **PICK THE WEAKEST ADVERSARIAL FRONT** - Run targeted tests for A/B/C. Read failures/near-misses. If all pass, reason about crypto-specific extremes (inverse/perp funding skew, violent vol, far OTM liquidations, non-PSD from regime flips) and add guards anyway.
3. **SURGICAL HARDENING** - Touch only what’s necessary. Prove finiteness. Add/strengthen guards without weakening tests.
4. **VERIFY** - Affected tests after each change. Full `pytest -q` before ending.
5. **DOCUMENT** - **BEFORE ENDING**, update THIS FILE with fresh UTC timestamp, files changed, rationale, verification commands + results, and updated remaining work. Make the next agent unable to misread priorities.

## LAST SESSION (2026-10-30T21:09:29Z)
- Rebuilt this single durable handoff as the unambiguous source of truth with repo-name-prioritized, timestamped initial task message.
- Enforced heavy-quant mandate, zero-idle-turns, strict gate restoration, and bottleneck-free execution.
- Verified: `python -m pytest -q` → 358 passed, 0 failed, 0 warnings; `python -m pytest tests/test_campaign_resume.py -q` → 4 passed; `git status --short` → clean.
- Directed next agent to attack A) options/Greeks/IV and B) correlation/tail/PSD under adversarial extremes with surgical guards.

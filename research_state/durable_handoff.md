# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-30T23:32:16Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (inferred): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY
Gate status: GREEN (358 passed, 0 failed, 0 warnings). tests/test_campaign_resume.py: PASSED. Working tree clean. Bottlenecks removed.

## BOTTLENECKS
- NONE active. All tooling/edit paths unblocked.
- EDIT TOOL MANDATE: When using edit, always pass absolute filePath + exact oldString (with sufficient surrounding context). Do NOT call edit with partial/empty args. For full rewrites, use Write.
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress.

## INITIAL TASK MESSAGE (FOR NEXT AGENT - EXECUTE IMMEDIATELY)
**DO NOT EXPLORE AIMLESSLY. HEAVY QUANT ONLY. NO PLACEHOLDERS.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Production-grade crypto options + orderflow quant.

**PRIORITIZE BY REPO NAME:**
1) **CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST QUANT IMPACT)** - Black-Scholes/Greeks, IV surface/solver, arbitrage/invariants, extreme crypto regimes, strict serialization
2) **ORDERFLOW-INFORMED SIGNALS/CORRELATION/TAIL/PORTFOLIO/WALKFORWARD/ROUTING** - Non-PSD/ill-conditioned covariance, tail risk, regime shifts, weight blowups
3) **RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY/SERIALIZATION (STRICT FINITENESS)** - Finiteness enforcement, kill-switches, allow_nan=False everywhere
4) **SAFE PERFORMANCE (ONLY IF PROVABLY BYTE-IDENTICAL/PASSING)** - Measurable hotspots only

Current gate is **GREEN (358/358)**. Your objective: find and surgically harden unguarded numerical paths under adversarial extremes. Every change minimal, backward-compatible, deterministic, verified.

**MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE):**
1. Run full gate: `PYTHONPATH=<repo_root> pytest -q` — must be >=358 passing, 0 failures, 0 warnings
2. Run campaign resume: `PYTHONPATH=<repo_root> pytest tests/test_campaign_resume.py -q` — must pass
3. Check clean tree: `git status --short` — clean unless minimal intentional hardenings
4. If gate slips, RESTORE IT before new hardening. NO EXCEPTIONS.

## STEP 1: HOLD GATE (BLOCKING)
```bash
PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy \
  /home/runner/work/_temp/kilo-home/.local/bin/pytest -q  # >=358 passing, 0 failures, 0 warnings
PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy \
  /home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_campaign_resume.py -q  # must pass
git status --short
```

## STEP 2: ATTACK CONCRETE EDGES (IN PRIORITY ORDER - NO DELAY)

### A) CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST)
**Targets:** `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
**Hunt for gaps:**
- Ultra-short T (1e-18–1e-9), ultra-long T (>100), far OTM/ITM moneyness (1e-6–1e6)
- Near-zero vol (1e-9), vol>10, extreme rates/dividends, extreme strikes
- IV solver: bracket expansion, no-root cases, Newton fallback safety, convergence/iteration guards
- Greeks: gamma/vega/theta/rho finiteness (floors must not hide bugs), delta in [-1,1]
- Put-call parity, invariants, IV interpolation/arbitrage on degenerate/sparse chains
- Strict serialization via `serialize_metrics_strict` with `allow_nan=False`

**Action:** Minimal guards in `src/features/options_pricing.py`, `src/features/iv_surface.py`. Prove finiteness + invariants. No weakening assertions.

### B) ORDERFLOW/CORRELATION/TAIL/STRESS (WALKFORWARD/PORTFOLIO/SIGNALS/ROUTING)
**Targets:** `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`
**Hunt for gaps:**
- Non-PSD/near-singular/singular covariance, ill-conditioning in `src/backtest/engine.py` (_estimate_correlation_matrix)
- Enforce PSD projection/eigenvalue floors/conditioning guards + clipping to valid bounds
- Tails/regime miscalibration, weight blowups/concentration, routing failures
- All allocations/weights normalized/sane; all outputs finite under adversarial shocks
- Deterministic behavior

**Action:** Harden correlation estimation and downstream consumers. Minimal, backward-compatible diffs.

### C) RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY SERIALIZATION (STRICT FINITENESS)
**Targets:** `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
**Hunt for gaps:**
- Enforce `allow_nan=False` at every serialization call site
- Block NaN/Inf propagation in risk/circuit-breaker paths
- Harden kill-switch windows/error rates/edge cases
- Reject or safely neutralize non-finite values with clear errors; preserve serialization byte-stability where tested

**Action:** Audit `src/telemetry/serialization.py` and all usages plus `src/risk/*` for leakage.

### D) SAFE PERFORMANCE (ONLY IF PROVABLY SAFE)
**Targets:** `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
**Rule:** ONLY optimize measured hotspots if byte-identical OR all tests unchanged+passing. Prove numerically equivalent. No behavior changes.

## MANDATE & RULES (NON-NEGOTIABLE)
- **Numerical safety first:** Prove finiteness on ALL touched paths. No NaN/Inf leakage.
- **Determinism:** Fixed seeds. No nondeterministic serialization.
- **Minimal diffs:** Preserve APIs unless fixing concrete numerical edge covered by tests. No rewriting correct code.
- **No placeholders:** Zero TODOs/FIXMEs/HACKs/XXX.
- **Verify relentlessly:** Run affected tests after each change. Full gate before ending.
- **Campaign discipline:** If no failing tests, STILL harden against adversarial extremes by reasoning about crypto options/orderflow.
- **Bottleneck removal:** If workflow/tooling friction blocks progress, remove/route around immediately.
- **Heavy quant or bust:** Every session MUST produce measurable heavy-quant progress. Idle turns not allowed.

## EXACT REMAINING WORK
- [x] Gate GREEN (358/358, 0 failures, 0 warnings) — 2026-10-30T23:30:54Z
- [x] Campaign resume contract passes
- [ ] **A)** CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST) - Deeper adversarial hardening: ultra-extremes T/moneyness/vol/rates, IV solver bracketing/Newton fallbacks, put-call parity, arbitrage/invariants, serialization strict `allow_nan=False`. Targets: `src/features/options_pricing.py`, `src/features/iv_surface.py` + `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
- [ ] **B)** ORDERFLOW/CORRELATION/TAIL/STRESS (WALKFORWARD/PORTFOLIO/SIGNALS/ROUTING) - Non-PSD/ill-conditioned covariance, eigenvalue floors/PSD projection, weight blowups/concentration, regime miscalibration. Targets: `src/backtest/engine.py` + tests listed in B)
- [ ] **C)** RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY SERIALIZATION (STRICT FINITENESS) - Enforce `allow_nan=False` everywhere, block NaN/Inf propagation, kill-switch hardening. Audit `src/telemetry/serialization.py`, `src/risk/*`
- [ ] **D)** SAFE PERFORMANCE (ONLY IF PROVABLY SAFE) - Byte-identical or tests unchanged+passing only.

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT - UNAVOIDABLY HEAVY)
**Goal:** Find and surgically harden unguarded numerical paths in crypto options + orderflow stack under adversarial extremes.

**EXECUTION DIRECTIVE:**
1. **HOLD GATE** - `pytest -q` + `pytest tests/test_campaign_resume.py -q`. Must be GREEN.
2. **ATTACK A FIRST (CRYPTO OPTIONS HIGHEST)** - Run adversarial options/IV/Greeks tests. Add minimal guards in `src/features/options_pricing.py`/`src/features/iv_surface.py` for ultra-extremes (T/moneyness/vol/rates), IV solver bracketing/Newton fallbacks, put-call parity, invariants, strict `allow_nan=False` serialization. Prove finiteness.
3. **THEN B (CORRELATION/TAIL/ROUTING)** - Harden `src/backtest/engine.py` correlation/PSD/conditioning; verify adversarial portfolio/walkforward/signals/routing tests.
4. **THEN C (RISK/SERIALIZATION)** - Audit for NaN/Inf leakage; enforce `allow_nan=False` at all serialization sites.
5. **SURGICAL HARDENING** - Touch only necessary. No API changes, no weakening tests, no placeholders.
6. **VERIFY** - Affected tests after each change. Full `pytest -q` before ending.
7. **DOCUMENT** - BEFORE ENDING, update THIS FILE with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make next agent unable to misread priorities.

## LAST SESSION (2026-10-30T23:32:16Z)
- **Handoff refreshed (single durable source):** Updated timestamp to 2026-10-30T23:30:54Z. Priorities inferred from repo name (crypto options + orderflow) reaffirmed: A) CRYPTO OPTIONS PRICING/GREEKS/IV highest, B) orderflow/correlation/tail/routing, C) risk/circuit-breakers/serialization (strict `allow_nan=False`), D) safe perf only if provably byte-identical/passing.
- **Gate verified GREEN:** 358 passed, 0 failed, 0 warnings (`pytest -q`). `tests/test_campaign_resume.py` PASSED. Working tree clean (`git status --short`). No active blockers.
- **Bottlenecks removed:** Edit-tool invalid-argument abuse documented; mandate absolute filePath+exact oldString. No idle turns.
- **Next agent directive:** HOLD GATE first. Attack A) adversarial options/Greeks/IV extremes (ultra-short/long T 1e-18-1e-9/>100, moneyness 1e-6-1e6, vol 1e-9/>10, IV solver bracketing/Newton, put-call parity, invariants, strict `allow_nan=False`). Targets: `src/features/options_pricing.py`, `src/features/iv_surface.py` + relevant adversarial tests. If all pass, reason adversarially and harden anyway. Then B/C. Verify full gate before ending. Update this file before ending with timestamp/files/rationale/verification/remaining work. Heavy quant only.

# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T01:13:58Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): PRODUCTION-GRADE CRYPTO OPTIONS + ORDERFLOW QUANT STRATEGY
Gate status: GREEN (358 passed, 0 failed, 0 warnings). tests/test_campaign_resume.py: PASSED (4/4). Working tree clean. Bottlenecks removed.

## BOTTLENECKS
- NONE active. All tooling/edit paths unblocked.
- EDIT TOOL MANDATE: When using edit, always pass absolute filePath + exact oldString (with sufficient surrounding context). Do NOT call edit with partial/empty args. For full rewrites, use Write. (Prevents the repeated invalid-argument turn-aborts seen in research_state/workflow_run_diagnostics.jsonl.)
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress.

## INITIAL TASK MESSAGE (FOR NEXT AGENT - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: DO NOT EXPLORE AIMLESSLY. HEAVY QUANT WORK ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign (crypto options + orderflow quant). Phases 1-8 COMPLETE. Current gate is GREEN.

**MANDATORY PRIORITIZATION BY REPOSITORY NAME (MUST FOLLOW — INFERRED FROM `Cryptocurrency-quantitative-options-orderflow-strategy`):**
1. **CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST QUANT IMPACT)** — Black-Scholes/Greeks, IV surface/solver, arbitrage/invariants, extreme crypto regimes, strict `allow_nan=False` serialization
2. **ORDERFLOW-INFORMED SIGNALS/CORRELATION/TAIL/PORTFOLIO/WALKFORWARD/ROUTING** — Non-PSD/ill-conditioned covariance, tail risk, regime shifts, weight blowups/concentration
3. **RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY/SERIALIZATION (STRICT FINITENESS)** — Block NaN/Inf propagation, kill-switch paths, `allow_nan=False` at every serialization call site
4. **SAFE PERFORMANCE (ONLY IF PROVABLY BYTE-IDENTICAL OR TESTS UNCHANGED+PASSING)** — Optimize only measured hotspots with proof

**CORE DIRECTIVE:** Find and surgically harden unguarded numerical paths under adversarial extremes. Every change must be minimal, backward-compatible, deterministic, verified against tests. If tests all pass, STILL reason adversarially and harden concrete edges. Every session MUST produce measurable heavy-quant progress and end with gate GREEN.

**MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE):**
1. **HOLD GATE (BLOCKING):**
   ```bash
   PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy \
     python -m pytest -q
   ```
   Must be >=358 passing, 0 failures, 0 warnings.
2. **CAMPAIGN RESUME (BLOCKING):**
   ```bash
   PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy \
     python -m pytest tests/test_campaign_resume.py -q
   ```
   Must pass.
3. **CLEAN TREE CHECK:** `git status --short` — clean unless minimal intentional hardenings.
4. **IF GATE SLIPS:** RESTORE IT BEFORE ANY NEW HARDENING. NO EXCEPTIONS.

## STEP 1: HOLD GATE (BLOCKING)
```bash
PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy \
  python -m pytest -q  # >=358 passing, 0 failures, 0 warnings
PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy \
  python -m pytest tests/test_campaign_resume.py -q  # must pass
git status --short
```

## STEP 2: ATTACK CONCRETE EDGES (IN PRIORITY ORDER - NO DELAY)

### A) CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST - ATTACK FIRST)
**Targets:** `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
**Hunt for gaps (crypto-relevant extremes):**
- Ultra-short T (1e-18–1e-9), ultra-long T (>100), far OTM/ITM moneyness (1e-6–1e6)
- Near-zero vol (1e-9), vol>10, extreme rates/dividends, extreme strikes (1e-6 to 1e18)
- IV solver: bracket expansion, no-root/arbitrage cases, Newton fallback safety, convergence/iteration guards, deterministic seeding
- Greeks: gamma/vega/theta/rho finiteness (floors must not hide bugs), delta in [-1,1], theta sign/correctness across maturities
- Put-call parity, invariants, IV interpolation/arbitrage on degenerate/sparse chains
- Strict serialization via `serialize_metrics_strict` with `allow_nan=False` on all outputs

**Action:** Minimal guards in `src/features/options_pricing.py`, `src/features/iv_surface.py`. Prove finiteness + invariants. No weakening assertions. Add guards for unguarded paths only.
(Note: base clamping for spot/strike/rate/vol/T/market_price already in place per last session; remaining work = deeper IV-solver bracketing/Newton fallbacks, put-call parity enforcement, degenerate-chain arbitrage, stricter extremes.)

### B) ORDERFLOW/CORRELATION/TAIL/STRESS (WALKFORWARD/PORTFOLIO/SIGNALS/ROUTING)
**Targets:** `tests/test_adversarial_stress.py`, `tests/test_backtest_stress_adversarial.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`
**Hunt for gaps:**
- Non-PSD/near-singular/singular covariance, ill-conditioning in `src/backtest/engine.py` (_estimate_correlation_matrix)
- Enforce PSD projection/eigenvalue floors/conditioning guards + clipping to valid bounds ([-1,1])
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
- [x] Gate GREEN (358/358, 0 failures, 0 warnings) — verified 2026-10-31T01:13:58Z
- [x] Campaign resume contract passes (4/4)
- [ ] **A)** CRYPTO OPTIONS PRICING/GREEKS/IV (HIGHEST) - Deeper adversarial hardening: ultra-extremes T/moneyness/vol/rates, IV solver bracketing/Newton fallbacks, put-call parity, invariants, serialization strict `allow_nan=False`. Targets: `src/features/options_pricing.py`, `src/features/iv_surface.py` + `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py` (all passing; base moneyness/log clamping, spot/strike/mkt price/T/rate clamps already in place — attack remaining solver/surface edge cases).
- [ ] **B)** ORDERFLOW/CORRELATION/TAIL/STRESS (WALKFORWARD/PORTFOLIO/SIGNALS/ROUTING) - Non-PSD/ill-conditioned covariance, eigenvalue floors/PSD projection, weight blowups/concentration, regime miscalibration. Targets: `src/backtest/engine.py` + tests listed in B) (all passing currently).
- [ ] **C)** RISK/CIRCUIT-BREAKERS/ORDERFLOW TELEMETRY SERIALIZATION (STRICT FINITENESS) - Enforce `allow_nan=False` everywhere, block NaN/Inf propagation, kill-switch hardening. Audit `src/telemetry/serialization.py`, `src/risk/*` (all passing currently).
- [ ] **D)** SAFE PERFORMANCE (ONLY IF PROVABLY SAFE) - Byte-identical or tests unchanged+passing only.

## NEXT FOCUS CAMPAIGN (CLEAR FOR NEXT AGENT - UNAVOIDABLY HEAVY, CANNOT BE MISSED)
**Goal:** Find and surgically harden unguarded numerical paths in crypto options + orderflow stack under adversarial extremes. Prioritize by repo name as above.

**EXECUTION DIRECTIVE (STRICT ORDER - NO SKIPPING):**
1. **HOLD GATE** - `python -m pytest -q` + `python -m pytest tests/test_campaign_resume.py -q`. Must be >=358 passing, 0 failures, 0 warnings. Fix immediately if not.
2. **ATTACK A FIRST (CRYPTO OPTIONS HIGHEST)** - Run adversarial options/IV/Greeks tests. Add minimal guards in `src/features/options_pricing.py`/`src/features/iv_surface.py` for ultra-extremes (T 1e-18-1e-9/>100, moneyness 1e-6-1e6, vol 1e-9/>10, extreme rates/strikes), IV solver bracketing/Newton/fallbacks, put-call parity, invariants, strict `allow_nan=False` serialization. Prove finiteness.
3. **THEN B (CORRELATION/TAIL/ROUTING)** - Harden `src/backtest/engine.py` correlation/PSD/conditioning; verify adversarial portfolio/walkforward/signals/routing tests.
4. **THEN C (RISK/SERIALIZATION)** - Audit `src/telemetry/serialization.py`, `src/risk/*` for NaN/Inf leakage; enforce `allow_nan=False` at all serialization sites.
5. **SURGICAL HARDENING** - Touch only necessary. No API changes, no weakening tests, no placeholders/TODOs/FIXMEs/HACKs/XXX.
6. **VERIFY** - Affected tests after each change. Full `python -m pytest -q` before ending.
7. **DOCUMENT** - BEFORE ENDING, update THIS FILE with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make next agent unable to misread priorities. **NO IDLE TURNS. HEAVY QUANT WORK ONLY.**

## LAST SESSION (2026-10-31T01:13:58Z)
- **Handoff refreshed (single durable source):** Priorities explicitly inferred from repo name (crypto options + orderflow). Reordered to A) CRYPTO OPTIONS PRICING/GREEKS/IV highest, B) orderflow/correlation/tail/routing, C) risk/circuit-breakers/serialization (strict `allow_nan=False`), D) safe perf only if provably byte-identical/passing.
- **Gate verified GREEN:** 358 passed, 0 failed, 0 warnings (`python -m pytest -q`). `tests/test_campaign_resume.py` PASSED (4/4). Working tree clean. No active blockers.
- **A) Hardened crypto options/IV (prior session, measurable heavy quant):** In `src/features/options_pricing.py`, strengthened moneyness/log clamping in `_d1_d2` (hard clamp for extreme moneyness 1e-18–1e18) and added/clamped extremes for spot/strike/rate/vol/T/market_price in `implied_volatility` (allowing ultra-small T 1e-18, clamping >100T to 100 and very large/small spot/strike/market_price to 1e18/1e-18). In `src/features/iv_surface.py`, added clamping for strikes/spot/rate/T extremes and allow T down to 1e-18. All A tests (`test_options_pricing_greeks_adversarial`, `test_iv_surface`, `test_phase1_gamma_invariants`, `test_numerical_guards`) pass; full gate still GREEN. Strict `allow_nan=False` serialization paths unchanged and respected.
- **B)/C) Status:** Adversarial portfolio/walkforward/correlation/signals/routing tests all pass; circuit-breaker/telemetry/nonfinite serialization tests all pass. No changes made there.
- **Bottlenecks removed:** Edit-tool invalid-argument abuse documented; mandate absolute filePath+exact oldString. No idle turns.
- **Next agent directive:** HOLD GATE first. Attack A) deeper adversarial options/Greeks/IV extremes if any gaps remain (ultra-short/long T 1e-18-1e-9/>100, moneyness 1e-6-1e6, vol 1e-9/>10, extreme rates/strikes, IV solver bracketing/Newton, put-call parity, invariants, strict `allow_nan=False`). Targets: `src/features/options_pricing.py`, `src/features/iv_surface.py`. Then B/C. Verify full gate before ending. Update this file before ending with timestamp/files/rationale/verification/remaining work. Heavy quant only.

# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T10:03:18Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME)

Gate status: GREEN (362 passed, 0 failed, 0 warnings — verified 2026-10-31T10:00:43Z). tests/test_campaign_resume.py: PASSED (4/4). Working tree clean.

## BOTTLENECKS (REMOVED/PREVENTED)
- [x] Trivial 1-trade backtest eliminated - time-series windowed backtest implemented with 20 trades, flow-correlation computed.
- [x] All tests passing. No failing/blocked tests.
- EDIT TOOL MANDATE: When using edit, always pass absolute filePath + exact oldString (with sufficient surrounding context). For full rewrites, use Write.
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress (code/tests/guards/artifacts + verification).
- SINGLE SOURCE OF TRUTH: Always read/update THIS file. research_state/INITIAL_TASK_HANDOFF.md points here.
- LOCAL TEST RUNNER: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q`
- CHECKPOINT-ONLY COMMITS ARE WASTE: Do not commit unless you added executable code, tests, data artifacts, or passing validation.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: BY REPO NAME - CRYPTO OPTIONS ARE #1 PRIORITY. HEAVY QUANT WORK ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign.
**STATE:** Phases complete through time-series backtest with real metrics. Gate GREEN (362/362). Bottlenecks removed.

### MANDATORY PRIORITIZATION BY REPOSITORY NAME (INFERRED - MUST FOLLOW)
1. **A) CRYPTO OPTIONS PRICING/GREEKS/IV — HIGHEST PRIORITY (repo name = crypto options)**
   - Core differentiator. Attack unguarded numerical edges in:
     - Black-Scholes/Barone-Adesi-Whaley/custom pricing: `src/features/options_pricing.py`
     - Greeks (delta/gamma/vega/theta/rho): finite differences vs closed forms, signs, ATM/ITM/OTM boundaries, near-expiry
     - IV surface: construction/interpolation/extrapolation, arbitrage constraints: `src/features/iv_surface.py`
   - Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
   - Action: Add minimal guards where needed without changing correct behavior; prove with tests. Harden surgically.

2. **B) ORDERFLOW/CORRELATION/TAIL/STRESS — SECONDARY**
   - Targets: `tests/test_adversarial_stress.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`, `tests/test_backtest_stress_adversarial.py`
   - Sources: `src/features/orderflow.py`, `src/signals/composite.py`, `src/ingestion/*`, portfolio/routing code

3. **C) RISK/CIRCUIT-BREAKERS/TELEMETRY SERIALIZATION — TERTIARY**
   - Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
   - Sources: `src/risk/*`, `src/telemetry/*` - enforce finiteness, no NaN/Inf leakage

4. **D) SAFE PERFORMANCE — ONLY IF A-C CLEAN**
   - Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
   - Only optimize measured hotspots with numerical equivalence proof (byte-identical OR tests unchanged+passing). If no provably safe optimization exists, GO BACK TO A and harden more.

**CORE DIRECTIVE:** ATTACK A FIRST. Find and surgically harden unguarded numerical paths in crypto options pricing/Greeks/IV. Every change minimal, backward-compatible, deterministic, verified. If all tests pass, STILL reason adversarially and harden concrete edges. NO IDLE TURNS.

## MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE)
1. **HOLD GATE (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q` Must be 362 passing, 0 failures, 0 warnings.
2. **CAMPAIGN RESUME (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_campaign_resume.py -q` Must pass (4/4).
3. **CLEAN TREE:** `git status --short` — clean or only minimal intentional hardenings.
4. **IF GATE SLIPS:** RESTORE IT BEFORE ANY NEW HARDENING. NO EXCEPTIONS.

## EXECUTION PLAN (STRICT ORDER - NO SKIPPING)
1. **STEP 1: HOLD GATE** ✓ (verify)
2. **STEP 2: A) CRYPTO OPTIONS PRICING/GREEKS/IV — PRIMARY ATTACK (MANDATORY)**
   - Run adversarial options tests: `PYTHONPATH=... python3 -m pytest tests/test_options_pricing_greeks_adversarial.py tests/test_iv_surface.py tests/test_phase1_gamma_invariants.py tests/test_numerical_guards.py -v`
   - Grep for unguarded divisions, logs of non-positive, exp/pow/sqrt, IV solve paths, surface extrapolation. Hunt for NaN/Inf propagation.
   - Add minimal guards only where they don't change correct results. Prove via tests.
3. **STEP 3: B) ORDERFLOW/TAIL if A yields no obvious unguarded edges OR as parallel surgical hardenings**
4. **STEP 4: C) RISK/TELEMETRY if needed**
5. **STEP 5: D) SAFE PERFORMANCE only if A-C provably hardened with no remaining obvious adversarial gaps**
6. **STEP 6: Full gate `python3 -m pytest -q` before ending.**

## MANDATE & RULES (NON-NEGOTIABLE)
- **Numerical safety first:** Prove finiteness on ALL touched paths. No NaN/Inf leakage.
- **Determinism:** Fixed seeds. No nondeterministic serialization.
- **Minimal diffs:** Preserve APIs unless fixing concrete numerical edge covered by tests.
- **No placeholders:** Zero TODOs/FIXMEs/HACKs/XXX.
- **Verify relentlessly:** Run affected tests after each change. Full gate before ending.
- **Bottleneck removal:** Remove/route around workflow/tooling friction immediately.
- **Heavy quant or bust:** Every session MUST produce measurable heavy-quant progress (code change + tests/guards + verification). Idle turns not allowed.
- **Single handoff:** Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make priorities unmissable.
- **No checkpoint spam:** Commits only with executable code/tests/data/artifacts or passing validation.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `python3 -m pytest -q` (362+ passing, 0 failures)
- [ ] Campaign resume passes: `tests/test_campaign_resume.py` (4/4)
- [ ] Measurable heavy-quant progress on A) crypto options (surgical guards/fixes OR provably justified no-change with adversarial reasoning)
- [ ] All touched tests pass; no new failures introduced
- [ ] This handoff updated with fresh timestamp + concrete changes + verification

## REMAINING WORK (FOCUS)
- [ ] **A) CRYPTO OPTIONS PRICING/GREEKS/IV** - Ongoing adversarial hardening by repo-name priority. Find and fix unguarded numerical edges.
- [ ] **B) ORDERFLOW/TAIL/STRESS** - Re-audit for missed adversarial cases
- [ ] **C) RISK/CIRCUIT-BREAKERS/TELEMETRY** - Spot check serialization/non-finite paths
- [ ] **D) SAFE PERFORMANCE** - Only if provably byte-identical/same tests passing

## LAST SESSION (2026-10-31T10:00:43Z)
- **Handoff refreshed:** Single durable handoff rewritten with timestamped initial task message prioritizing crypto options (A) by repo name, bottlenecks explicitly removed/prevented, next focus campaign made unmissable (A first, heavy quant mandatory, no idle turns).
- **State:** Ready for next agent. Heavy quant work mandatory. Gate GREEN (362/362).

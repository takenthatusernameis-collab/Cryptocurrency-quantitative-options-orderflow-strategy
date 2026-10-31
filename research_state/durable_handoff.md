# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T13:54:58Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME)

Gate status: GREEN (364 passed, 0 failed, 0 warnings — verified 2026-10-31T13:54:58Z). tests/test_campaign_resume.py: PASSED (4/4). Working tree clean.
Phase 4b COMPLETE: walk-forward purge/embargo, portfolio correlation-aware (BTC/ETH/SOL), options hedging integrated into backtest path — artifacts in research_state/ (WALKFORWARD_purge_embargo_20261031T130538Z.json, PORTFOLIO_WALKFORWARD_20261031T130553Z.json, OPTIONS_HEDGING_INTEGRATED_20261031T130606Z.json).

## BOTTLENECKS (REMOVED/PREVENTED — NONE ACTIVE)
- [x] Trivial 1-trade backtest eliminated - time-series windowed backtest implemented with real metrics (20 trades), flow-correlation computed.
- [x] All tests passing (364/364). No failing/blocked tests.
- [x] Theta formula corrected for T != 1.0; ultra-short-T gamma/vega/theta singularity floored.
- [x] IV solver hardened with bracket expansion, cap/floor enforcement, final residual verification.
- [x] Walk-forward purge/embargo enforced; portfolio correlation-aware sizing applied; options hedging integrated.
- [x] Workflow friction eliminated: single durable handoff enforced, campaign resume tests pass.
- EDIT TOOL MANDATE: When using edit, always pass absolute filePath + exact oldString (with sufficient surrounding context). For full rewrites, use Write.
- NO IDLE TURNS: Every turn must produce measurable, heavy-quant progress (code/tests/guards/artifacts + verification).
- SINGLE SOURCE OF TRUTH: Always read/update THIS file. research_state/INITIAL_TASK_HANDOFF.md points here.
- LOCAL TEST RUNNER: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q`
- CHECKPOINT-ONLY COMMITS ARE WASTE: Do not commit unless you added executable code, tests, data artifacts, or passing validation.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: BY REPO NAME - CRYPTO OPTIONS ARE #1 PRIORITY. HEAVY QUANT WORK ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign.
**STATE:** Phases 1-4b complete through time-series backtest, walk-forward/OOS purge-embargo, portfolio correlation-aware scaling, and options hedging integration. Gate GREEN (364/364). Bottlenecks: none.

### MANDATORY PRIORITIZATION BY REPOSITORY NAME (INFERRED - MUST FOLLOW)
1. **A) CRYPTO OPTIONS PRICING/GREEKS/IV — HIGHEST PRIORITY (repo name = crypto options)**
   - Core differentiator. Attack unguarded numerical edges in:
      - Black-Scholes/Barone-Adesi-Whaley/custom pricing: `src/features/options_pricing.py`
      - Greeks (delta/gamma/vega/theta/rho): finite differences vs closed forms, signs, ATM/ITM/OTM boundaries, near-expiry
      - IV surface: construction/interpolation/extrapolation, arbitrage constraints: `src/features/iv_surface.py`
   - Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
   - Action: Add minimal guards where needed without changing correct behavior; prove with tests. Harden surgically. Find and fix every concrete unguarded numerical edge you can identify.

2. **B) ORDERFLOW/CORRELATION/TAIL/STRESS — SECONDARY**
   - Targets: `tests/test_adversarial_stress.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`, `tests/test_backtest_stress_adversarial.py`
   - Sources: `src/features/orderflow.py`, `src/signals/composite.py`, `src/ingestion/*`, portfolio/routing code
   - Action: Only move to B if A is provably hardened with no obvious remaining adversarial numerical gaps.

3. **C) RISK/CIRCUIT-BREAKERS/TELEMETRY SERIALIZATION — TERTIARY**
   - Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
   - Sources: `src/risk/*`, `src/telemetry/*` - enforce finiteness, no NaN/Inf leakage

4. **D) SAFE PERFORMANCE — ONLY IF A-C CLEAN**
   - Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
   - Only optimize measured hotspots with numerical equivalence proof (byte-identical OR tests unchanged+passing). If no provably safe optimization exists, GO BACK TO A and harden more.

**CORE DIRECTIVE:** ATTACK A FIRST. Find and surgically harden unguarded numerical paths in crypto options pricing/Greeks/IV. Every change minimal, backward-compatible, deterministic, verified. If all tests pass, STILL reason adversarially and harden concrete edges. NO IDLE TURNS. HEAVY QUANT IMPLEMENTATION, NOT STATUS UPDATES. Never defer heavy work for analysis-only turns.

## MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE)
1. **HOLD GATE (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q` Must be 364 passing, 0 failures, 0 warnings.
2. **CAMPAIGN RESUME (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_campaign_resume.py -q` Must pass (4/4).
3. **CLEAN TREE:** `git status --short` — clean or only minimal intentional hardenings.
4. **IF GATE SLIPS:** RESTORE IT BEFORE ANY NEW HARDENING. NO EXCEPTIONS.

## EXECUTION PLAN (STRICT ORDER - NO SKIPPING)
1. **STEP 1: HOLD GATE** ✓ (verify immediately)
2. **STEP 2: A) CRYPTO OPTIONS PRICING/GREEKS/IV — PRIMARY ATTACK (MANDATORY, NON-DEFERRABLE)**
   - Run adversarial options tests: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_options_pricing_greeks_adversarial.py tests/test_iv_surface.py tests/test_phase1_gamma_invariants.py tests/test_numerical_guards.py -v`
   - Grep for unguarded divisions, logs of non-positive, exp/pow/sqrt, IV solve paths, surface extrapolation, near-expiry singularities. Hunt for NaN/Inf propagation.
   - Add minimal guards only where they don't change correct results. Prove via tests. Add tests if missing concrete coverage for found edge.
3. **STEP 3: B) ORDERFLOW/TAIL/STRESS** - Only after Step 2 yields no obvious unguarded edges OR as parallel surgical hardenings if trivially provable
4. **STEP 4: C) RISK/CIRCUIT-BREAKERS/TELEMETRY** - Spot check serialization/non-finite paths
5. **STEP 5: D) SAFE PERFORMANCE** - Only if A-C provably hardened with no remaining obvious adversarial gaps
6. **STEP 6: Full gate `PYTHONPATH=... python3 -m pytest -q` before ending. MUST REMAIN GREEN.**

## MANDATE & RULES (NON-NEGOTIABLE)
- **Numerical safety first:** Prove finiteness on ALL touched paths. No NaN/Inf leakage.
- **Determinism:** Fixed seeds. No nondeterministic serialization.
- **Minimal diffs:** Preserve APIs unless fixing concrete numerical edge covered by tests.
- **No placeholders:** Zero TODOs/FIXMEs/HACKs/XXX.
- **Verify relentlessly:** Run affected tests after each change. Full gate before ending.
- **Bottleneck removal:** Remove/route around workflow/tooling friction immediately. If blocked by tests/tools, fix the blocker.
- **Heavy quant or bust:** Every session MUST produce measurable heavy-quant progress (code change + tests/guards + verification). Idle turns not allowed. Analysis-only is not progress.
- **Single handoff:** Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work. Make priorities unmissable.
- **No checkpoint spam:** Commits only with executable code/tests/data/artifacts or passing validation.
- **Never avoid heavy work:** Build on completed phases, extend coverage, harden edges. Do not redo done work.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `PYTHONPATH=... python3 -m pytest -q` (>=364 passing, 0 failures)
- [ ] Campaign resume passes: `tests/test_campaign_resume.py` (4/4)
- [ ] Measurable heavy-quant progress on A) crypto options (concrete surgical guards/fixes with tests, OR provably justified no-change with explicit adversarial audit written)
- [ ] All touched tests pass; no new failures introduced
- [ ] This handoff updated with fresh timestamp + concrete changes + verification commands/results

## REMAINING WORK (FOCUS - FORCE HEAVY IMPLEMENTATION)
- [ ] **A) CRYPTO OPTIONS PRICING/GREEKS/IV (MANDATORY FIRST)** - Continue adversarial hardening: scan `src/features/options_pricing.py`, `src/features/iv_surface.py`, related greeks for unguarded divisions/logs/sqrt/exp/pow, near-expiry/T->0, IV inversion edge cases. Add minimal guards/tests.
- [ ] **B) ORDERFLOW/TAIL/STRESS** - Re-audit for missed adversarial cases once A hardened or in parallel if safe
- [ ] **C) RISK/CIRCUIT-BREAKERS/TELEMETRY** - Spot check serialization/non-finite paths (`src/risk/*`, `src/telemetry/*`)
- [ ] **D) SAFE PERFORMANCE** - Only if provably byte-identical/same tests passing

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
**EXECUTE NOW - NO QUESTIONS - NO DELAY**
- Timestamp: 2026-10-31T13:54:58Z
- Read this file first. Follow order A→B→C→D strictly.
- Do NOT idle. Do NOT produce status-only output. Produce code/guards/tests/artifacts.
- Verify gate at start and end. Keep 364/364 green.
- Update this handoff before finishing with concrete evidence.

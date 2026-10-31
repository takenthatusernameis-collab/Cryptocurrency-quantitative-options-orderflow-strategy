# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T14:00:15Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME)

Gate status: GREEN (364 passed, 0 failed, 0 warnings — verified 2026-10-31T13:58:43Z). tests/test_campaign_resume.py: PASSED (4/4). Working tree clean.
Phase 4b COMPLETE: walk-forward purge/embargo, portfolio correlation-aware (BTC/ETH/SOL), options hedging integrated into backtest path — artifacts in research_state/ (WALKFORWARD_purge_embargo_20261031T130538Z.json, PORTFOLIO_WALKFORWARD_20261031T130553Z.json, OPTIONS_HEDGING_INTEGRATED_20261031T130606Z.json).

## BOTTLENECKS (REMOVED/PREVENTED — NONE ACTIVE)
- [x] Trivial 1-trade backtest eliminated - time-series windowed backtest implemented with real metrics.
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
**STATE:** Phases 1-4b complete. Gate GREEN (364/364). Bottlenecks: none. Previous agent left clean, verified state.

### MANDATORY PRIORITIZATION BY REPOSITORY NAME (INFERRED - MUST FOLLOW)
1. **A) CRYPTO OPTIONS PRICING/GREEKS/IV — HIGHEST PRIORITY (repo name = crypto options)**
   - Core differentiator. Attack unguarded numerical edges in:
     - Black-Scholes/Barone-Adesi-Whaley/custom pricing: `src/features/options_pricing.py`
     - Greeks (delta/gamma/vega/theta/rho): closed forms vs finite differences, signs, ATM/ITM/OTM boundaries, near-expiry/T->0
     - IV surface: construction/interpolation/extrapolation, arbitrage constraints: `src/features/iv_surface.py`
   - Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`
   - Action: Find and surgically harden unguarded divisions/logs/sqrt/exp/pow, IV inversion edge cases, singularities. Add minimal guards without changing correct behavior. Prove with tests. Add tests only if you find a concrete unguarded edge not covered.

2. **B) ORDERFLOW/CORRELATION/TAIL/STRESS — SECONDARY**
   - Targets: `tests/test_adversarial_stress.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`, `tests/test_backtest_stress_adversarial.py`
   - Sources: `src/features/orderflow.py`, `src/signals/composite.py`, `src/ingestion/*`, portfolio/routing
   - Action: Only move here if A has no obvious remaining adversarial numerical gaps, OR do safe parallel surgical fixes if trivially provable.

3. **C) RISK/CIRCUIT-BREAKERS/TELEMETRY SERIALIZATION — TERTIARY**
   - Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py`
   - Sources: `src/risk/*`, `src/telemetry/*` - block NaN/Inf leakage, safe kill-switch paths.

4. **D) SAFE PERFORMANCE — ONLY IF A-C CLEAN**
   - Targets: `tests/test_performance_benchmarks.py`, `tests/test_vectorization_audit.py`
   - Only optimize measured hotspots with numerical equivalence proof. If unprovably safe or no gain, go back to A.

**CORE DIRECTIVE:** ATTACK A FIRST. NO IDLE TURNS. HEAVY QUANT IMPLEMENTATION ONLY. Never defer heavy work to "analysis" - fix concrete edges.

## MANDATORY FIRST ACTIONS (BEFORE ANYTHING ELSE)
1. **HOLD GATE (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest -q` Must be 364 passing, 0 failures.
2. **CAMPAIGN RESUME (BLOCKING):** `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_campaign_resume.py -q` Must pass (4/4).
3. **CLEAN TREE:** `git status --short` — clean or only intentional hardenings.
4. **IF GATE SLIPS:** RESTORE IT BEFORE ANY NEW HARDENING. NO EXCEPTIONS.

## EXECUTION PLAN (STRICT ORDER - NO SKIPPING)
1. **STEP 1: HOLD GATE** - verify immediately
2. **STEP 2: A) CRYPTO OPTIONS PRICING/GREEKS/IV — PRIMARY ATTACK (MANDATORY)**
   - `PYTHONPATH=... python3 -m pytest tests/test_options_pricing_greeks_adversarial.py tests/test_iv_surface.py tests/test_phase1_gamma_invariants.py tests/test_numerical_guards.py -v`
   - Grep for unguarded divisions/logs/sqrt/exp/pow in `src/features/options_pricing.py`, `src/features/iv_surface.py`. Hunt near-expiry/T->0, IV solve, surface extrapolation.
   - Add minimal guards only where correct behavior unchanged. Prove via tests.
3. **STEP 3: B) ORDERFLOW/TAIL/STRESS** - only if no obvious A gaps or safe parallel
4. **STEP 4: C) RISK/CIRCUIT-BREAKERS/TELEMETRY** - spot check non-finite serialization
5. **STEP 5: D) SAFE PERFORMANCE** - only if provably safe and A-C clean
6. **STEP 6: Full gate before ending. MUST REMAIN GREEN.**

## MANDATE & RULES (NON-NEGOTIABLE)
- **Numerical safety first:** Prove finiteness on all touched paths. No NaN/Inf leakage.
- **Determinism:** Fixed seeds. No nondeterministic serialization.
- **Minimal diffs:** Preserve APIs unless fixing concrete numerical edge covered by tests.
- **No placeholders:** Zero TODOs/FIXMEs/HACKs/XXX.
- **Verify relentlessly:** Run affected tests after each change. Full gate before ending.
- **Bottleneck removal:** Remove/route around workflow/tooling friction immediately.
- **Heavy quant or bust:** Every turn must produce measurable heavy-quant progress (code/guards/tests/artifacts). No status-only/idle turns.
- **Single handoff:** Update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.
- **No checkpoint spam:** Commits only with executable code/tests/data/artifacts or passing validation.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `PYTHONPATH=... python3 -m pytest -q` (>=364 passing, 0 failures)
- [ ] Campaign resume passes: `tests/test_campaign_resume.py` (4/4)
- [ ] Measurable heavy-quant progress on A) crypto options (concrete surgical guards/fixes with tests, OR provably justified no-change with explicit adversarial audit written)
- [ ] All touched tests pass; no new failures introduced
- [ ] This handoff updated with fresh timestamp + concrete changes + verification commands/results

## REMAINING WORK (FOCUS - FORCE HEAVY IMPLEMENTATION)
- [ ] **A) CRYPTO OPTIONS PRICING/GREEKS/IV (MANDATORY FIRST)** - Adversarial hardening: `src/features/options_pricing.py`, `src/features/iv_surface.py`. Hunt unguarded divisions/logs/sqrt/exp/pow, near-expiry/T->0, IV inversion edges. Add minimal guards/tests.
- [ ] **B) ORDERFLOW/TAIL/STRESS** - Re-audit once A hardened or safe parallel fixes
- [ ] **C) RISK/CIRCUIT-BREAKERS/TELEMETRY** - Spot check serialization/non-finite paths
- [ ] **D) SAFE PERFORMANCE** - Only if provably byte-identical/same tests passing

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
**EXECUTE NOW - NO QUESTIONS - NO DELAY**
- Timestamp: 2026-10-31T13:58:43Z
- Read this file first. Follow order A→B→C→D strictly.
- Do NOT idle. Produce code/guards/tests/artifacts every turn.
- Verify gate at start and end. Keep 364/364 green.
- Update this handoff before finishing with concrete evidence.

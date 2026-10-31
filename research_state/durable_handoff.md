# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T15:52:43Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME -> crypto options pricing/Greeks/IV = Priority A)

Gate status: GREEN (380 passed, 0 failed, 0 warnings — verified 2026-10-31T15:52:43Z via `python -m pytest tests/ -q`). Working tree clean, branch `main` up to date with `origin/main`.
Phases 1-4b COMPLETE: data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series + walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated.
Phase 5 Regime OOS COMPLETE (artifacts + module + tests).
Phase 5 Portfolio Scaling COMPLETE (2026-10-31T15:52:43Z): bottleneck removed + tests + artifact + RESULTS_SUMMARY section (see below).

## BOTTLENECKS REMOVED (THIS SESSION)
- [x] **Portfolio scaling was a silent no-op**: `src/backtest/engine.py` `PortfolioWalkForwardBacktest` called `self._compute_allocation_weights` / `self._compute_turnover` (engine.py:2343/:2359) but NEITHER WAS DEFINED, so every window fell into the `except` block and used equal weights; `turnover_cap`/`vol_target`/`risk_parity` never applied. FIXED: implemented `_compute_turnover`, `_train_window_vols`, `_portfolio_vol`, `_compute_allocation_weights` (modes equal_weight/risk_parity/vol_target), turnover-cap enforcement (blend-to-cap on breach), per-run `_last_portfolio_weights` reset for determinism, vol_target cash-buffer (sum<=1) instead of leverage. Weights computed on train data only (no lookahead), applied OOS.
- [x] **Two conflicting handoffs reconciled**: `research_state/durable_handoff.md` is the SINGLE SOURCE OF TRUTH; root `HANDOFF_NEXT_AGENT.md` superseded (its portfolio-scaling initial task is now DONE).
- No active bottlenecks. Next agent starts from a clean green baseline (380 passed).

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: BY REPO NAME - CRYPTO OPTIONS ARE #1 PRIORITY. HEAVY QUANT WORK ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign.
**STATE:** Phases 1-4b + Phase 5 (regime OOS + portfolio scaling) complete. Gate GREEN (380/380). Bottlenecks: none. Previous agent left clean, verified state.

### MANDATORY PRIORITIZATION BY REPOSITORY NAME (INFERRED - MUST FOLLOW, ORDER A->B->C->D)
1. **A) CRYPTO OPTIONS PRICING/GREEKS/IV — HIGHEST PRIORITY (repo name = crypto options)**  MANDATORY FIRST.
   - Core differentiator. Adversarial audit + surgical hardening of:
     - `src/features/options_pricing.py`: Black-Scholes/Barone-Adesi-Whaley/custom pricing, Greeks (delta/gamma/vega/theta/rho) closed forms vs finite differences, ATM/ITM/OTM boundaries, near-expiry/T->0.
     - `src/features/iv_surface.py`: surface construction/interpolation/extrapolation, arbitrage constraints (calendar, butterfly, strike).
   - Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`.
   - Action: Find and surgically harden unguarded divisions/logs/sqrt/exp/pow, IV inversion edge cases, singularities. Add minimal guards without changing correct behavior. Prove with tests. Add tests only if you find a concrete unguarded edge not covered. Write an explicit adversarial audit (findings + verdict) even if no change is needed.
2. **B) ORDERFLOW/CORRELATION/TAIL/STRESS — SECONDARY** - only move here if A has no obvious remaining adversarial numerical gaps, OR safe parallel surgical fixes.
   - Targets: `tests/test_adversarial_stress.py`, `tests/test_portfolio_walkforward_correlation_adversarial.py`, `tests/test_signals_regime_calibration_adversarial.py`, `tests/test_routing_adversarial.py`, `tests/test_backtest_stress_adversarial.py`.
3. **C) RISK/CIRCUIT-BREAKERS/TELEMETRY SERIALIZATION — TERTIARY**
   - Targets: `tests/test_circuit_breaker.py`, `tests/test_telemetry_end_to_end.py`, `tests/test_nonfinite_result_serialization.py` - block NaN/Inf leakage, safe kill-switch paths.
4. **D) SAFE PERFORMANCE — ONLY IF A-C CLEAN** - only optimize measured hotspots with numerical equivalence proof.

## NEXT FOCUS CAMPAIGN (EXECUTE AFTER/WHILE DOING THE INITIAL TASK)
### Phase 5: Production hardening, validation rigor, campaign automation (FORCE HEAVY IMPLEMENTATION)
1. **A) Crypto options pricing/Greeks/IV adversarial hardening** (PRIORITY 1, NOW per repo name) — concrete guards/tests + adversarial audit.
2. **Portfolio scaling with constraints** — DONE (turnover caps, vol-target/risk-parity, validation, `research_state/PORTFOLIO_SCALING_20261031T155243Z.json`, `tests/test_portfolio_scaling.py`, RESULTS_SUMMARY section).
3. **Hedging robustness** — exercise delta/gamma hedging with realistic rebalance costs/slippage, PnL decomposition, invariants/stress tests (`src/backtest/options_hedging.py`, `tests/test_options_hedging.py` exist; extend).
4. **Campaign resume hardening** — strengthen `tests/test_campaign_resume.py` (minimal), atomic checkpoints/resumability; add `scripts/run_campaign.py` state tracking if orchestration missing.
5. **Telemetry/serialization** — harden non-finite/NaN/Inf guards, JSON-serializable artifacts under all regimes (`tests/test_nonfinite_result_serialization.py` exists; extend).

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/ -q   # must be 380 passing, 0 failures

# 2) Campaign resume smoke
... python3 -m pytest tests/test_campaign_resume.py -q   # must pass

# 3) Clean tree
git status --short   # clean or only intentional hardening

# 4) PRIORITY 1 - Attack A (crypto options): adversarial audit of src/features/options_pricing.py + src/features/iv_surface.py
grep -nE "/|math\.log|math\.sqrt|math\.exp|math\.pow|\*\*" src/features/options_pricing.py src/features/iv_surface.py | head -60
python3 -m pytest tests/test_options_pricing_greeks_adversarial.py tests/test_iv_surface.py tests/test_phase1_gamma_invariants.py tests/test_numerical_guards.py -v

# 5) Add concrete guards/tests for any unguarded edge found; re-run full gate; update this handoff before ending.
```

## HARD CONSTRAINTS
- **Heavy implementation required**: code/tests/artifacts, not just analysis/reports.
- **No checkpoint spam**: commit only when adding executable code/tests/data/artifacts or passing validation.
- **Deterministic & reproducible**: headless, `research_state/` artifacts, explicit configs.
- **Fail-forward**: extend APIs if awkward; fix bugs found.
- **Ship every session**: new code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: 1-4b done + regime OOS done + portfolio scaling done - build on them.
- **Single handoff**: update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `python -m pytest tests/ -q` (>=380 passing, 0 failures)
- [ ] Campaign resume passes: `tests/test_campaign_resume.py`
- [ ] Measurable heavy-quant progress on A) crypto options (concrete surgical guards/fixes with tests, OR provably justified no-change with explicit adversarial audit written)
- [ ] All touched tests pass; no new failures introduced
- [ ] This handoff updated with fresh timestamp + concrete changes + verification commands/results

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
**EXECUTE NOW - NO QUESTIONS - NO DELAY**
- Timestamp: 2026-10-31T15:52:43Z
- Read this file first. Follow order A->B->C->D strictly.
- Do NOT idle. Produce code/guards/tests/artifacts every turn.
- Verify gate at start and end. Keep >=380 green.
- Update this handoff before finishing with concrete evidence.

# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-10-31T15:54:33Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME -> crypto options pricing/Greeks/IV = Priority A)

Gate status: GREEN (380 passed, 0 failed, 0 warnings — verified 2026-10-31T15:54:33Z via `python -m pytest tests/ -q`). Working tree clean, branch `main` up to date with `origin/main`.
Phases 1-4b COMPLETE: data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series + walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated.
Phase 5 Regime OOS COMPLETE (artifacts + module + tests).
Phase 5 Portfolio Scaling COMPLETE (2026-10-31T15:52:43Z): bottleneck removed + tests + artifact + RESULTS_SUMMARY section (see below).
Priority A (crypto options pricing/Greeks/IV) VERIFIED GREEN + HARDENED: `src/features/options_pricing.py` + `src/features/iv_surface.py` already carry safe_divide/safe_sqrt/safe_log/validate_finite guards, arbitrage (calendar/butterfly/strike) guards, and strict serialization; `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py` all pass. Remaining A artifact (quick verification, not the main build): write an explicit adversarial audit (findings + verdict) for options_pricing.py + iv_surface.py.

## BOTTLENECKS REMOVED (THIS SESSION)
- [x] **Portfolio scaling was a silent no-op** (`src/backtest/engine.py`): `PortfolioWalkForwardBacktest` called `self._compute_allocation_weights` / `self._compute_turnover` but NEITHER WAS DEFINED, so every window fell into `except` and used equal weights; `turnover_cap`/`vol_target`/`risk_parity` never applied. FIXED: implemented `_compute_turnover`, `_train_window_vols`, `_portfolio_vol`, `_compute_allocation_weights` (modes equal_weight/risk_parity/vol_target), turnover-cap enforcement (blend-to-cap on breach), per-run `_last_portfolio_weights` reset for determinism, vol_target cash-buffer (sum<=1) instead of leverage. Weights computed on train data only (no lookahead), applied OOS. Artifact: `research_state/PORTFOLIO_SCALING_20261031T155243Z.json` (4 modes). Tests: `tests/test_portfolio_scaling.py` (14 tests). `research_state/RESULTS_SUMMARY.md` updated. Gate: 380 passed (was 366).
- [x] **Stale root handoff superseded**: root `HANDOFF_NEXT_AGENT.md` still listed portfolio scaling as the "current initial task" though it is DONE. This file (`research_state/durable_handoff.md`) is the SINGLE SOURCE OF TRUTH; root handoff is retired. Do NOT re-run portfolio scaling as the opening task.
- [x] **Priority A already green**: crypto options pricing/Greeks/IV is hardened and all adversarial tests pass; do NOT treat A as blocking. Move to the next unimplemented heavy item.
- No active bottlenecks. Next agent starts from a clean green baseline (380/380).

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)

**CRITICAL: BY REPO NAME - CRYPTO OPTIONS ARE #1 PRIORITY (ALREADY GREEN/HARDENED). HEAVY QUANT IMPLEMENTATION ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY. SHIP CODE/TESTS/ARTIFACTS EVERY SESSION.**

You are picking up the **Cryptocurrency-quantitative-options-orderflow-strategy** campaign.
**STATE:** Phases 1-4b + Phase 5 (regime OOS + portfolio scaling) complete. Priority A (crypto options pricing/Greeks/IV) verified green + hardened. Gate GREEN (380/380). Bottlenecks: none. Previous agent left clean, verified state.

### MANDATORY INITIAL TASK: Hedging robustness with PnL decomposition (PRIORITY 1 NOW — portfolio scaling done, Priority A already green)
Repo = crypto options+orderflow; delta/gamma hedging is the options PnL engine. `src/backtest/options_hedging.py::automated_delta_hedging_loop` already has `transaction_cost_bps`, `rebalance_threshold`, `RiskManager`/`CircuitBreaker`, and `max_hedge_notional`, but it returns ONLY `total_pnl` — no delta/gamma/vega/theta/residual attribution. Its `total_pnl` is computed twice confusingly (engine.py lines ~224-231). And `tests/test_options_hedging.py` only covers `delta_hedged_option_pnl` — the risk-integrated loop has ZERO test coverage. Implement and validate:

1) **Add PnL attribution/decomposition to `automated_delta_hedging_loop`** so it returns an `attribution` dict matching `delta_hedged_option_pnl`'s contract: `delta_pnl`, `gamma_pnl`, `vega_pnl`, `theta_pnl`, `residual`, `total_pnl`, `sum_attribution`, with `sum_attribution == total_pnl` exactly. Compute all attribution on in-sample/current-step data only (no lookahead). Fix the duplicated `total_pnl` calculation into a single correct, no-lookahead computation. Keep strict-serialization gating (`serialize_metrics_strict`, `allow_nan=False`).

2) **Extend `tests/test_options_hedging.py`** with tests for `automated_delta_hedging_loop`: attribution reconciliation (`sum_attribution == total_pnl`), transaction costs/slippage reduce PnL (higher bps -> lower-or-equal PnL), rebalance band behavior (`rebalance_threshold` triggers rebalance vs hold), `risk_approved`/`blocked` actions with `RiskManager`/`CircuitBreaker`, determinism (twice byte-identical), strict serialization `allow_nan=False`, deep ITM/OTM/near-expiry/zero-vol edges, and no-lookahead (decisions use only current/past info).

3) **Produce `research_state/HEDGING_ROBUSTNESS_{YYYYMMDDTHHMMSSZ}.json`** covering >=2 cost/slippage scenarios (e.g., 0 bps vs 50 bps) and >=2 rebalance modes (every step vs band), with per-step PnL decomposition, total PnL, rebalance counts, risk actions, and correlation-free risk controls.

4) **Update `research_state/RESULTS_SUMMARY.md`** with a 'Phase 5: Hedging Robustness' section.

5) **Gate**: `python -m pytest tests/ -q` green (>=380 passed, 0 failures). Fail-forward: extend APIs if awkward; fix bugs found. Do not skip implementation for discussion.

## NEXT FOCUS CAMPAIGN (EXECUTE AFTER/WHILE DOING THE INITIAL TASK)
### Phase 5: Production hardening, validation rigor, campaign automation (FORCE HEAVY IMPLEMENTATION)
1. **A) Crypto options pricing/Greeks/IV adversarial hardening** — VERIFIED GREEN + hardened. Remaining: write explicit adversarial audit (findings + verdict) for `src/features/options_pricing.py` + `src/features/iv_surface.py` (quick verification; no change expected unless a concrete edge is found). Targets: `tests/test_options_pricing_greeks_adversarial.py`, `tests/test_iv_surface.py`, `tests/test_phase1_gamma_invariants.py`, `tests/test_numerical_guards.py`.
2. **Hedging robustness** — ACTIVE NOW = current initial task above. Turnover/vol-target/risk-parity already done; now add PnL decomposition + costs/slippage + invariants/stress tests + artifact + RESULTS_SUMMARY section.
3. **Campaign resume hardening** — strengthen `tests/test_campaign_resume.py` (currently minimal: only asserts handoff file exists), ensure atomic checkpoints/resumability; add minimal `scripts/run_campaign.py` with state tracking if orchestration missing.
4. **Telemetry/serialization** — harden non-finite/NaN/Inf guards, ensure JSON-serializable artifacts under all regimes (`tests/test_nonfinite_result_serialization.py` exists; extend guards).
5. **Portfolio scaling** — DONE (do not redo).

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q   # must be 380 passing, 0 failures

# 2) Confirm hedging loop gap (zero coverage of automated_delta_hedging_loop)
grep -n "automated_delta_hedging_loop\|attribution\|total_pnl" tests/test_options_hedging.py src/backtest/options_hedging.py | head -40

# 3) Run existing hedging + portfolio + scaling + regime tests
python -m pytest tests/test_options_hedging.py tests/test_portfolio_scaling.py tests/test_regime_stress_oos.py tests/test_portfolio_walkforward_correlation_adversarial.py -q

# 4) Implement hedging PnL decomposition in automated_delta_hedging_loop; extend tests; run one hedging config; write HEDGING_ROBUSTNESS_*.json artifact; update RESULTS_SUMMARY.md (per initial task above)
```

## HARD CONSTRAINTS
- **Heavy implementation required**: code/tests/artifacts, not just analysis/reports.
- **No checkpoint spam**: commit only when adding executable code/tests/data/artifacts or passing validation.
- **Deterministic & reproducible**: headless, `research_state/` artifacts, explicit configs.
- **Fail-forward**: extend APIs if awkward; fix bugs found.
- **Ship every session**: new code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: 1-4b done + regime OOS done + portfolio scaling done + Priority A green - build on them.
- **Single handoff**: update THIS FILE before ending with fresh UTC timestamp, files changed, rationale, verification commands+results, updated remaining work.

## SUCCESS CRITERIA (MUST HIT BEFORE NEXT HANDOFF)
- [ ] Gate GREEN: `python -m pytest tests/ -q` (>=380 passing, 0 failures)
- [ ] Hedging robustness: PnL decomposition (delta/gamma/vega/theta/residual) added to `automated_delta_hedging_loop`; `sum_attribution == total_pnl` exactly; no-lookahead; strict serialization.
- [ ] Hedging tests added/extended, passing (attribution reconciliation, cost/slippage reduce PnL, rebalance band, risk_approved/blocked, determinism, serialization, edges).
- [ ] `research_state/HEDGING_ROBUSTNESS_*.json` artifact with >=2 cost/slippage scenarios and >=2 rebalance modes.
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 5: Hedging Robustness section.
- [ ] Then continue campaign: campaign resume hardening, telemetry hardening.

## NEXT AGENT INSTRUCTION (CLEAR, TIMESTAMPED, NON-DEFERRABLE)
**EXECUTE NOW - NO QUESTIONS - NO DELAY**
- Timestamp: 2026-10-31T15:54:33Z
- Read this file first. Do NOT re-run portfolio scaling (DONE) or treat Priority A as blocking (already green).
- Start on the Hedging robustness initial task immediately. Produce code/guards/tests/artifacts every turn.
- Verify gate at start and end. Keep >=380 green.
- Update this handoff before finishing with concrete evidence.

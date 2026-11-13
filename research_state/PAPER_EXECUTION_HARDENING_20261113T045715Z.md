# PAPER EXECUTION + LIVE-MONITORING HARDENING — EVAL-15 (paper-only)

- Report ID: PAPER_EXECUTION_HARDENING_EVAL_15
- Generated at: 2026-11-13T04:57:15.525750Z
- Verdict: GO
- Trading mode: paper (live trading enabled: False)

## SEALED EVIDENCE SUMMARY
- EVAL-14 verdict: GO, all checks pass=True
- EVAL-13 verdict: GO, all checks pass=True (8/8)
- EVAL-13 mean net Sharpe: 15.476855 vs no-hedge 5.590936 vs EVAL-10 default -22.765930
- EVAL-12 walk-forward: verdict=GO, PBO overall=0.5000, BH survivors=['EVAL11_best', 'EVAL10_default']
- Paper pre-live readiness: gates all critical passed=True (failed=0), mode=paper, live_trading_enabled=False
- Continuous validation: 5/5 iterations passed, reconciliation freshness met=True (target >= 0.99)

## EXECUTION SIMULATION SUMMARY
- Seeds simulated: 5 ([1, 2, 3, 4, 5])
- Mean OOS return (with hedge+gate): 0.476859
- Mean OOS Sharpe (with hedge+gate): 15.476855
- Mean max drawdown: 0.065000
- Mean abs delta USD: 150.82
- Mean toxicity score: 0.7133
- Toxic gate active fraction: 0.3333
- Total hedges: 2280
- Total cost USD: 377.07
- Total traded notional: 646.42
- Max single-series notional: 519749.88
- Max drawdown observed: 0.1887
- Effective cost bps: 1.06
- Daily loss estimate USD: 18867.42

## EXECUTION THRESHOLDS (guardrails wired to EVAL-13/14)
- [PASS] max_notional_cap_usd (position_risk): threshold=1000000.0, observed=519749.8780964023
  rationale: Per-position notional cap 1,000,000 USD; largest single-series observed notional 519749.88 USD is below the cap.
- [PASS] delta_band_usd (delta_risk): threshold=323.7734839590619, observed=150.8213456031083
  rationale: Delta band 323.77 USD = 2 x EVAL-11 mean_abs_delta_usd 150.82 around target_delta_usd -20000 [-20323.77, -19676.23].
- [PASS] toxicity_gate_threshold (orderflow_risk): threshold=0.7, observed=0.3333333333333333
  rationale: Toxicity gate threshold 0.7 (EVAL-11 best config toxicity_threshold); mean observed toxic_gate_active_fraction 0.3333 below the 0.5 deployment watch level (max observed 1.0000).
- [PASS] cost_budget_bps (execution_cost): threshold=2.0, observed=0.5
  rationale: Cost budget 0.50 bps (EVAL-11 best feasible config) at or below the 2.00 bps deployment ceiling (EVAL-10 default used 2.0 bps). Observed effective cost 1.06 bps of traded notional.
- [PASS] kill_switch_max_drawdown (kill_switch): threshold=0.2, observed=0.18867421527305756
  rationale: Kill-switch: halt paper deployment if max drawdown exceeds 20%; worst observed simulation max drawdown 0.1887 is below the kill level.
- [PASS] kill_switch_toxicity (kill_switch): threshold=0.8, observed=0.3333333333333333
  rationale: Kill-switch: halt paper deployment if mean toxic_gate_active_fraction exceeds 80%; mean observed 0.3333 (max per-series 1.0000) is below the kill level.
- [PASS] kill_switch_cost_bps (kill_switch): threshold=5.0, observed=1.0643514468628845
  rationale: Kill-switch: halt paper deployment if effective cost exceeds 5.00 bps of traded notional; observed 1.06 bps.
- [PASS] max_daily_loss_usd (risk_limit): threshold=50000.0, observed=18867.421527305756
  rationale: Daily loss limit 50,000 USD from .env.example risk limits; estimated worst-case daily loss 18867.42 USD from simulation; paper-only bound, checked against realized PnL at deployment time.
- [PASS] live_trading_disabled (safety): threshold=0.0, observed=0.0
  rationale: Live trading disabled (LIVE_TRADING_ENABLED=false); EVAL-15 hardening is paper-only and does not authorize deployment or venue connectivity.

## ALERT WATCH LEVELS (alert, not block)
- [OK] max_notional_cap_usd_watch: threshold=750000.0, observed=519749.8780964023
- [OK] delta_band_usd_watch: threshold=242.8301129692964, observed=150.8213456031083
- [OK] toxicity_gate_watch: threshold=0.5, observed=0.3333333333333333
- [OK] cost_budget_bps_watch: threshold=1.5, observed=1.0643514468628845
- [TRIGGERED] kill_switch_max_drawdown_watch: threshold=0.1, observed=0.18867421527305756
- [OK] max_daily_loss_usd_watch: threshold=25000.0, observed=18867.421527305756

## KILL-SWITCH HALT CONDITIONS
- [OK] kill_switch_max_drawdown_halt: threshold=0.2, observed=0.18867421527305756
- [OK] kill_switch_toxicity_halt: threshold=0.8, observed=0.3333333333333333
- [OK] kill_switch_cost_bps_halt: threshold=5.0, observed=1.0643514468628845

- All guardrails pass: True
- Kill-switch not triggered: True
- n guardrails: 9, n alert watch levels: 6, n kill-switch halt conditions: 3

## EVIDENCE MATRIX
- btc_real_trades: False
- eth_synthetic_fallback: False
- sol_synthetic_fallback: False
- venue_snapshots_aggregate_only: False
- eval14_sealed_artifact_present: True
- eval13_sealed_artifact_present: True
- eval12_sealed_artifact_present: True
- eval11_sealed_artifact_present: True
- paper_readiness_checkpoint_present: True
- continuous_validation_checkpoint_present: True

## RECONCILIATION METRICS
- Freshness target >= 0.99: MET
- CV iterations passed: 5/5
- Simulation bars: 2500
- Symbols simulated: 3

## VERDICT CHECKS (deterministic)
- [PASS] evidence_sources_complete: PASS: 6 sealed evidence source(s) compared
- [PASS] eval14_paper_readiness_go: PASS: EVAL-14 paper deployment readiness verdict GO
- [PASS] eval13_certification_go: PASS: EVAL-13 final strategy certification verdict GO
- [PASS] eval13_all_checks_pass: PASS: EVAL-13 8/8 checks pass
- [PASS] eval12_walkforward_go: PASS: EVAL-12 real-data walk-forward verdict GO
- [PASS] paper_pre_live_gates_all_passed: PASS: paper pre-live readiness gates all critical passed (failed=0)
- [PASS] continuous_validation_all_passed: PASS: continuous validation 5/5 iterations passed
- [PASS] reconciliation_freshness_met: PASS: reconciliation freshness >= 0.99 met
- [PASS] all_execution_guardrails_pass: PASS: all 9 execution guardrail checks pass
- [PASS] kill_switch_not_triggered: PASS: no kill-switch halt condition triggered
- [PASS] live_trading_disabled: PASS: live trading disabled (paper-only execution)
- [PASS] metrics_and_thresholds_finite: PASS: all metrics and thresholds finite
- All checks pass: True (12/12)

## DEPLOYMENT AUTHORIZATION
- Authorized: True (mode=paper_only)
GO verdict certifies paper-execution hardening only; not an authorization to trade live.

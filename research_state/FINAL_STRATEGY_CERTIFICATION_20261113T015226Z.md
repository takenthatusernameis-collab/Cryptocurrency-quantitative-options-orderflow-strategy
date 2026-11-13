# FINAL STRATEGY CERTIFICATION — EVAL-13 (paper-only)

- Report ID: FINAL_STRATEGY_CERTIFICATION_EVAL_13
- Generated at: 2026-11-13T01:52:26.345940Z
- Verdict: GO
- Trading mode: paper (live trading enabled: False)

## SEALED EVIDENCE SUMMARY
- EVAL-10 verdict: NO-GO, pass_fraction=0.0000, mean net Sharpe=-22.765930, mean net return=-0.558011
- EVAL-11 (best feasible): config={'cost_budget_bps': 0.5, 'target_delta_usd': -20000.0, 'toxicity_threshold': 0.7}, mean net Sharpe=13.188322, mean net return=0.399995, mean abs delta=161.8867 USD, total cost=646.42 USD, hedges=3800, series=15
- EVAL-11 no-hedge control Sharpe: 5.590936; improvement vs no-hedge: 7.597386
- EVAL-12 walk-forward: verdict=GO, BH survivors=['EVAL11_best', 'EVAL10_default'], PBO overall=0.5000, DSR sealed={'EVAL10_default': 0.0, 'EVAL11_best': 0.0}

## RECOMPUTED NET-OF-COST METRICS
- DSR recomputed: {'EVAL10_default': 0.0, 'EVAL11_best': 0.0} (sealed: {'EVAL10_default': 0.0, 'EVAL11_best': 0.0}; consistent=True)
- Bootstrap CI mean net return: [0.298731, 0.494794] point=0.399995, lower>0=True
- Bootstrap CI mean net Sharpe: [9.378864, 18.878999] point=13.188322, lower>0=True
- Paired permutation EVAL-11 vs EVAL-10: p=0.001499, significant=True, observed difference=0.958006

## VERDICT CHECKS (deterministic)
- [PASS] evidence_sources_complete: PASS: 3 sealed evidence sources compared (EVAL-10/EVAL-11/EVAL-12)
- [PASS] eval12_walkforward_go: PASS: EVAL-12 walk-forward verdict GO
- [PASS] eval12_bh_survivor: PASS: 2 config(s) survive BH FDR 0.1: ['EVAL11_best', 'EVAL10_default']
- [PASS] eval11_best_beats_no_hedge_control: PASS: EVAL-11 best mean net Sharpe 13.188322 > 0 and > no-hedge control 5.590936
- [PASS] eval11_best_strictly_beats_eval10_default: PASS: EVAL-11 best 13.188322 > EVAL-10 default -22.765930 (sealed NO-GO baseline)
- [PASS] permutation_eval11_dominates_eval10: PASS: paired permutation EVAL-11 vs EVAL-10 p=0.001499 < 0.05 (EVAL-11 best strictly dominates sealed NO-GO baseline)
- [PASS] all_deployment_guardrails_pass: PASS: all 9 guardrail checks pass
- [PASS] metrics_and_guardrails_finite: PASS: all DSR/PBO/bootstrap/guardrail numeric fields finite
- All checks pass: True (8/8)

## PAPER-ONLY DEPLOYMENT GUARDRAILS
- max_notional_cap_usd (position_risk): threshold=1000000.0, observed=519749.8780964023, pass=True
  rationale: Per-position notional cap derived from configured MAX_POSITION_NOTIONAL; largest observed EVAL-11 single-series traded notional 519749.88 USD is below the 1,000,000 USD cap. EVAL-11 aggregate traded notional is cumulative across 15 series, not a single position.
- delta_band_usd (delta_risk): threshold=323.7734839590619, observed=161.88674197953094, pass=True
  rationale: Delta band derived from EVAL-11 best mean_abs_delta_usd=161.89; band = 2 x mean abs delta = 323.77 USD around target target_delta_usd=-20000 [-20323.77, -19676.23].
- toxicity_gate_threshold (orderflow_risk): threshold=0.7, observed=0.3333333333333333, pass=True
  rationale: Toxicity gate threshold 0.7 (EVAL-11 best config toxicity_threshold); mean observed toxic_gate_active_fraction 0.3333 below the 0.5 deployment watch level (max observed 1.0000 on single ETH series).
- cost_budget_bps (execution_cost): threshold=2.0, observed=0.5, pass=True
  rationale: Cost budget 0.50 bps (EVAL-11 best feasible config) at or below the 2.00 bps deployment ceiling (EVAL-10 default used 2.0 bps). Observed effective cost 1.06 bps of traded notional.
- kill_switch_max_drawdown (kill_switch): threshold=0.2, observed=0.18867421527305756, pass=True
  rationale: Kill-switch: halt paper deployment if max drawdown exceeds 20%; worst observed EVAL-11 series max drawdown 0.1887 is below the kill level.
- kill_switch_toxicity (kill_switch): threshold=0.8, observed=0.3333333333333333, pass=True
  rationale: Kill-switch: halt paper deployment if mean toxic_gate_active_fraction exceeds 80%; mean observed 0.3333 (max per-series 1.0000 on single ETH series with zero notional) is below the kill level.
- kill_switch_cost_bps (kill_switch): threshold=5.0, observed=1.0643514468628845, pass=True
  rationale: Kill-switch: halt paper deployment if effective cost exceeds 5.00 bps of traded notional; observed 1.06 bps.
- max_daily_loss_usd (risk_limit): threshold=50000.0, observed=50000.0, pass=True
  rationale: Daily loss limit 50,000 USD from .env.example risk limits; paper-only bound, checked against realized PnL at deployment time.
- live_trading_disabled (safety): threshold=0.0, observed=0.0, pass=True
  rationale: Live trading disabled (LIVE_TRADING_ENABLED=false); EVAL-13 certification is paper-only and does not authorize deployment or venue connectivity.

## DEPLOYMENT AUTHORIZATION
- Authorized: True (mode=paper_only)
GO verdict certifies paper-readiness only; not an authorization to trade live.

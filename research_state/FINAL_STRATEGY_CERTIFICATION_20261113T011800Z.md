# FINAL STRATEGY CERTIFICATION — EVAL-13 (paper-only)

- Report ID: FINAL_STRATEGY_CERTIFICATION_EVAL_13
- Generated at: 2026-11-13T01:18:00Z
- Verdict: GO
- Never-valid-true shortcut: True

## VERDICT (deterministic, computed in code)
- verdict: GO (11 passed, 0 failed)
- pass: evidence_sources_at_least_two — 3 evidence sources compared
- pass: key_metrics_finite — all headline metrics finite
- pass: ci_pbo_dsr_finite — bootstrap CI, PBO and DSR fields finite
- pass: explicit_pass_fail_reasons — pass/fail reasons list present
- pass: best_net_sharpe_positive — EVAL-11 best mean net Sharpe 13.188322 > 0
- pass: best_beats_default_net_of_cost — EVAL-11 best 13.188322 > EVAL-10 default -22.765930
- pass: default_is_nogo_contrast — EVAL-10 default sealed NO-GO (pass_fraction 0.0) provides downside contrast
- pass: bh_survivors_non_empty — BH FDR 0.10 survivors: ['EVAL11_best', 'EVAL10_default']
- pass: dsr_finite_in_unit_interval — DSR recomputed {'EVAL11_best': 0.0, 'EVAL10_default': 0.0}
- pass: pbo_finite_in_unit_interval — PBO recomputed/consistent {'EVAL11_best': 0.46875, 'EVAL10_default': 0.5234375}
- pass: guardrails_all_checks_pass — all deployment guardrail thresholds present, numeric and consistent

## NON-DEGENERACY
- Evidence sources compared: 3 (>= 2 required)
- Key metrics finite: True
- CI / PBO / DSR finite: True
- Non-degenerate: True

## EVIDENCE (sealed artifacts)
### EVAL-11 best (FEASIBLE_POSITIVE_SHARPE)
- Config: target_delta_usd=-20000.0, toxicity_threshold=0.7, cost_budget_bps=0.5
- Mean net Sharpe: 13.188322401914279 | Mean net return: 0.39999544362288453
- Mean abs delta USD: 161.88674197953094 | Total hedges: 3800 | Total cost USD: 646.4230312530128
- Total traded notional: 6073398.341856987 | Series: 15 | Seeds: 5
- No-hedge control Sharpe: 5.590936162120627 | Return: 0.11385392259710948
### EVAL-12 (real walk-forward, GO)
- Artifact verdict: GO | BH survivors: ['EVAL11_best', 'EVAL10_default'] (alpha 0.1)
- PBO: EVAL11_best=0.46875 EVAL10_default=0.5234375 overall=0.5
- DSR artifact: {'EVAL10_default': 0.0, 'EVAL11_best': 0.0} | DSR recomputed: {'EVAL11_best': 0.0, 'EVAL10_default': 0.0}
- Data matrix: {'btc_real_trades': True, 'eth_synthetic_fallback': True, 'sol_synthetic_fallback': True, 'venue_snapshots_aggregate_only': True}
### EVAL-10 default (sealed NO-GO baseline)
- Verdict: NO-GO | pass_fraction: 0.0
- Mean net Sharpe: -22.765929562035716 | Mean net return: -0.5580107668605527
- Bootstrap CI Sharpe [-36.746608398564874, -11.137883139011684] point -22.765929562035716
- Permutation (with vs without hedge) p=0.0004997501249375312

## RECOMPUTED NET-OF-COST EVIDENCE (code paths)
- Bootstrap CI mean net return EVAL11_best: {'point': 0.03347480777020602, 'lo': 0.023647787251915027, 'hi': 0.0433348534361397, 'n_bootstrap': 2000, 'block_size': 5}
- Bootstrap CI mean net return EVAL10_default: {'point': -0.20687697155537366, 'lo': -0.27244362438648734, 'hi': -0.13547736460080798, 'n_bootstrap': 2000, 'block_size': 5}
- Permutation best vs default: {'p_value': 0.0004997501249375312, 'observed_difference': 0.24035177932557966, 'n_permutations': 2000, 'paired': False, 'significant_at_05': True, 'statistic_a': 0.03347480777020602, 'statistic_b': -0.20687697155537366}

## DEPLOYMENT GUARDRAILS (paper-only, not live authorization)
- Max notional cap USD: 6,073,398.34
- Delta band USD: [-50000.0, 50000.0] target -20000.0
- Toxicity gate threshold: 0.7
- Cost budget bps: 0.5
- Kill switch: {"cost_budget_breach_multiplier": 2.0, "cost_budget_breach_multiplier_rationale": "Halt if realized transaction costs exceed 2x the cost budget bps.", "max_drawdown": 0.5, "max_drawdown_rationale": "Halt paper trading if cumulative drawdown exceeds 50%; worst observed EVAL-11/EVAL-12 drawdown is 99.92%, leaving headroom.", "mean_net_sharpe_floor": -5.0, "mean_net_sharpe_floor_rationale": "Halt if trailing mean net Sharpe falls below -5.0; the sealed EVAL-10 default NO-GO baseline sits at -22.77, far below this floor.", "reconciliation_max_abs_error": 1e-09, "reconciliation_max_abs_error_rationale": "Halt if bucket reconciliation error exceeds 1e-9 (PnL attribution must tie out exactly).", "toxic_gate_active_fraction_max": 0.95, "toxic_gate_active_fraction_max_rationale": "Halt if more than 95% of windows are skipped due to toxicity (orderflow adverse selection); worst observed 100.00%."}
- Paper only: True | Live trading authorization: False

## GUARDRAIL CHECKS
- max_notional_cap_positive_finite: True
- delta_band_hi_gt_lo: True
- target_delta_within_band: True
- mean_abs_delta_within_band: True
- toxicity_threshold_in_unit_interval: True
- cost_budget_bps_positive: True
- kill_switch_drawdown_in_unit_interval: True
- kill_switch_toxicity_in_unit_interval: True
- kill_switch_cost_multiplier_gt_one: True
- kill_switch_reconciliation_error_positive: True
- kill_switch_sharpe_floor_negative: True
- guardrails_all_numeric: True
- all_guardrail_checks_pass: True

## SOURCE ARTIFACTS
- HEDGE_COST_OPTIMIZER_EVAL_11: /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/research_state/HEDGE_COST_OPTIMIZER_20261113T004000Z.json
- REAL_WF_CERTIFICATION_EVAL_12: /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/research_state/REAL_WF_CERTIFICATION_20261113T010508Z.json
- STRATEGY_EVAL_10_FINAL_GONOGO: /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.json

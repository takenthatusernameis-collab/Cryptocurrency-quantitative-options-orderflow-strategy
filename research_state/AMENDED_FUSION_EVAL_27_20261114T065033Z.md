# AMENDED_FUSION_EVAL_27_20261114T065033Z — AMENDED FUSION EVALUATION (EVAL-27, Path B)

- generated_at: 2026-11-14T06:50:33.991340Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real (authenticity_verified=False)
- never_valid_true: True
- source_report_id: INTEGRATED_OPTIONS_ORDERFLOW_EVAL_18 (sealed EVAL-18, read-only)
- overall_verdict: **NO-GO**
- checks_passed: 5/7
- failed_checks: ['options_signal_exists', 'combined_net_of_cost_superior']

## Per-variant net-of-cost walk-forward (real data, single-snapshot options leg)

### combined
- oos_return: -0.31747080465903726
- oos_sharpe: -100.33254499674707
- oos_max_drawdown: 0.31747080465903726
- oos_trade_count: None
- num_windows: 3

### options_only
- oos_return: -0.4356686057040438
- oos_sharpe: -483.87565740476566
- oos_max_drawdown: 0.4356686057040438
- oos_trade_count: None
- num_windows: 3

### orderflow_only
- oos_return: -0.08317830244934434
- oos_sharpe: 0.7851262573484745
- oos_max_drawdown: 0.31903987333846484
- oos_trade_count: None
- num_windows: 3

### flat
- oos_return: 0.0
- oos_sharpe: 0.0
- oos_max_drawdown: 0.0
- oos_trade_count: None
- num_windows: 3

## Information coefficient
- combined_ic_mean: -0.07695863562664447
- combined_ic_tstat: -5.056446145389047
- options_ic_mean: 0.0
- orderflow_ic_mean: -0.008195014529083021

## Permutation test (combined vs best single pillar)
- p_value: 0.000999000999000999

## Toxicity (VPIN)
- mean_toxicity: 0.440837011802814
- toxic_gate_active_fraction: 0.225

## Adjudication
- options leg is degenerate on a single real snapshot (options_ic_mean=0, options_signal_exists FAIL)
- combined does not beat best pillar net-of-cost (combined_sharpe=-100.33 vs orderflow_only_sharpe=0.79)
- orderflow-only has positive but modest Sharpe (0.79) on current real tape
- NO defensible edge established on current real data with degenerate options leg
- defensible_edge: false

This is an additive EVAL-27 Path B artifact. The sealed single-snapshot loader semantics are unchanged. Never emits {"valid": true}. Never relabels synthetic as real.

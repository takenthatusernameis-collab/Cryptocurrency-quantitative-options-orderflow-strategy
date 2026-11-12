# Strategy Evaluation Report
Timestamp: 2026-10-31T00:00:00Z
Data provenance: synthetic
Seeds: [1, 2, 3, 4, 5]
Allocation modes: ['equal_weight', 'risk_parity', 'vol_target']

## Headline
- Strategy Sharpe: 0.009481
- Strategy total return: -0.002449
- Strategy max drawdown: 0.072498
- Null (zero-signal random) Sharpe: -0.051927
- Null total return: -0.003658

## Gates
- nonzero_oos_return: PASS (value=-0.0024485702940080954)
- positive_sharpe: PASS (value=0.009481179050770524)
- beats_null: PASS (value=0.009481179050770524)
- ci_brackets: PASS (value=None)

## Verdict: GO

## Baseline comparison (deltas vs null)
- max_drawdown: +0.041246
- sharpe: +0.061408
- total_return: +0.001209

Verdict metric: strategy
Compared metrics: 3

## Attribution (reconciled)
- reconciled_total: 0.01641937643813595
- grand_total: 0.01641937643813595
- max_abs_error: 0.0
- reconciliation_ok: True
- num_buckets: 1

## Baselines (aggregated)
- delta_hedged_buy_and_hold_long_gamma: sharpe=+0.023299 total_return=-0.000997 max_drawdown=+0.043002 oos_return=-0.000997
- naive_orderflow_threshold_no_hedge: sharpe=+0.029475 total_return=+0.000046 max_drawdown=+0.046609 oos_return=+0.000046
- zero_signal_random_seed_fixed: sharpe=-0.051927 total_return=-0.003658 max_drawdown=+0.031253 oos_return=-0.003658

---
Paper-only evaluation. Synthetic data. No live trading.

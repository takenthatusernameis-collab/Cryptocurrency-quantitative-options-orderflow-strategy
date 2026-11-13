# ORDERFLOW ALPHA & TOXICITY EVALUATION — EVAL-17 (paper-only)

- Report ID: ORDERFLOW_ALPHA_TOXICITY_EVAL_17
- Generated at: 2026-11-13T08:00:05.714236Z
- Verdict: NO-GO
- Trading mode: paper (live enabled: False)
- Symbol: BTC @ spot 65000.0

## BARS (causal, from real trade tape)
- Bars: 240 (2026-10-31T06:16:23.656379Z -> 2026-10-31T07:16:21.656379Z, 15.0s each, 1000 trades)

## CAUSAL SIGNAL SERIES (no lookahead)
- Bars: 240, mean signal -0.042242, mean |signal| 0.264454

## ALPHA (information coefficient + decay)
- IC by horizon: {'1': -0.00817794856015245, '5': -0.02106966716799313, '20': 0.004662572140896516}
- IC mean -0.008195, std 0.010505, t-stat -1.351164
- IC bootstrap CI [-0.021070, 0.004663] (point -0.008195)
- IC decay slope 6.420260e-03

## PERMUTATION TEST (mean IC vs zero)
- p_value 0.088911, observed_difference -0.038304, significant_at_05 False, n_permutations 1000

## TOXICITY (VPIN, causal)
- Mean 0.440837, p95 1.000000, range [0.001403, 1.000000]
- Threshold 0.7, fraction above 0.225000, gate engages True
- Toxicity measured: True

## NET-OF-COST WITH/FORWARD (orderflow signal vs always-flat control)
- With signal: return -0.590291, Sharpe -53.363344, max-DD 0.590291, cost 43.12 USD, trades 58, windows 3
- Without (flat): return 0.000000, Sharpe 0.000000, max-DD 0.000000, cost 0.00 USD
- Net delta (with - without): return -0.590291, Sharpe -53.363344

## EVIDENCE MATRIX
- orderflow_loaded: True
- n_trades: 1000
- n_liquidations: 20
- n_funding_rates: 8
- symbol: BTC
- venue: synthetic
- bars_constructed: True
- causal_signal_computed: True
- ic_computed: True
- permutation_computed: True
- toxicity_measured: True
- net_of_cost_run: True
- paper_only: True
- live_trading_enabled: False

## VERDICT CHECKS (deterministic)
- [PASS] signal_exists_ic_nonzero: PASS: mean IC -8.195015e-03 nonzero (> 1e-09)
- [FAIL] ic_significant: FAIL: IC not significant (|t|=1.3512 <= 1.96, permutation p=0.0889 >= 0.05)
- [PASS] toxicity_measured: PASS: toxicity mean 0.4408 in (0,1), gate engages fraction 0.2250
- [PASS] net_of_cost_with_vs_without: PASS: net-of-cost comparison finite (with -0.590291 vs without 0.000000, cost 43.12 USD)
- [PASS] no_lookahead_asserted: PASS: causal no-lookahead signal asserted and tested
- All checks pass: False (4/5)

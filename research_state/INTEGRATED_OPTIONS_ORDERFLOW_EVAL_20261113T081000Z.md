# INTEGRATED OPTIONS + ORDERFLOW EVALUATION — EVAL-18 (paper-only)

- Report ID: INTEGRATED_OPTIONS_ORDERFLOW_EVAL_18
- Generated at: 2026-11-13T08:10:00Z
- Verdict: NO-GO
- Trading mode: paper (live enabled: False)
- Symbol: BTC @ spot 65000.0

## BARS (causal, from real orderflow tape)
- Bars: 240 (2026-10-31T06:16:23.656379Z -> 2026-10-31T07:16:21.656379Z, 15.0s each, 1000 trades)

## OPTIONS ALPHA (reconstructed IV surface, EVAL-16 pattern)
- Surface points: 30 across 3 expiries
- Calibration residual: max abs 0.000e+00, mean 0.000e+00
- Gamma flip level: 58207.50, GEX flip distance: 0.104500
- GEX signal: 1.0000, skew signal: 0.0000, calib signal: -0.0000
- Options signal raw: 0.3333

## OPTIONS ALPHA (IC + decay)
- IC by horizon: {'1': 0.0, '5': 0.0, '20': 0.0}
- IC mean 0.000000, std 0.000000, t-stat 0.000000

## ORDERFLOW ALPHA (IC + decay, EVAL-17 causal signal)
- IC by horizon: {'1': -0.00817794856015245, '5': -0.02106966716799313, '20': 0.004662572140896516}
- IC mean -0.008195, std 0.010505, t-stat -1.351164

## COMBINED ALPHA (IC + decay)
- IC by horizon: {'1': -0.10828468387648257, '5': -0.07880029561638165, '20': -0.04379092738706918}
- IC mean -0.076959, std 0.026362, t-stat -5.056446
- IC bootstrap CI [-0.108285, -0.043791]

## PERMUTATION TEST (combined vs best single pillar)
- p_value 0.000999, observed_difference 0.297395, significant_at_05 True, n_permutations 1000

## TOXICITY (VPIN, causal, EVAL-17 pattern)
- Mean 0.440837, p95 1.000000, range [0.001403, 1.000000]
- Threshold 0.7, fraction above 0.225000, gate engages True
- Toxicity measured: True

## COMBINED SIGNAL (fusion + toxicity gate)
- Bars: 240, long 59, short 0, flat 181
- Mean signal: 0.245833

## NET-OF-COST INTEGRATED WALK-FORWARD (combined vs 3 controls)
- Combined:    return -0.634326, Sharpe -37.073042, max-DD 0.634326, cost 48.11 USD, trades 51, windows 3
- Options-only: return -0.569792, Sharpe -63.794670, max-DD 0.569792, cost 51.01 USD
- Orderflow-only: return -0.634770, Sharpe -37.282646, max-DD 0.634770, cost 48.10 USD
- Flat control: return 0.000000, Sharpe 0.000000, max-DD 0.000000, cost 0.00 USD

## STATISTICAL DEFENSIBILITY
- DSR: combined=0.000000, options_only=0.000000, orderflow_only=0.000000, flat=0.000000
- PBO overall: 0.000000 (n_configs=16)
- BH-FDR: alpha=0.1, m_tests=3, rejected=['combined_vs_options_only', 'combined_vs_flat', 'combined_vs_orderflow_only']
- Permutation pairs: combined_vs_options_only=0.001996, combined_vs_orderflow_only=0.003992, combined_vs_flat=0.001996

## EVIDENCE MATRIX
- options_chain_loaded: True
- n_options_quotes: 30
- orderflow_loaded: True
- n_trades: 1000
- n_liquidations: 20
- n_funding_rates: 8
- symbol: BTC
- venue: synthetic
- bars_constructed: True
- causal_orderflow_signal_computed: True
- causal_options_signal_computed: True
- combined_signal_computed: True
- ic_computed: True
- permutation_computed: True
- toxicity_measured: True
- integrated_walkforward_run: True
- paper_only: True
- live_trading_enabled: False
- options_signal_from_reconstructed_surface: True
- toxicity_gate_applied_to_all_pillars: True

## VERDICT CHECKS (deterministic)
- [FAIL] options_signal_exists: FAIL: options mean IC 0.000000e+00 indistinguishable from zero (<= 1e-09)
- [PASS] orderflow_signal_exists: PASS: orderflow mean IC -8.195015e-03 nonzero (> 1e-09)
- [PASS] combined_ic_significant: PASS: combined IC significant (|t|=5.0564 > 1.96, permutation p=0.0010)
- [FAIL] combined_net_of_cost_superior: FAIL: combined not superior (combined -37.073042 vs options -63.794670, orderflow -37.282646, flat 0.000000; cost applied True)
- [PASS] toxicity_gate_measured: PASS: toxicity mean 0.4408 in (0,1), gate engages fraction 0.2250 (measured EVAL-17 VPIN)
- [PASS] no_lookahead_asserted: PASS: causal no-lookahead signal asserted and tested
- [PASS] guardrails_consistent_with_eval13_14_15: PASS: guardrails consistent (delta band ±323.77 USD around -20000.0, toxicity gate 0.7, cost budget 0.5 bps, kill-switch DD 0.2/tox 0.8/cost 5.0 bps, max notional 1000000.0 USD, max daily loss 50000.0 USD)
- All checks pass: False (5/7)

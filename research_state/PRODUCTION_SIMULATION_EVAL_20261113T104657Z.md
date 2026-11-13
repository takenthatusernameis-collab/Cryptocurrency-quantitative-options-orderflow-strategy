# PRODUCTION NET-OF-COST SIMULATION & ROBUSTNESS CERTIFICATION — EVAL-19 (paper-only)

- Report ID: PRODUCTION_SIMULATION_EVAL_19
- Generated at: 2026-11-13T10:46:57.348960Z
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

## COMBINED ALPHA (IC + decay)
- IC by horizon: {'1': -0.10828468387648257, '5': -0.07880029561638165, '20': -0.04379092738706918}
- IC mean -0.076959, std 0.026362, t-stat -5.056446
- IC bootstrap CI [-0.108285, -0.043791]

## TOXICITY (VPIN, causal, EVAL-17 pattern)
- Mean 0.440837, p95 1.000000, range [0.001403, 1.000000]
- Threshold 0.7, fraction above 0.225000, gate engages True, measured True

## NET-OF-COST MULTI-SEED WALK-FORWARD (seeds 1-10, combined vs 4 controls)
- combined      : return -0.396136, Sharpe -30.063030, max-DD 0.396136, cost 13.92 USD, trades 95.0, windows 3.0
- flat          : return 0.000000, Sharpe 0.000000, max-DD 0.000000, cost 0.00 USD, trades 0.0, windows 3.0
- options_only  : return -0.270734, Sharpe -21.548226, max-DD 0.270734, cost 14.46 USD, trades 119.5, windows 3.0
- orderflow_only: return -0.398124, Sharpe -30.050428, max-DD 0.398124, cost 13.92 USD, trades 95.0, windows 3.0

## COST SENSITIVITY (pure spread, 0 / 0.5 / 1 / 5 bps)
- 0.0 bps: Sharpe -22.572649, return -0.590208, cost 0.00 USD, trades 46.0
- 0.5 bps: Sharpe -22.572649, return -0.590208, cost 26.18 USD, trades 46.0
- 1.0 bps: Sharpe -22.572649, return -0.590208, cost 52.35 USD, trades 46.0
- 5.0 bps: Sharpe -22.572649, return -0.590208, cost 261.77 USD, trades 46.0

## REGIME STRESS (high vs low VPIN toxicity)
- Toxicity median: 0.417588
- High-tox regime: windows 3, return -0.993755, Sharpe -28.488097, max-DD 0.993755
- Low-tox regime: windows 0, return 0.000000, Sharpe 0.000000, max-DD 0.000000
- IV skew slope: 0.000000 (low_skew)

## KILL-SWITCH TRIGGERS (DD 20% / toxicity 80% / cost 5 bps)
- Max DD: 0.494440 (threshold 0.2) -> TRIGGERED
- Max toxicity: 1.000000 (threshold 0.8) -> TRIGGERED
- Main cost bps: 1.3916 (threshold 5.0) -> ok
- Any triggered: True

## STATISTICAL DEFENSIBILITY
- Combined IC mean -0.076959, t-stat -5.056446
- Permutation p 0.000999 (significant_at_05 True)
- DSR: combined=0.000000, options_only=0.000000, orderflow_only=0.000000, flat=0.000000
- PBO overall: 0.750000 (n_configs=16)
- BH-FDR: alpha=0.1, m_tests=3, rejected=['combined_vs_orderflow_only', 'combined_vs_flat', 'combined_vs_options_only']
- Permutation pairs: combined_vs_options_only=0.003992, combined_vs_orderflow_only=0.001996, combined_vs_flat=0.001996

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
- toxicity_gate_measured: True
- multi_seed_walkforward_run: True
- cost_sensitivity_grid: [0.0, 0.5, 1.0, 5.0]
- integrated_walkforward_run: True
- paper_only: True
- live_trading_enabled: False
- options_signal_from_reconstructed_surface: True
- toxicity_gate_applied_to_all_pillars: True

## VERDICT CHECKS (deterministic)
- [PASS] signal_exists: PASS: combined mean IC -7.695864e-02 nonzero (> 1e-09)
- [PASS] ic_significant: PASS: combined IC significant (|t|=5.0564 > 1.96, permutation p=0.0010)
- [FAIL] net_of_cost_superior_vs_controls: FAIL: combined not superior (combined -30.063030 vs options -21.548226, orderflow -30.050428, flat 0.000000; cost applied True)
- [PASS] toxicity_gate_measured: PASS: toxicity mean 0.4408 in (0,1), gate engagement 0.2250 (non-degenerate, gate engages but does not stand down every bar)
- [FAIL] robust_across_regimes: FAIL: not robust across regimes (low 0.000000, high -28.488097, flat 0.000000)
- [PASS] guardrails_consistent_with_eval13_14_15: PASS: guardrails consistent (delta band ±323.77 USD around -20000.0, toxicity gate 0.7, cost budget 0.5 bps, kill-switch DD 0.2/tox 0.8/cost 5.0 bps, max notional 1000000.0 USD, max daily loss 50000.0 USD)
- All checks pass: False (4/6)

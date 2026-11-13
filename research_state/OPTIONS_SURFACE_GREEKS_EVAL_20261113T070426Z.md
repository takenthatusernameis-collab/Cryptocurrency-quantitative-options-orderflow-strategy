# OPTIONS VOL-SURFACE & GREEKS EVALUATION — EVAL-16 (paper-only)

- Report ID: OPTIONS_SURFACE_GREEKS_EVAL_16
- Generated at: 2026-11-13T07:04:26Z
- Verdict: NO-GO
- Trading mode: paper (live enabled: False)
- Symbol: BTC @ spot 65000.0

## DATA QUALITY (measured, not assumed)
- Quotes: 30 (missing IV: 0, missing mark: 0)
- BS(mark_iv) vs mark: max abs 8516.3642, mean abs 3192.6835, mean signed 3070.8734
- Put-call parity: pairs 15, min -6480.2391, max 6634.6831, mean 84.8653, mean abs 3938.5249, max abs 6634.6831
- Mark IV: min 0.4181, max 0.7991, mean 0.6301, distinct 30

## SURFACE RECONSTRUCTION
- Points: 30 across 3 expiries
- Calibration residual: mean 0.000e+00, std 0.000e+00, max abs 0.000e+00

## ARBITRAGE CHECKS (reconstructed IV grid)
- Butterfly: checks 9, violations 1, max violation 4.006e-01
- Calendar: checks 10, violations 0, max violation 0.000e+00
- Arbitrage-free: False

## GREEKS (recomputed from reconstructed surface)
- Evaluated: 30
- Stored-vs-recomputed delta error: mean 0.3402, max 0.8494
- Delta FD match: 30/30 (fraction 1.0000)
- Vega FD match: 30/30 (fraction 1.0000)

## BOOK GREEKS
- Total GEX: 1052954758.9925
- Gamma flip level: 58207.50
- Put-call ratio: 1.1961
- Max pain: 65000.00
- IV skew: 0.1063
- Avg bid-ask spread: 2.0369, total OI 145568

## NET-OF-COST DELTA HEDGE (OOS, with options vs no-options)
- Windows: 25 across seeds [1, 2, 3, 4, 5] (strike 65000.0, spread 1.0 bps)
- With options: mean return 0.000051, mean Sharpe 2.548602, mean max-DD 0.000000
- Without options (underlying hold): mean return 1.574455, mean Sharpe 2.722552, mean max-DD 0.492238

## EVIDENCE MATRIX
- options_chain_loaded: True
- surface_reconstructed: True
- greeks_recomputed_from_surface: True
- arbitrage_checked_on_grid: True
- delta_hedge_oos_windows: True
- book_greeks_present: True
- paper_only: True
- live_trading_enabled: False

## VERDICT CHECKS (deterministic)
- [FAIL] data_quality_bs_vs_mark: FAIL: BS(mark_iv) vs mark max abs 8516.3642 > 1.0
- [FAIL] data_quality_put_call_parity: FAIL: parity residual max abs 6634.6831 > 1.0
- [PASS] data_quality_mark_iv_range: PASS: mark IV range [0.4181, 0.7991] within [0.01, 5.0]
- [PASS] surface_calibration_residual: PASS: surface residual max abs 0.000e+00 <= 1.0e-06
- [FAIL] surface_arbitrage_free: FAIL: 1 arbitrage violations (butterfly 1, calendar 0)
- [FAIL] greeks_stored_vs_recomputed_delta: FAIL: mean stored-vs-recomputed delta error 0.3402 > 0.05
- [PASS] greeks_analytic_vs_finite_difference: PASS: analytic vs FD match fraction 1.0000 >= 0.99
- [PASS] net_of_cost_delta_hedge_finite: PASS: delta-hedge metrics finite (with Sharpe 2.5486, return 0.0001)
- [PASS] metrics_non_degenerate: PASS: all measured blocks finite and non-empty
- All checks pass: False (5/9)

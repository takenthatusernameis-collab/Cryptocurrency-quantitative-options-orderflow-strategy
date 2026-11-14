# REAL_TAPE_INGESTION_22 — REAL_TAPE_INGESTION (EVAL-22)

- generated_at: 2026-11-14T02:53:22.130434Z
- overall_verdict: **GO**
- reason: adequate real tape(s) passed the sealed verdict battery
- data_provenance: real
- candidates discovered: 1
- adequate real tapes: 1
- floors: {'min_returns': 1000, 'min_windows': 20, 'bar_duration_seconds': 15.0}

## Candidates

### `data/raw/orderflow_okx_BTC-USD-SWAP.json`
- venue/symbol: `okx` / `BTCUSDSWAP`
- content_sha256: `865d2e06157331bb…`
- n_trades: 57400
- span: 23266.0s (2026-11-13T20:19:45.772000Z → 2026-11-14T02:47:31.736000Z)
- bars/returns/windows: {'n_bars': 1552, 'n_returns': 1551, 'n_windows': 35, 'start_timestamp': '2026-11-13T20:19:45.772000Z', 'end_timestamp': '2026-11-14T02:47:31.736000Z', 'bar_return_mean_bps': -0.1434400629797912, 'bar_return_std_bps': 3.674651635554426, 'bar_return_tstat': -1.5373055418356731}
- causal_no_lookahead: True
- microstructure_sane: True
- verdict: **GO**
- checks passed: 8/8
  - [PASS] measurement_reproducible: Two consecutive full evaluations must produce byte-identical artifacts.
  - [PASS] sample_adequate_declared: Adequacy is judged against the pre-declared floors; an inadequate sample is a legitimate, sealable outcome.
  - [PASS] sizing_consistent: Requested max_position_pct must equal RiskConfig.max_position_pct and engine rejections must be counted, not swallowed.
  - [PASS] sharpe_basis_valid: Sharpe must be reproducible from the emitted per-bar returns with the bar-duration annualisation.
  - [PASS] non_degenerate_pillars_reported: Every pillar with < 2 unique values must be flagged explicitly (options leg is expected degenerate on the current snapshot).
  - [PASS] net_of_cost_honest: gross, net, turnover and cost bps must be emitted for all four series, cost non-negative.
  - [PASS] ic_reported_with_power: IC mean, t-stat, n and the minimum detectable effect must be emitted.
  - [PASS] strict_serialization: Artifact must validate with allow_nan=False and never contain {"valid": true}.

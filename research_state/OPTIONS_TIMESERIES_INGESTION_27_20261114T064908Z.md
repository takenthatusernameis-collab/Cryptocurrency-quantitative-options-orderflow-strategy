# OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z — OPTIONS TIME-SERIES INGESTION & TRADABILITY (EVAL-27, Path A)

- generated_at: 2026-11-14T06:49:08.230976Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real (authenticity_verified=false)
- never_valid_true: True
- symbol: BTC  venue: okx
- spot_used: 66825.3  rate_used: 0.0

## Snapshot series

- n_snapshots: 3
- span_seconds: 10659.824732
- start_timestamp: 2026-11-14T03:49:23.491920Z
- end_timestamp: 2026-11-14T06:47:03.316652Z

## Time-variation diagnostics (across snapshots)

- iv_surface_point_count_stdev: 1.247219128924647
- atm_delta_stdev: 9.955629495563858e-09
- atm_gamma_stdev: 1.7644629200374098e-09
- total_gex_stdev: 0.0
- put_call_ratio_stdev: 0.03632214285173199
- iv_skew_stdev: 0.0
- parity_max_residual_stdev: 0.008720983637268264
- signal_stdev_over_mean: 1.3894952791126824

## Options-leg tradability

- options_leg_tradable: false
- reason: 1017 put-call parity violation(s) across snapshots
- overall_verdict: **NO-GO**
- overall_reason: 1017 put-call parity violation(s) across snapshots

## Per-snapshot diagnostics

### data/raw/options_okx_BTC_20261114T034546Z.json
- acquired_at: 2026-11-14T03:49:23.491920Z
- snapshot_timestamp: 2026-11-14T03:49:23.491920Z
- n_quotes: 731, n_contracts: 731, n_strikes: 88, n_expiries: 12
- min_strike: 25000.0, max_strike: 240000.0
- iv_surface_points: 731, iv_residual_max_abs: 0.0
- atm_delta: 2.10944595124829e-11, atm_gamma: 5.376558064116484e-12, total_gex: 0.0
- put_call_ratio: 1.020143146196358, iv_skew: 0.0, max_pain: 64000.0
- parity_pairs_checked: 341, parity_max_abs_residual: 133172.85030000002, parity_violations: 341
- calendar_arb_violations: 0, butterfly_arb_violations: 0
- quotes_with_iv: 731, quotes_with_greeks: 1
- content_sha256: 1cb40cde29777c27e544ac60c5f10a722cfb97d92114b6a5f5e489ec3e58467c

### data/raw/options_okx_BTC_20261114T035050Z.json
- acquired_at: 2026-11-14T03:54:26.712854Z
- snapshot_timestamp: 2026-11-14T03:54:26.712854Z
- n_quotes: 728, n_contracts: 728, n_strikes: 88, n_expiries: 12
- min_strike: 25000.0, max_strike: 240000.0
- iv_surface_points: 728, iv_residual_max_abs: 0.0
- atm_delta: 2.2988538850299278e-10, atm_gamma: 5.2436026144431036e-11, total_gex: 0.0
- put_call_ratio: 1.0316381095156755, iv_skew: 0.0, max_pain: 64000.0
- parity_pairs_checked: 338, parity_max_abs_residual: 133172.85030000002, parity_violations: 338
- calendar_arb_violations: 0, butterfly_arb_violations: 0
- quotes_with_iv: 728, quotes_with_greeks: 1
- content_sha256: 375aa0cfe73ae4daa45cb2fb9fa766865a8616e44633f4e363fe7378d564824a

### data/raw/options_okx_BTC_20261114T064702Z.json
- acquired_at: 2026-11-14T06:47:03.316652Z
- snapshot_timestamp: 2026-11-14T06:47:03.316652Z
- n_quotes: 730, n_contracts: 730, n_strikes: 89, n_expiries: 12
- min_strike: 25000.0, max_strike: 240000.0
- iv_surface_points: 730, iv_residual_max_abs: 0.0
- atm_delta: 2.124379522294717e-08, atm_gamma: 3.771675499214063e-09, total_gex: 0.0
- put_call_ratio: 1.102295736584118, iv_skew: 0.0, max_pain: 64000.0
- parity_pairs_checked: 338, parity_max_abs_residual: 133172.86880000003, parity_violations: 338
- calendar_arb_violations: 0, butterfly_arb_violations: 0
- quotes_with_iv: 730, quotes_with_greeks: 1
- content_sha256: 8d1148f7258cf67322b3d2e3cda1f6604aba8a113f05350628c81519c1fd35e5


This is an additive EVAL-27 Path A artifact. The sealed single-snapshot loader semantics (src.campaign.integrated.load_real_options_chain) are unchanged. Never emits {"valid": true}. Never relabels synthetic as real.

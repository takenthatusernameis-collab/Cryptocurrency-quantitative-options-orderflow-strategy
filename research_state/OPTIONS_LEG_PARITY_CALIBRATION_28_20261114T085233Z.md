# OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z — PER-EXPIRY FORWARD-CALIBRATED PUT-CALL PARITY (EVAL-28)

- generated_at: 2026-11-14T08:52:33.989737Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real (authenticity_verified=false)
- never_valid_true: True
- symbol: BTC  venue: okx
- reference_spot (hint only, not used for parity): 66825.3  rate_used: 0.0

## Verdict

- parity_consistent: true
- overall_verdict: **GO**
- overall_reason: per-expiry forward-calibrated put-call parity holds on 1017/1017 pairs (100.0%) across 3 snapshot(s); min R2=0.999919

## Code paths

- `src/data/options_timeseries.py`
- `src/data/loader.py`
- `tests/test_options_timeseries_parity_calibration.py`

## Verification

```
python3 -m py_compile src/data/options_timeseries.py
```
```
PYTHONPATH=. python3 -m pytest -q tests/test_options_timeseries_parity_calibration.py -> 3 passed
```
```
PYTHONPATH=. python3 -m pytest -q tests/test_integrated_options_orderflow_evaluation.py tests/test_real_data_inputs.py tests/test_public_export_acquisition.py tests/test_options_timeseries_parity_calibration.py -> 44 passed
```

## Why this differs from EVAL-27

EVAL-27 applied a single constant spot (66825.3) to every strike/expiry, so the `S - K` parity term was wrong away from the ATM and every pair falsely reported a violation. Here each expiry's forward is fitted from the chain itself (`C_mid - P_mid = F/S - K/S`); a genuine arbitrage must survive the per-expiry fit.

## Per-snapshot calibration

### data/raw/options_okx_BTC_20261114T034546Z.json
- snapshot_timestamp: 2026-11-14T03:49:23.491920Z
- n_pairs: 341, n_expiries: 12, skipped: 0
- implied_spot range: [66702.25, 70141.57]
- min R2: 0.999919; median|p90|max residual USD: 27.55 / 167.21 / 250.70
- pairs within bid-ask spread: 341/341
  - 2026-11-15T00:00:00Z: n=26 implied_spot=66986.53 R2=0.999919 med=15.20 p90=34.09 max=47.44 within_spread=26/26
  - 2026-11-16T00:00:00Z: n=26 implied_spot=66702.25 R2=0.999980 med=8.81 p90=20.27 max=28.55 within_spread=26/26
  - 2026-11-17T00:00:00Z: n=24 implied_spot=66835.48 R2=0.999988 med=10.37 p90=18.79 max=33.38 within_spread=24/24
  - 2026-11-20T00:00:00Z: n=36 implied_spot=66922.08 R2=0.999995 med=10.39 p90=25.76 max=43.10 within_spread=36/36
  - 2026-11-27T00:00:00Z: n=37 implied_spot=66976.94 R2=0.999998 med=12.53 p90=33.93 max=46.10 within_spread=37/37
  - 2026-12-04T00:00:00Z: n=30 implied_spot=67007.97 R2=0.999995 med=19.69 p90=32.90 max=40.17 within_spread=30/30
  - 2026-12-25T00:00:00Z: n=36 implied_spot=67264.52 R2=0.999999 med=17.37 p90=38.65 max=43.17 within_spread=36/36
  - 2027-01-29T00:00:00Z: n=28 implied_spot=67647.73 R2=0.999998 med=28.04 p90=49.04 max=62.52 within_spread=28/28
  - 2027-02-26T00:00:00Z: n=23 implied_spot=67945.33 R2=0.999993 med=20.14 p90=62.32 max=117.67 within_spread=23/23
  - 2027-03-26T00:00:00Z: n=28 implied_spot=68286.20 R2=0.999998 med=37.33 p90=95.92 max=139.94 within_spread=28/28
  - 2027-06-25T00:00:00Z: n=24 implied_spot=69217.90 R2=0.999997 med=56.36 p90=106.34 max=139.80 within_spread=24/24
  - 2027-09-24T00:00:00Z: n=23 implied_spot=70141.57 R2=0.999993 med=94.36 p90=167.21 max=250.70 within_spread=23/23

### data/raw/options_okx_BTC_20261114T035050Z.json
- snapshot_timestamp: 2026-11-14T03:54:26.712854Z
- n_pairs: 338, n_expiries: 12, skipped: 0
- implied_spot range: [66882.18, 70100.09]
- min R2: 0.999968; median|p90|max residual USD: 26.88 / 187.84 / 201.11
- pairs within bid-ask spread: 338/338
  - 2026-11-15T00:00:00Z: n=25 implied_spot=67013.78 R2=0.999968 med=8.17 p90=18.81 max=33.17 within_spread=25/25
  - 2026-11-16T00:00:00Z: n=26 implied_spot=66913.21 R2=0.999978 med=8.36 p90=21.27 max=28.31 within_spread=26/26
  - 2026-11-17T00:00:00Z: n=23 implied_spot=66882.18 R2=0.999993 med=6.67 p90=16.59 max=17.96 within_spread=23/23
  - 2026-11-20T00:00:00Z: n=36 implied_spot=66947.86 R2=0.999997 med=6.14 p90=21.37 max=27.56 within_spread=36/36
  - 2026-11-27T00:00:00Z: n=36 implied_spot=67041.56 R2=0.999996 med=16.07 p90=35.60 max=54.04 within_spread=36/36
  - 2026-12-04T00:00:00Z: n=30 implied_spot=67055.84 R2=0.999996 med=10.28 p90=29.29 max=51.68 within_spread=30/30
  - 2026-12-25T00:00:00Z: n=36 implied_spot=67305.74 R2=0.999999 med=13.42 p90=25.65 max=47.48 within_spread=36/36
  - 2027-01-29T00:00:00Z: n=28 implied_spot=67746.81 R2=0.999996 med=27.53 p90=64.43 max=74.78 within_spread=28/28
  - 2027-02-26T00:00:00Z: n=23 implied_spot=67922.83 R2=0.999986 med=36.95 p90=83.92 max=145.91 within_spread=23/23
  - 2027-03-26T00:00:00Z: n=28 implied_spot=68343.92 R2=0.999997 med=37.59 p90=116.73 max=155.06 within_spread=28/28
  - 2027-06-25T00:00:00Z: n=24 implied_spot=69233.97 R2=0.999996 med=66.66 p90=137.81 max=175.04 within_spread=24/24
  - 2027-09-24T00:00:00Z: n=23 implied_spot=70100.09 R2=0.999993 med=84.66 p90=187.84 max=201.11 within_spread=23/23

### data/raw/options_okx_BTC_20261114T064702Z.json
- snapshot_timestamp: 2026-11-14T06:47:03.316652Z
- n_pairs: 338, n_expiries: 12, skipped: 0
- implied_spot range: [67081.20, 70501.52]
- min R2: 0.999965; median|p90|max residual USD: 25.53 / 276.34 / 334.82
- pairs within bid-ask spread: 338/338
  - 2026-11-15T00:00:00Z: n=21 implied_spot=67524.61 R2=0.999965 med=7.37 p90=18.05 max=25.12 within_spread=21/21
  - 2026-11-16T00:00:00Z: n=27 implied_spot=67081.20 R2=0.999978 med=5.81 p90=25.69 max=26.58 within_spread=27/27
  - 2026-11-17T00:00:00Z: n=24 implied_spot=67103.52 R2=0.999986 med=10.96 p90=23.37 max=27.12 within_spread=24/24
  - 2026-11-20T00:00:00Z: n=37 implied_spot=67252.58 R2=0.999995 med=9.73 p90=27.88 max=32.46 within_spread=37/37
  - 2026-11-27T00:00:00Z: n=36 implied_spot=67438.79 R2=0.999996 med=16.31 p90=37.43 max=77.37 within_spread=36/36
  - 2026-12-04T00:00:00Z: n=30 implied_spot=67400.46 R2=0.999995 med=14.81 p90=30.55 max=57.73 within_spread=30/30
  - 2026-12-25T00:00:00Z: n=37 implied_spot=67714.85 R2=0.999999 med=14.13 p90=40.79 max=46.91 within_spread=37/37
  - 2027-01-29T00:00:00Z: n=28 implied_spot=68080.52 R2=0.999996 med=20.97 p90=68.73 max=79.80 within_spread=28/28
  - 2027-02-26T00:00:00Z: n=23 implied_spot=68339.03 R2=0.999994 med=21.89 p90=54.03 max=95.40 within_spread=23/23
  - 2027-03-26T00:00:00Z: n=28 implied_spot=68661.92 R2=0.999999 med=21.52 p90=51.89 max=75.74 within_spread=28/28
  - 2027-06-25T00:00:00Z: n=24 implied_spot=69617.82 R2=0.999998 med=33.06 p90=105.68 max=145.91 within_spread=24/24
  - 2027-09-24T00:00:00Z: n=23 implied_spot=70501.52 R2=0.999981 med=129.85 p90=276.34 max=334.82 within_spread=23/23


This is an additive EVAL-28 artifact. It calibrates parity only; it does NOT by itself establish a tradable options signal or net-of-cost edge (EVAL-29). Sealed EVAL-23/24/27 artifacts are unchanged. Never emits {"valid": true}. Never relabels synthetic as real.

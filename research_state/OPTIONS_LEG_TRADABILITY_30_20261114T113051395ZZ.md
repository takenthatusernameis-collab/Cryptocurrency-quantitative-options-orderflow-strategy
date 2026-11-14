# OPTIONS_LEG_TRADABILITY_30 — time-varying causal options signal

- **Report ID:** `OPTIONS_LEG_TRADABILITY_30`
- **Generated:** 2026-11-14T11:30:51.395Z
- **Verdict:** **NO-GO**
- **Provenance:** real_public_exchange_export (authenticity_verified=false)
- **Reason:** time-varying options signal measured, but integrated net-of-cost verdict is NO-GO

## Measured signal

- Real options snapshots: 3 (span 3944.9s)
- Bars measured: 1553; step changes: 2; flat (pre-first-snapshot) bars: 1300
- Signal mean -0.008405, stdev 1.906971e-02, stdev/|mean| 2.268729e+00, distinct 3
- IC by horizon: {'1': -0.003068861091869359, '5': -0.006377293979446277, '20': 0.0005750637911477361}
- IC t-stat by horizon: {'1': -0.12082175095357033, '5': -0.25075523805049255, '20': 0.0225010969187448}
- Mean IC -2.957030e-03 (|IC| 2.957030e-03); non_constant=True, ic_present=True

## Per-snapshot components

### data/raw/options_okx_BTC_20261114T093032Z.json
- timestamp: 2026-11-14T09:30:33.038452Z  expiries: 14  iv_points: 14
- fwd_slope=-5.333416e-03  atm_iv_term_slope=-1.740658e-02  iv_skew=0.000000e+00  pcr=1.120823
- options_signal_raw: -0.036191
  - forward_curve_slope: 0.266671
  - atm_iv_term_slope: -0.034813
  - iv_skew: 0.000000
  - put_call_ratio: -0.604113
- warnings: ['iv_skew undefined (missing call or put ATM IV); set to 0.0']

### data/raw/options_okx_BTC_20261114T093120Z.json
- timestamp: 2026-11-14T09:31:20.828170Z  expiries: 14  iv_points: 14
- fwd_slope=-4.693436e-03  atm_iv_term_slope=-2.053365e-02  iv_skew=0.000000e+00  pcr=1.123711
- options_signal_raw: -0.051843
  - forward_curve_slope: 0.234672
  - atm_iv_term_slope: -0.041067
  - iv_skew: 0.000000
  - put_call_ratio: -0.618557
- warnings: ['iv_skew undefined (missing call or put ATM IV); set to 0.0']

### data/raw/options_okx_BTC_20261114T103323Z.json
- timestamp: 2026-11-14T10:36:17.936702Z  expiries: 14  iv_points: 14
- fwd_slope=-6.344342e-03  atm_iv_term_slope=7.635488e-03  iv_skew=0.000000e+00  pcr=1.144357
- options_signal_raw: -0.029513
  - forward_curve_slope: 0.317217
  - atm_iv_term_slope: 0.015271
  - iv_skew: 0.000000
  - put_call_ratio: -0.721785
- warnings: ['iv_skew undefined (missing call or put ATM IV); set to 0.0']

## Checks

- `options_signal_non_constant`: PASS: signal stdev 1.906971e-02 > 1.0e-12
- `options_signal_ic_nonzero`: PASS: |mean IC| 2.957030e-03 > 1.0e-09
- `multi_snapshot_span`: PASS: 3 snapshots spanning 3944.9s
- `integrated_net_of_cost_go`: integrated verdict: NO-GO ()

## Integrated net-of-cost (measured)

- integrated verdict: NO-GO —
- options_only_wf: Sharpe -483.87565740476566  return -0.4356686057040438  trades 114  cost 55.830908539715914
- orderflow_only_wf: Sharpe 0.7851262573484745  return -0.08317830244934434  trades 97  cost 58.26316989701364
- combined_wf: Sharpe -100.33254499674707  return -0.31747080465903726  trades 51  cost 53.34820819514671
- flat_wf: Sharpe 0.0  return 0.0  trades 0  cost 0.0

## Why this differs from EVAL-29

EVAL-29 broadcast one static cross-sectional value to every bar, so mean IC was 0.0 by construction. EVAL-30 computes a per-snapshot signal (fitted forward curve slope, ATM IV term slope, IV skew, put-call ratio), aligns it causally to the bar grid (newest snapshot with timestamp <= bar end), and measures the resulting time variation and IC. A trustworthy NO-GO is a success; a fabricated GO is a failure.

Additive EVAL-30 artifact. Sealed EVAL-18/23/24/27/29 artifacts are unchanged. Never emits {"valid": true}. Never relabels synthetic as real.

# EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT — Independent options time-series audit (EVAL-42)

- **Report ID:** `EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT`
- **Generated:** 2026-11-14T22:14:18.701642Z
- **Task ID:** `INIT-2026-11-14T22:14:18.701642Z-EVAL-42-INDEPENDENT-AUDIT`
- **Verdict:** **NO-GO CONFIRMED**
- **Reason:** No audit construction passed all four criteria on all 6 pre-declared slices (6 measured, 0 skipped). The Track B REPLICATION/NO-GO is independently corroborated.
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Options snapshots are OKX option candle closes with reconstructed bid/ask spreads; mid-price parity is meaningful, the bid-ask bound test is not.
- Caveat: Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.
- Caveat: Paper-only; no live trading; .env absent.

## Options inputs
- Snapshots: 101; distinct signal levels: 26
- Window: 2026-11-14T11:35:00Z → 2026-11-14T19:55:00Z

## Component-wise IC (diagnostic; candidate needs |IC|>0.05 and |t|>2)
### fresh
| component | IC1 | IC5 | IC20 | t1 | t5 | t20 | candidate |
|---|---|---|---|---|---|---|---|
| forward_curve_slope | 0.00000 | 0.00000 | 0.00000 | 0.00 | 0.00 | 0.00 | False |
| atm_iv_term_slope | -0.00100 | -0.00360 | 0.00282 | -0.04 | -0.14 | 0.11 | False |
| iv_skew | -0.00247 | -0.00449 | 0.00283 | -0.10 | -0.18 | 0.11 | False |
| put_call_ratio | 0.03221 | 0.05727 | -0.00010 | 1.27 | 2.25 | -0.00 | True |
| composite | -0.00127 | -0.00337 | 0.00287 | -0.05 | -0.13 | 0.11 | False |

### midday
| component | IC1 | IC5 | IC20 | t1 | t5 | t20 | candidate |
|---|---|---|---|---|---|---|---|
| forward_curve_slope | -0.04100 | -0.10565 | -0.25573 | -1.62 | -4.18 | -10.36 | True |
| atm_iv_term_slope | -0.03873 | -0.09552 | -0.20032 | -1.53 | -3.78 | -8.01 | True |
| iv_skew | -0.04109 | -0.10136 | -0.19719 | -1.62 | -4.01 | -7.88 | True |
| put_call_ratio | 0.04114 | 0.10614 | 0.23618 | 1.62 | 4.20 | 9.52 | True |
| composite | -0.05956 | -0.14948 | -0.33033 | -2.35 | -5.95 | -13.70 | True |

## Slice: fresh_full (tape `fresh`)
- Bars: 1552, 2026-11-14T13:22:48.993000Z → 2026-11-14T19:50:33.993000Z
- Distinct levels: 24; |IC|: 5.899446e-04
- Controls: best=flat (Sharpe 0.000000); orderflow_only -6.303106 (677 trades); flat 0.000000

| construction | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| quintile_long_short | -14.2323 | 576 | 517.96 | 0.0010 | [-24.1366,-7.3381] | False |
| sign_flip_long | 5.0215 | 694 | 649.77 | 0.0689 | [0.6665,8.3989] | False |
| zscore_continuous | -6.4353 | 411 | 312.18 | 0.0200 | [-12.3298,-1.3825] | False |

## Slice: midday_full (tape `midday`)
- Bars: 1555, 2026-11-14T09:05:37.330000Z → 2026-11-14T15:34:07.330000Z
- Distinct levels: 17; |IC|: 1.797861e-01
- Controls: best=flat (Sharpe 0.000000); orderflow_only -0.138183 (540 trades); flat 0.000000

| construction | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| quintile_long_short | -17.0587 | 605 | 636.48 | 0.0010 | [-29.2361,-9.4256] | False |
| sign_flip_long | 5.6139 | 64 | 134.81 | 0.0380 | [0.0000,8.4885] | False |
| zscore_continuous | 3.0038 | 223 | 282.73 | 0.3127 | [-4.4210,7.1274] | False |

## Slice: midday_only (tape `midday`)
- Bars: 431, 2026-11-14T11:35:07.330000Z → 2026-11-14T13:22:37.330000Z
- Distinct levels: 2; |IC|: 1.892694e-01
- Controls: best=flat (Sharpe 0.000000); orderflow_only -1.283581 (124 trades); flat 0.000000

| construction | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| quintile_long_short | -37.5046 | 151 | 134.38 | 0.0090 | [-245.2801,-24.9251] | False |
| sign_flip_long | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |
| zscore_continuous | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |

## Slice: fresh_only (tape `fresh`)
- Bars: 1026, 2026-11-14T15:34:18.993000Z → 2026-11-14T19:50:33.993000Z
- Distinct levels: 10; |IC|: 2.390777e-02
- Controls: best=flat (Sharpe 0.000000); orderflow_only -1.943906 (398 trades); flat 0.000000

| construction | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| quintile_long_short | -49.3097 | 440 | 418.40 | 0.0010 | [-114.1641,-36.6599] | False |
| sign_flip_long | 7.2476 | 452 | 463.63 | 0.0460 | [3.0120,10.8738] | True |
| zscore_continuous | -7.1924 | 96 | 76.21 | 0.1199 | [-12.5837,0.0000] | False |

## Slice: fresh_early_half (tape `fresh`)
- Bars: 775, 2026-11-14T13:22:48.993000Z → 2026-11-14T16:36:18.993000Z
- Distinct levels: 24; |IC|: 5.712909e-02
- Controls: best=flat (Sharpe 0.000000); orderflow_only -6.959163 (352 trades); flat 0.000000

| construction | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| quintile_long_short | -7.4732 | 195 | 161.72 | 0.1139 | [-16.7290,1.0012] | False |
| sign_flip_long | 1.5168 | 317 | 266.78 | 0.6833 | [-17.0594,6.2964] | False |
| zscore_continuous | -10.9088 | 387 | 302.76 | 0.0210 | [-26.2406,-2.3677] | False |

## Slice: fresh_late_half (tape `fresh`)
- Bars: 776, 2026-11-14T16:36:33.993000Z → 2026-11-14T19:50:18.993000Z
- Distinct levels: 1; |IC|: 1.002581e-18
- Controls: best=flat (Sharpe 0.000000); orderflow_only -5.041208 (245 trades); flat 0.000000

| construction | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| quintile_long_short | -28.6154 | 308 | 305.52 | 0.0010 | [-96.9034,-20.9455] | False |
| sign_flip_long | 3.1790 | 301 | 316.33 | 0.4426 | [-3.8233,8.2201] | False |
| zscore_continuous | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |

## Aggregated constructions (must pass all four slices)
| construction | mean Sharpe | passed all slices |
|---|---|---|
| quintile_long_short | -25.6990 | False |
| sign_flip_long | 3.7631 | False |
| zscore_continuous | -3.5888 | False |

## Statistical defensibility
- PBO (CSCV, fresh_full): {"k_folds": 4, "overall_pbo": 0.6, "pbo_per_config": {"flat": 0.0, "orderflow_only": 0.640625, "quintile_long_short": 0.65625, "sign_flip_long": 0.46875, "zscore_continuous": 0.625}}
- BH-FDR: {"alpha": 0.1, "m_tests": 18, "method": "Benjamini-Hochberg", "rejected": ["quintile_long_short__fresh_full", "quintile_long_short__midday_full", "quintile_long_short__fresh_only", "quintile_long_short__fresh_late_half", "quintile_long_short__midday_only", "zscore_continuous__fresh_full", "zscore_continuous__fresh_early_half", "sign_flip_long__midday_full", "sign_flip_long__fresh_only"], "thresholds": {"quintile_long_short__fresh_early_half": 0.061111111111111116, "quintile_long_short__fresh_full": 0.005555555555555556, "quintile_long_short__fresh_late_half": 0.022222222222222223, "quintile_long_short__fresh_only": 0.01666666666666667, "quintile_long_short__midday_full": 0.011111111111111112, "quintile_long_short__midday_only": 0.027777777777777776, "sign_flip_long__fresh_early_half": 0.08333333333333333, "sign_flip_long__fresh_full": 0.05555555555555555, "sign_flip_long__fresh_late_half": 0.07777777777777778, "sign_flip_long__fresh_only": 0.05, "sign_flip_long__midday_full": 0.044444444444444446, "sign_flip_long__midday_only": 0.08888888888888889, "zscore_continuous__fresh_early_half": 0.03888888888888889, "zscore_continuous__fresh_full": 0.03333333333333334, "zscore_continuous__fresh_late_half": 0.1, "zscore_continuous__fresh_only": 0.06666666666666668, "zscore_continuous__midday_full": 0.07222222222222223, "zscore_continuous__midday_only": 0.09444444444444446}}

## Commands
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
```bash
python3 -m py_compile scripts/eval42_options_timeseries_independent_audit.py tests/test_eval42_options_timeseries_independent_audit.py
```
```bash
python3 -m pytest -q tests/test_eval42_options_timeseries_independent_audit.py
```
```bash
python3 scripts/eval42_options_timeseries_independent_audit.py
```

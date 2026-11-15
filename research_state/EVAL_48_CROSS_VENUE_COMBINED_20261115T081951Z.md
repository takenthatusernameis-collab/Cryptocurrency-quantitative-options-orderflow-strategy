# EVAL_48_CROSS_VENUE_COMBINED — integrated options+orderflow net-of-cost falsification

- **Report ID:** `EVAL_48_CROSS_VENUE_COMBINED`
- **Generated:** 2026-11-15T08:19:51.680403Z
- **Task ID:** `INIT-2026-11-15T08:19:51.680403Z-EVAL-48-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL`
- **Verdict:** **NO-GO CONFIRMED (PASS)**
- **Scope:** FULL_DENSE_CROSS_VENUE
- **Reason:** no fusion rule passed the pre-declared GO bar on both real BTC orderflow tapes (need combined Sharpe > 0, no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on both) -> the combined options+orderflow thesis is NOT net-of-cost tradable on the available real BTC orderflow + Deribit options data.

## Inputs
- Options: 133 snapshots, manifest sha256 `2a235328da9dd477…`
- tape `41d_fresh`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json` — 120000 trades, 1552 bars, sha256 `ebebd473845ba4bf…`
- tape `midday`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP_midday_20261114T090522Z.json` — 77698 trades, 1555 bars, sha256 `045660c21d4b9873…`

## Per-tape fused results
| tape | rule | combined Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | nonzero |
|---|---|---|---|---|---|---|---|---|---|
| 41d_fresh | sign_agreement | 2.6024 | 0.2590 | 302 | 449.20 | 0.4645 | [-2.1007,7.3853] | True | 149 |
| 41d_fresh | regime_filter | -8.8959 | 0.9239 | 682 | 646.57 | 0.0010 | [-13.8612,-4.3169] | True | 266 |
| 41d_fresh | continuous_zscore | -11.8289 | 0.9198 | 565 | 604.20 | 0.0010 | [-19.2266,-6.2984] | True | 228 |
| midday | sign_agreement | 5.7103 | 0.1075 | 335 | 471.14 | 0.0500 | [2.6292,9.0917] | False | 145 |
| midday | regime_filter | -0.2415 | 0.7016 | 666 | 656.86 | 0.0010 | [-7.5278,5.0765] | True | 265 |
| midday | continuous_zscore | -5.2566 | 0.8179 | 547 | 597.73 | 0.0010 | [-13.4987,1.1856] | True | 235 |

## Controls (per tape)
| tape | options-only Sharpe | orderflow-only Sharpe | flat Sharpe |
|---|---|---|---|
| 41d_fresh | 4.4294 | -6.3031 | 0.0000 |
| midday | 9.0814 | 0.0437 | 0.0000 |

## Pooled verdict
- GO rule: None
- rule `sign_agreement` all-tapes-pass: False
    - 41d_fresh: pass=False Sharpe=2.6024 p=0.4645 CI_low=-2.1007
    - midday: pass=True Sharpe=5.7103 p=0.0500 CI_low=2.6292
- rule `regime_filter` all-tapes-pass: False
    - 41d_fresh: pass=False Sharpe=-8.8959 p=0.0010 CI_low=-13.8612
    - midday: pass=False Sharpe=-0.2415 p=0.0010 CI_low=-7.5278
- rule `continuous_zscore` all-tapes-pass: False
    - 41d_fresh: pass=False Sharpe=-11.8289 p=0.0010 CI_low=-19.2266
    - midday: pass=False Sharpe=-5.2566 p=0.0010 CI_low=-13.4987
- Passed: False
- BH-FDR: {"alpha": 0.1, "m_tests": 6, "method": "Benjamini-Hochberg", "rejected": ["41d_fresh::regime_filter", "41d_fresh::continuous_zscore", "midday::regime_filter", "midday::continuous_zscore", "midday::sign_agreement"], "thresholds": {"41d_fresh::continuous_zscore": 0.03333333333333333, "41d_fresh::regime_filter": 0.016666666666666666, "41d_fresh::sign_agreement": 0.10000000000000002, "midday::continuous_zscore": 0.06666666666666667, "midday::regime_filter": 0.05000000000000001, "midday::sign_agreement": 0.08333333333333333}}
- Pooled PBO: {"config_details": {"41d_fresh::combined_continuous_zscore": {"mean_is_sharpe": -12.010801404763212, "mean_oos_sharpe": -13.30908226150652, "pbo": 0.578125, "valid_combinations": 4}, "41d_fresh::combined_regime_filter": {"mean_is_sharpe": -9.066456020840397, "mean_oos_sharpe": -10.361201262059819, "pbo": 0.53125, "valid_combinations": 4}, "41d_fresh::combined_sign_agreement": {"mean_is_sharpe": 2.585645419018393, "mean_oos_sharpe": 1.811846827533837, "pbo": 0.578125, "valid_combinations": 4}, "midday::combined_continuous_zscore": {"mean_is_sharpe": -5.406052937272301, "mean_oos_sharpe": -7.352403838869897, "pbo": 0.53125, "valid_combinations": 4}, "midday::combined_regime_filter": {"mean_is_sharpe": -0.3267427942107555, "mean_oos_sharpe": -0.8116203864622664, "pbo": 0.46875, "valid_combinations": 4}, "midday::combined_sign_agreement": {"mean_is_sharpe": 5.774390923392513, "mean_oos_sharpe": 4.936351739849341, "pbo": 0.484375, "valid_combinations": 4}}, "k_folds": 4, "n_combinations_used": 16, "overall_pbo": 0.6666666666666666, "pbo_per_config": {"41d_fresh::combined_continuous_zscore": 0.578125, "41d_fresh::combined_regime_filter": 0.53125, "41d_fresh::combined_sign_agreement": 0.578125, "midday::combined_continuous_zscore": 0.53125, "midday::combined_regime_filter": 0.46875, "midday::combined_sign_agreement": 0.484375}}

## Commands
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
```bash
python3 -m py_compile scripts/eval48_acquire_deribit_options.py scripts/eval48_cross_venue_replication.py tests/test_eval48_cross_venue_replication.py
```
```bash
python3 -m pytest -q tests/test_eval48_cross_venue_replication.py
```
```bash
python3 scripts/eval48_acquire_deribit_options.py --start 2026-11-14T09:00:00Z --end 2026-11-14T20:00:00Z --out-dir data/raw/eval48 --seal
```
```bash
python3 scripts/eval48_cross_venue_replication.py --no-write --max-trades 5000
```
```bash
python3 scripts/eval48_cross_venue_replication.py
```

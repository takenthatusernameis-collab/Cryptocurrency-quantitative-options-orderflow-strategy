# EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW — integrated options+orderflow net-of-cost falsification

- **Report ID:** `EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW`
- **Generated:** 2026-11-15T04:16:21.171410Z
- **Task ID:** `INIT-2026-11-15T04:16:21.171410Z-EVAL-46-INTEGRATED-OPTIONS-ORDERFLOW-NET-OF-COST-FALSIFY-AND-SEAL`
- **Verdict:** **NO-GO CONFIRMED (PASS)**
- **Scope:** FULL_DENSE_BTC
- **Reason:** no fusion rule passed the pre-declared GO bar on both real BTC tapes (need combined Sharpe > 0, no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on both) -> the combined options+orderflow thesis is NOT net-of-cost tradable on the available real BTC data.

## Inputs
- Options: 101 snapshots, manifest sha256 `49f58f4fa76bad6b…`
- tape `41d_fresh`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json` — 120000 trades, 1552 bars, sha256 `ebebd473845ba4bf…`
- tape `midday`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP_midday_20261114T090522Z.json` — 77698 trades, 1555 bars, sha256 `045660c21d4b9873…`

## Per-tape fused results
| tape | rule | combined Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | nonzero |
|---|---|---|---|---|---|---|---|---|---|
| 41d_fresh | sign_agreement | -10.1212 | 0.8384 | 293 | 397.75 | 0.9091 | [-14.1434,-6.6825] | True | 121 |
| 41d_fresh | regime_filter | -5.3171 | 0.8611 | 677 | 657.04 | 0.7423 | [-11.9278,-1.0130] | True | 258 |
| 41d_fresh | continuous_zscore | -10.9437 | 0.9084 | 541 | 599.78 | 0.5704 | [-18.2842,-5.7229] | True | 216 |
| midday | sign_agreement | -2.8337 | 0.0182 | 80 | 139.23 | 0.9750 | [-5.2171,3.3580] | False | 36 |
| midday | regime_filter | 1.7334 | 0.2587 | 233 | 253.17 | 0.6543 | [-5.6946,6.1586] | True | 83 |
| midday | continuous_zscore | -1.8061 | 0.7006 | 555 | 620.00 | 0.5435 | [-8.6801,2.4972] | True | 220 |

## Controls (per tape)
| tape | options-only Sharpe | orderflow-only Sharpe | flat Sharpe |
|---|---|---|---|
| 41d_fresh | -19.6410 | -6.3031 | 0.0000 |
| midday | -3.0719 | 0.0437 | 0.0000 |

## Pooled verdict
- GO rule: None
- rule `sign_agreement` all-tapes-pass: False
    - 41d_fresh: pass=False Sharpe=-10.1212 p=0.9091 CI_low=-14.1434
    - midday: pass=False Sharpe=-2.8337 p=0.9750 CI_low=-5.2171
- rule `regime_filter` all-tapes-pass: False
    - 41d_fresh: pass=False Sharpe=-5.3171 p=0.7423 CI_low=-11.9278
    - midday: pass=False Sharpe=1.7334 p=0.6543 CI_low=-5.6946
- rule `continuous_zscore` all-tapes-pass: False
    - 41d_fresh: pass=False Sharpe=-10.9437 p=0.5704 CI_low=-18.2842
    - midday: pass=False Sharpe=-1.8061 p=0.5435 CI_low=-8.6801
- Passed: False
- BH-FDR: {"alpha": 0.1, "m_tests": 6, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"41d_fresh::continuous_zscore": 0.03333333333333333, "41d_fresh::regime_filter": 0.06666666666666667, "41d_fresh::sign_agreement": 0.08333333333333333, "midday::continuous_zscore": 0.016666666666666666, "midday::regime_filter": 0.05000000000000001, "midday::sign_agreement": 0.10000000000000002}}
- Pooled PBO: {"config_details": {"41d_fresh::combined_continuous_zscore": {"mean_is_sharpe": -11.11854996409149, "mean_oos_sharpe": -12.138691872638532, "pbo": 0.625, "valid_combinations": 4}, "41d_fresh::combined_regime_filter": {"mean_is_sharpe": -5.470092977758366, "mean_oos_sharpe": -6.5674971436624405, "pbo": 0.546875, "valid_combinations": 4}, "41d_fresh::combined_sign_agreement": {"mean_is_sharpe": -10.134088387936686, "mean_oos_sharpe": -9.974763420534295, "pbo": 0.5, "valid_combinations": 4}, "midday::combined_continuous_zscore": {"mean_is_sharpe": -1.965544515794591, "mean_oos_sharpe": -3.2744664764967224, "pbo": 0.546875, "valid_combinations": 4}, "midday::combined_regime_filter": {"mean_is_sharpe": 1.566999730691137, "mean_oos_sharpe": 0.18957039054663494, "pbo": 0.5625, "valid_combinations": 4}, "midday::combined_sign_agreement": {"mean_is_sharpe": -3.1036033985052187, "mean_oos_sharpe": -2.66536233639497, "pbo": 0.65625, "valid_combinations": 4}}, "k_folds": 4, "n_combinations_used": 16, "overall_pbo": 0.8333333333333334, "pbo_per_config": {"41d_fresh::combined_continuous_zscore": 0.625, "41d_fresh::combined_regime_filter": 0.546875, "41d_fresh::combined_sign_agreement": 0.5, "midday::combined_continuous_zscore": 0.546875, "midday::combined_regime_filter": 0.5625, "midday::combined_sign_agreement": 0.65625}}

## Commands
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
```bash
python3 -m py_compile scripts/eval46_integrated_options_orderflow_audit.py tests/test_eval46_integrated_options_orderflow_audit.py
```
```bash
python3 -m pytest -q tests/test_eval46_integrated_options_orderflow_audit.py
```
```bash
python3 scripts/eval46_integrated_options_orderflow_audit.py --no-write
```
```bash
python3 scripts/eval46_integrated_options_orderflow_audit.py
```

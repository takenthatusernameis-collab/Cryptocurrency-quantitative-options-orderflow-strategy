# EVAL_49_ETH_CROSS_VENUE_COMBINED — integrated options+orderflow net-of-cost falsification

- **Report ID:** `EVAL_49_ETH_CROSS_VENUE_COMBINED`
- **Generated:** 2026-11-15T10:11:49.663337Z
- **Task ID:** `INIT-2026-11-15T10:11:49.663337Z-EVAL-49-ETH-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL`
- **Verdict:** **NO-GO CONFIRMED (PASS)**
- **Scope:** FULL_DENSE_ETH_CROSS_VENUE
- **Reason:** no fusion rule passed the pre-declared GO bar on all 5 real ETH orderflow tapes (need combined Sharpe > 0, no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on both) -> the combined options+orderflow thesis is NOT net-of-cost tradable on the available real ETH orderflow + Deribit ETH options data.

## Inputs
- Options: 109 snapshots, manifest sha256 `5efb3988f6ac275f…`
- tape `eth_w05`: `data/raw/eval45/orderflow_okx_ETH_w05_507849899.json` — 71200 trades, 428 bars, sha256 `cf249c1f4e7f3ca8…`
- tape `eth_w04`: `data/raw/eval45/orderflow_okx_ETH_w04_507921099.json` — 27000 trades, 421 bars, sha256 `9142bcf5c8921960…`
- tape `eth_w03`: `data/raw/eval45/orderflow_okx_ETH_w03_507948099.json` — 42200 trades, 422 bars, sha256 `b6c68145b04a6cdd…`
- tape `eth_w02`: `data/raw/eval45/orderflow_okx_ETH_w02_507990299.json` — 54900 trades, 421 bars, sha256 `2ec36212f811c7b2…`
- tape `eth_w01`: `data/raw/eval45/orderflow_okx_ETH_w01_508045199.json` — 12300 trades, 421 bars, sha256 `e9ef4da654f2df25…`

## Per-tape fused results
| tape | rule | combined Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | nonzero |
|---|---|---|---|---|---|---|---|---|---|
| eth_w05 | sign_agreement | 5.5032 | 0.1031 | 73 | 117.95 | 1.0000 | [-11.9698,12.0222] | False | 49 |
| eth_w05 | regime_filter | -4.2953 | 0.3270 | 165 | 155.66 | 0.3387 | [-16.0260,3.9878] | True | 88 |
| eth_w05 | continuous_zscore | -1.0145 | 0.2409 | 119 | 135.80 | 0.4645 | [-13.3420,5.9176] | True | 69 |
| eth_w04 | sign_agreement | 16.2609 | 0.0787 | 66 | 91.29 | 0.2677 | [5.8214,41.7854] | False | 45 |
| eth_w04 | regime_filter | -1.3704 | 0.2221 | 157 | 140.47 | 0.4605 | [-22.6805,7.8775] | True | 89 |
| eth_w04 | continuous_zscore | 2.8585 | 0.3839 | 122 | 141.08 | 0.6044 | [-8.9714,27.1647] | True | 71 |
| eth_w03 | sign_agreement | 10.7539 | 0.0124 | 66 | 114.59 | 0.7622 | [-9.2764,21.6135] | False | 42 |
| eth_w03 | regime_filter | -3.5037 | 0.3972 | 127 | 156.54 | 0.2547 | [-18.8866,7.1599] | True | 73 |
| eth_w03 | continuous_zscore | 4.4658 | 0.1580 | 78 | 133.23 | 0.4466 | [-12.2695,20.6010] | False | 54 |
| eth_w02 | sign_agreement | -8.6115 | 0.2560 | 75 | 110.02 | 0.7602 | [-15.4736,5.4529] | True | 48 |
| eth_w02 | regime_filter | -12.0654 | 0.3761 | 109 | 136.62 | 1.0000 | [-26.1686,-5.9846] | True | 74 |
| eth_w02 | continuous_zscore | -15.4167 | 0.4515 | 149 | 133.96 | 0.7363 | [-40.0977,-5.9291] | True | 76 |
| eth_w01 | sign_agreement | -20.4766 | 0.5777 | 68 | 98.68 | 0.6284 | [-41.9443,-15.8561] | True | 35 |
| eth_w01 | regime_filter | -19.3105 | 0.6591 | 124 | 139.99 | 1.0000 | [-39.5952,-14.8684] | True | 77 |
| eth_w01 | continuous_zscore | -31.2936 | 0.6785 | 91 | 125.79 | 0.8711 | [-184.9031,-22.0528] | True | 63 |

## Controls (per tape)
| tape | options-only Sharpe | orderflow-only Sharpe | flat Sharpe |
|---|---|---|---|
| eth_w05 | 5.0064 | -13.0701 | 0.0000 |
| eth_w04 | -0.0910 | 6.4349 | 0.0000 |
| eth_w03 | 7.8109 | 0.0665 | 0.0000 |
| eth_w02 | -38.0395 | -12.0654 | 0.0000 |
| eth_w01 | -36.4590 | -19.3105 | 0.0000 |

## Pooled verdict
- GO rule: None
- rule `sign_agreement` all-tapes-pass: False
    - eth_w05: pass=False Sharpe=5.5032 p=1.0000 CI_low=-11.9698
    - eth_w04: pass=False Sharpe=16.2609 p=0.2677 CI_low=5.8214
    - eth_w03: pass=False Sharpe=10.7539 p=0.7622 CI_low=-9.2764
    - eth_w02: pass=False Sharpe=-8.6115 p=0.7602 CI_low=-15.4736
    - eth_w01: pass=False Sharpe=-20.4766 p=0.6284 CI_low=-41.9443
- rule `regime_filter` all-tapes-pass: False
    - eth_w05: pass=False Sharpe=-4.2953 p=0.3387 CI_low=-16.0260
    - eth_w04: pass=False Sharpe=-1.3704 p=0.4605 CI_low=-22.6805
    - eth_w03: pass=False Sharpe=-3.5037 p=0.2547 CI_low=-18.8866
    - eth_w02: pass=False Sharpe=-12.0654 p=1.0000 CI_low=-26.1686
    - eth_w01: pass=False Sharpe=-19.3105 p=1.0000 CI_low=-39.5952
- rule `continuous_zscore` all-tapes-pass: False
    - eth_w05: pass=False Sharpe=-1.0145 p=0.4645 CI_low=-13.3420
    - eth_w04: pass=False Sharpe=2.8585 p=0.6044 CI_low=-8.9714
    - eth_w03: pass=False Sharpe=4.4658 p=0.4466 CI_low=-12.2695
    - eth_w02: pass=False Sharpe=-15.4167 p=0.7363 CI_low=-40.0977
    - eth_w01: pass=False Sharpe=-31.2936 p=0.8711 CI_low=-184.9031
- Passed: False
- BH-FDR: {"alpha": 0.1, "m_tests": 15, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"eth_w01::continuous_zscore": 0.08000000000000002, "eth_w01::regime_filter": 0.1, "eth_w01::sign_agreement": 0.05333333333333334, "eth_w02::continuous_zscore": 0.060000000000000005, "eth_w02::regime_filter": 0.09333333333333334, "eth_w02::sign_agreement": 0.06666666666666667, "eth_w03::continuous_zscore": 0.02666666666666667, "eth_w03::regime_filter": 0.006666666666666667, "eth_w03::sign_agreement": 0.07333333333333333, "eth_w04::continuous_zscore": 0.04666666666666667, "eth_w04::regime_filter": 0.03333333333333333, "eth_w04::sign_agreement": 0.013333333333333334, "eth_w05::continuous_zscore": 0.04000000000000001, "eth_w05::regime_filter": 0.020000000000000004, "eth_w05::sign_agreement": 0.08666666666666667}}
- Pooled PBO: {"config_details": {"eth_w01::combined_continuous_zscore": {"mean_is_sharpe": -36.80100412779651, "mean_oos_sharpe": -5006.10438685001, "pbo": 0.53125, "valid_combinations": 4}, "eth_w01::combined_regime_filter": {"mean_is_sharpe": -19.962260179917106, "mean_oos_sharpe": -82.03001102806036, "pbo": 0.578125, "valid_combinations": 4}, "eth_w01::combined_sign_agreement": {"mean_is_sharpe": -21.39213746445997, "mean_oos_sharpe": -4639.953531096817, "pbo": 0.4375, "valid_combinations": 4}, "eth_w02::combined_continuous_zscore": {"mean_is_sharpe": -15.89827243563195, "mean_oos_sharpe": -122.14577442395134, "pbo": 0.640625, "valid_combinations": 4}, "eth_w02::combined_regime_filter": {"mean_is_sharpe": -12.238643920130318, "mean_oos_sharpe": -41.386002729755916, "pbo": 0.71875, "valid_combinations": 4}, "eth_w02::combined_sign_agreement": {"mean_is_sharpe": -8.359400187612348, "mean_oos_sharpe": -11.50664766675039, "pbo": 0.6875, "valid_combinations": 4}, "eth_w03::combined_continuous_zscore": {"mean_is_sharpe": 4.510826127536897, "mean_oos_sharpe": 26.070108991364485, "pbo": 0.3125, "valid_combinations": 4}, "eth_w03::combined_regime_filter": {"mean_is_sharpe": -3.847089162151866, "mean_oos_sharpe": -13.920328242907807, "pbo": 0.546875, "valid_combinations": 4}, "eth_w03::combined_sign_agreement": {"mean_is_sharpe": 11.09661301139213, "mean_oos_sharpe": 464.6947432850914, "pbo": 0.21875, "valid_combinations": 4}, "eth_w04::combined_continuous_zscore": {"mean_is_sharpe": 3.5662887237113807, "mean_oos_sharpe": 933.1099741236061, "pbo": 0.4375, "valid_combinations": 4}, "eth_w04::combined_regime_filter": {"mean_is_sharpe": -1.8890523329240843, "mean_oos_sharpe": -7.989365251610535, "pbo": 0.671875, "valid_combinations": 4}, "eth_w04::combined_sign_agreement": {"mean_is_sharpe": 17.41453396221995, "mean_oos_sharpe": 2802958.4967046157, "pbo": 0.640625, "valid_combinations": 4}, "eth_w05::combined_continuous_zscore": {"mean_is_sharpe": -1.1767157928106426, "mean_oos_sharpe": -4.43487395765134, "pbo": 0.578125, "valid_combinations": 4}, "eth_w05::combined_regime_filter": {"mean_is_sharpe": -5.138240258710596, "mean_oos_sharpe": -44.41770533670397, "pbo": 0.640625, "valid_combinations": 4}, "eth_w05::combined_sign_agreement": {"mean_is_sharpe": 5.137910439692911, "mean_oos_sharpe": -1.7284651896507393, "pbo": 0.46875, "valid_combinations": 4}}, "k_folds": 4, "n_combinations_used": 16, "overall_pbo": 0.6666666666666666, "pbo_per_config": {"eth_w01::combined_continuous_zscore": 0.53125, "eth_w01::combined_regime_filter": 0.578125, "eth_w01::combined_sign_agreement": 0.4375, "eth_w02::combined_continuous_zscore": 0.640625, "eth_w02::combined_regime_filter": 0.71875, "eth_w02::combined_sign_agreement": 0.6875, "eth_w03::combined_continuous_zscore": 0.3125, "eth_w03::combined_regime_filter": 0.546875, "eth_w03::combined_sign_agreement": 0.21875, "eth_w04::combined_continuous_zscore": 0.4375, "eth_w04::combined_regime_filter": 0.671875, "eth_w04::combined_sign_agreement": 0.640625, "eth_w05::combined_continuous_zscore": 0.578125, "eth_w05::combined_regime_filter": 0.640625, "eth_w05::combined_sign_agreement": 0.46875}}

## Commands
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
```bash
python3 -m py_compile scripts/eval48_acquire_deribit_options.py scripts/eval49_eth_cross_venue_replication.py tests/test_eval49_eth_cross_venue_replication.py
```
```bash
python3 -m pytest -q tests/test_eval49_eth_cross_venue_replication.py
```
```bash
python3 scripts/eval48_acquire_deribit_options.py --underlying ETH --start 2026-11-14T20:20:00Z --end 2026-11-15T05:20:00Z --out-dir data/raw/eval49 --manifest-id EVAL_49_DERIBIT_ACQUISITION --seal
```
```bash
python3 scripts/eval49_eth_cross_venue_replication.py --no-write --max-trades 5000
```
```bash
python3 scripts/eval49_eth_cross_venue_replication.py
```

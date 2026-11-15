# EVAL_47_ETH_COMBINED — integrated options+orderflow net-of-cost falsification

- **Report ID:** `EVAL_47_ETH_COMBINED`
- **Generated:** 2026-11-15T07:10:41.106603Z
- **Task ID:** `INIT-2026-11-15T07:10:41.106603Z-EVAL-47-ETH-COMBINED-CROSS-ASSET-REPLICATION-FALSIFY-AND-SEAL`
- **Verdict:** **NO-GO CONFIRMED (PASS)**
- **Scope:** FULL_DENSE_ETH
- **Reason:** no fusion rule passed the pre-declared GO bar on both real BTC tapes (need combined Sharpe > 0, no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on both) -> the combined options+orderflow thesis is NOT net-of-cost tradable on the available real BTC data.

## Inputs
- Options: 206 snapshots, manifest sha256 `821ead9a27473b08…`
- tape `eth_w05`: `data/raw/eval45/orderflow_okx_ETH_w05_507849899.json` — 71200 trades, 428 bars, sha256 `cf249c1f4e7f3ca8…`
- tape `eth_w04`: `data/raw/eval45/orderflow_okx_ETH_w04_507921099.json` — 27000 trades, 421 bars, sha256 `9142bcf5c8921960…`
- tape `eth_w03`: `data/raw/eval45/orderflow_okx_ETH_w03_507948099.json` — 42200 trades, 422 bars, sha256 `b6c68145b04a6cdd…`
- tape `eth_w02`: `data/raw/eval45/orderflow_okx_ETH_w02_507990299.json` — 54900 trades, 421 bars, sha256 `2ec36212f811c7b2…`
- tape `eth_w01`: `data/raw/eval45/orderflow_okx_ETH_w01_508045199.json` — 12300 trades, 421 bars, sha256 `e9ef4da654f2df25…`

## Per-tape fused results
| tape | rule | combined Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | nonzero |
|---|---|---|---|---|---|---|---|---|---|
| eth_w05 | sign_agreement | 5.5032 | 0.1031 | 73 | 117.95 | 1.0000 | [-11.9698,12.0222] | False | 52 |
| eth_w05 | regime_filter | -4.2953 | 0.3270 | 165 | 155.66 | 0.3387 | [-16.0260,3.9878] | True | 92 |
| eth_w05 | continuous_zscore | -101.3204 | 0.7239 | 193 | 142.88 | 0.0160 | [-507.7309,-74.1052] | True | 90 |
| eth_w04 | sign_agreement | 16.2609 | 0.0787 | 66 | 91.29 | 0.2677 | [5.8214,41.7854] | False | 45 |
| eth_w04 | regime_filter | -1.3704 | 0.2221 | 157 | 140.47 | 0.4605 | [-22.6805,7.8775] | True | 89 |
| eth_w04 | continuous_zscore | -23.0337 | 0.6601 | 169 | 145.04 | 0.0220 | [-85.7822,-11.8750] | True | 85 |
| eth_w03 | sign_agreement | 10.7539 | 0.0124 | 66 | 114.59 | 0.7622 | [-9.2764,21.6135] | False | 42 |
| eth_w03 | regime_filter | -3.5037 | 0.3972 | 127 | 156.54 | 0.2547 | [-18.8866,7.1599] | True | 73 |
| eth_w03 | continuous_zscore | -9.0689 | 0.5588 | 131 | 152.93 | 0.0370 | [-193.0984,0.7039] | True | 69 |
| eth_w02 | sign_agreement | -3.0244 | 0.0014 | 26 | 57.26 | 0.1289 | [-9.9012,16.0414] | False | 20 |
| eth_w02 | regime_filter | -7.9169 | 0.3907 | 109 | 142.07 | 0.0699 | [-19.1294,-6.0422] | True | 74 |
| eth_w02 | continuous_zscore | 10.7405 | 0.0393 | 134 | 142.54 | 0.8332 | [2.8574,15.8666] | False | 77 |
| eth_w01 | sign_agreement | -12.1654 | 0.1137 | 40 | 67.75 | 0.7323 | [-27.4331,-5.7454] | False | 42 |
| eth_w01 | regime_filter | 3.1949 | 0.2062 | 106 | 143.05 | 0.6394 | [-12.7817,18.9159] | True | 77 |
| eth_w01 | continuous_zscore | -53.9236 | 0.7298 | 91 | 124.45 | 0.0090 | [-365.4270,-29.7925] | True | 62 |

## Controls (per tape)
| tape | options-only Sharpe | orderflow-only Sharpe | flat Sharpe |
|---|---|---|---|
| eth_w05 | 5.0064 | -13.0701 | 0.0000 |
| eth_w04 | -0.0910 | 6.4349 | 0.0000 |
| eth_w03 | 7.8109 | 0.0665 | 0.0000 |
| eth_w02 | 12.2722 | -12.0654 | 0.0000 |
| eth_w01 | 0.1168 | -19.3105 | 0.0000 |

## Pooled verdict
- GO rule: None
- rule `sign_agreement` all-tapes-pass: False
    - eth_w05: pass=False Sharpe=5.5032 p=1.0000 CI_low=-11.9698
    - eth_w04: pass=False Sharpe=16.2609 p=0.2677 CI_low=5.8214
    - eth_w03: pass=False Sharpe=10.7539 p=0.7622 CI_low=-9.2764
    - eth_w02: pass=False Sharpe=-3.0244 p=0.1289 CI_low=-9.9012
    - eth_w01: pass=False Sharpe=-12.1654 p=0.7323 CI_low=-27.4331
- rule `regime_filter` all-tapes-pass: False
    - eth_w05: pass=False Sharpe=-4.2953 p=0.3387 CI_low=-16.0260
    - eth_w04: pass=False Sharpe=-1.3704 p=0.4605 CI_low=-22.6805
    - eth_w03: pass=False Sharpe=-3.5037 p=0.2547 CI_low=-18.8866
    - eth_w02: pass=False Sharpe=-7.9169 p=0.0699 CI_low=-19.1294
    - eth_w01: pass=False Sharpe=3.1949 p=0.6394 CI_low=-12.7817
- rule `continuous_zscore` all-tapes-pass: False
    - eth_w05: pass=False Sharpe=-101.3204 p=0.0160 CI_low=-507.7309
    - eth_w04: pass=False Sharpe=-23.0337 p=0.0220 CI_low=-85.7822
    - eth_w03: pass=False Sharpe=-9.0689 p=0.0370 CI_low=-193.0984
    - eth_w02: pass=False Sharpe=10.7405 p=0.8332 CI_low=2.8574
    - eth_w01: pass=False Sharpe=-53.9236 p=0.0090 CI_low=-365.4270
- Passed: False
- BH-FDR: {"alpha": 0.1, "m_tests": 15, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"eth_w01::continuous_zscore": 0.006666666666666667, "eth_w01::regime_filter": 0.07333333333333333, "eth_w01::sign_agreement": 0.08000000000000002, "eth_w02::continuous_zscore": 0.09333333333333334, "eth_w02::regime_filter": 0.03333333333333333, "eth_w02::sign_agreement": 0.04000000000000001, "eth_w03::continuous_zscore": 0.02666666666666667, "eth_w03::regime_filter": 0.04666666666666667, "eth_w03::sign_agreement": 0.08666666666666667, "eth_w04::continuous_zscore": 0.020000000000000004, "eth_w04::regime_filter": 0.06666666666666667, "eth_w04::sign_agreement": 0.05333333333333334, "eth_w05::continuous_zscore": 0.013333333333333334, "eth_w05::regime_filter": 0.060000000000000005, "eth_w05::sign_agreement": 0.1}}
- Pooled PBO: {"config_details": {"eth_w01::combined_continuous_zscore": {"mean_is_sharpe": -82.6591515135087, "mean_oos_sharpe": -5328.988761009295, "pbo": 0.75, "valid_combinations": 4}, "eth_w01::combined_regime_filter": {"mean_is_sharpe": 3.354098435495829, "mean_oos_sharpe": 20.09428764774859, "pbo": 0.4375, "valid_combinations": 4}, "eth_w01::combined_sign_agreement": {"mean_is_sharpe": -12.29319466197979, "mean_oos_sharpe": -4182.505765296051, "pbo": 0.71875, "valid_combinations": 4}, "eth_w02::combined_continuous_zscore": {"mean_is_sharpe": 10.870226973564161, "mean_oos_sharpe": 435.8240256072399, "pbo": 0.421875, "valid_combinations": 4}, "eth_w02::combined_regime_filter": {"mean_is_sharpe": -9.184810133332787, "mean_oos_sharpe": -15.592104124251385, "pbo": 0.90625, "valid_combinations": 4}, "eth_w02::combined_sign_agreement": {"mean_is_sharpe": -1.254994933768856, "mean_oos_sharpe": 6.733643363186928, "pbo": 0.359375, "valid_combinations": 4}, "eth_w03::combined_continuous_zscore": {"mean_is_sharpe": -11.428018877475264, "mean_oos_sharpe": -79.33762624449943, "pbo": 0.75, "valid_combinations": 4}, "eth_w03::combined_regime_filter": {"mean_is_sharpe": -3.847089162151866, "mean_oos_sharpe": -13.920328242907807, "pbo": 0.546875, "valid_combinations": 4}, "eth_w03::combined_sign_agreement": {"mean_is_sharpe": 11.09661301139213, "mean_oos_sharpe": 464.6947432850914, "pbo": 0.21875, "valid_combinations": 4}, "eth_w04::combined_continuous_zscore": {"mean_is_sharpe": -24.80253713805937, "mean_oos_sharpe": -101.59279513845271, "pbo": 0.546875, "valid_combinations": 4}, "eth_w04::combined_regime_filter": {"mean_is_sharpe": -1.8890523329240843, "mean_oos_sharpe": -7.989365251610535, "pbo": 0.671875, "valid_combinations": 4}, "eth_w04::combined_sign_agreement": {"mean_is_sharpe": 17.41453396221995, "mean_oos_sharpe": 2802958.4967046157, "pbo": 0.640625, "valid_combinations": 4}, "eth_w05::combined_continuous_zscore": {"mean_is_sharpe": -159.223856643293, "mean_oos_sharpe": -939.6396711871857, "pbo": 0.75, "valid_combinations": 4}, "eth_w05::combined_regime_filter": {"mean_is_sharpe": -5.138240258710596, "mean_oos_sharpe": -44.41770533670397, "pbo": 0.640625, "valid_combinations": 4}, "eth_w05::combined_sign_agreement": {"mean_is_sharpe": 5.137910439692911, "mean_oos_sharpe": -1.7284651896507393, "pbo": 0.46875, "valid_combinations": 4}}, "k_folds": 4, "n_combinations_used": 16, "overall_pbo": 0.6666666666666666, "pbo_per_config": {"eth_w01::combined_continuous_zscore": 0.75, "eth_w01::combined_regime_filter": 0.4375, "eth_w01::combined_sign_agreement": 0.71875, "eth_w02::combined_continuous_zscore": 0.421875, "eth_w02::combined_regime_filter": 0.90625, "eth_w02::combined_sign_agreement": 0.359375, "eth_w03::combined_continuous_zscore": 0.75, "eth_w03::combined_regime_filter": 0.546875, "eth_w03::combined_sign_agreement": 0.21875, "eth_w04::combined_continuous_zscore": 0.546875, "eth_w04::combined_regime_filter": 0.671875, "eth_w04::combined_sign_agreement": 0.640625, "eth_w05::combined_continuous_zscore": 0.75, "eth_w05::combined_regime_filter": 0.640625, "eth_w05::combined_sign_agreement": 0.46875}}

## Commands
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
```bash
python3 -m py_compile scripts/eval47_eth_combined_audit.py tests/test_eval47_eth_combined_audit.py
```
```bash
python3 -m pytest -q tests/test_eval47_eth_combined_audit.py
```
```bash
python3 scripts/eval47_eth_combined_audit.py --no-write --max-trades 5000
```
```bash
python3 scripts/eval47_eth_combined_audit.py
```

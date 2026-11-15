# EVAL_45_ETH_ORDERFLOW_META — orderflow full-roster net-of-cost meta-analysis

- **Report ID:** `EVAL_45_ETH_ORDERFLOW_META`
- **Generated:** 2026-11-15T01:27:07.010146Z
- **Task ID:** `INIT-2026-11-15T01:27:07.010146Z-EVAL-45-ETH-ORDERFLOW-META`
- **Verdict:** **NO-GO CONFIRMED (PASS)**
- **Scope:** ETH_FULL_ROSTER
- **Reason:** orderflow-only net-of-cost Sharpe > 0 on only 3/5 tapes (bar: >= 3/5) and 2 kill-switch breach(es) -> Track A NO-GO corroborated across the full roster; the orderflow pillar is definitively closed.

## Inputs
- Full roster met: True
- present `eth_w01`: `data/raw/orderflow_okx_ETH_w01_507773331.json`
- present `eth_w02`: `data/raw/orderflow_okx_ETH_w02_507812331.json`
- present `eth_w03`: `data/raw/orderflow_okx_ETH_w03_507835631.json`
- present `eth_w04`: `data/raw/orderflow_okx_ETH_w04_507848531.json`
- present `eth_w05`: `data/raw/orderflow_okx_ETH_w05_507908231.json`

## Per-tape results
| tape | bars | Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | IC mean |
|---|---|---|---|---|---|---|---|---|---|
| eth_w01 | 421 | -2.9927 | 0.4932 | 109 | 149.12 | 0.6543 | [-26.6182,12.0163] | True | -0.099708 |
| eth_w02 | 421 | 6.0598 | 0.1999 | 129 | 144.84 | 0.3886 | [-2.7779,17.2446] | False | -0.060257 |
| eth_w03 | 422 | 6.0265 | 0.1545 | 173 | 144.30 | 0.3646 | [-6.0605,16.1870] | False | -0.008928 |
| eth_w04 | 421 | 2.8198 | 0.1978 | 168 | 148.73 | 0.5964 | [-8.4519,13.8447] | False | 0.042285 |
| eth_w05 | 422 | -19.8035 | 0.6214 | 157 | 148.01 | 0.0340 | [-40.8857,-8.3752] | True | -0.091212 |

## Pooled verdict
- Tapes: 5; positive Sharpe: 3 (bar >= 3/5)
- Kill-switch breaches: 2 (max-DD > 0.2)
- Passed: False
- BH-FDR: {"alpha": 0.1, "m_tests": 5, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"eth_w01": 0.1, "eth_w02": 0.06000000000000001, "eth_w03": 0.04, "eth_w04": 0.08, "eth_w05": 0.02}}
- Pooled PBO: {"config_details": {"eth_w01": {"mean_is_sharpe": -4.283453425758939, "mean_oos_sharpe": -30.6184121506708, "pbo": 0.75, "valid_combinations": 4}, "eth_w02": {"mean_is_sharpe": 6.092543735312696, "mean_oos_sharpe": 93.45071130182464, "pbo": 0.46875, "valid_combinations": 4}, "eth_w03": {"mean_is_sharpe": 5.73416715053638, "mean_oos_sharpe": 2.1321422901555755, "pbo": 0.484375, "valid_combinations": 4}, "eth_w04": {"mean_is_sharpe": 3.155246981337762, "mean_oos_sharpe": 20.152307663716073, "pbo": 0.484375, "valid_combinations": 4}, "eth_w05": {"mean_is_sharpe": -20.836040640936922, "mean_oos_sharpe": -791.5202617552841, "pbo": 0.4375, "valid_combinations": 4}}, "k_folds": 4, "n_combinations_used": 16, "overall_pbo": 0.2, "pbo_per_config": {"eth_w01": 0.75, "eth_w02": 0.46875, "eth_w03": 0.484375, "eth_w04": 0.484375, "eth_w05": 0.4375}}

## Commands
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
```bash
python3 -m py_compile scripts/eval43_orderflow_full_roster_meta.py tests/test_eval43_orderflow_full_roster_meta.py
```
```bash
python3 -m pytest -q tests/test_eval43_orderflow_full_roster_meta.py
```
```bash
python3 scripts/eval43_orderflow_full_roster_meta.py
```
## Cross-asset consistency (BTC vs ETH)

| asset | verdict | scope | tapes | positive Sharpe | kill-switch breaches |
|---|---|---|---|---|---|
| BTC | NO-GO CONFIRMED (PASS) | SEALED (EVAL-43, cited) | 5 | 1 | 5 |
| ETH | NO-GO CONFIRMED (PASS) | ETH_FULL_ROSTER | 5 | 3 | 2 |

- ETH replicates the BTC NO-GO: True
- BTC control cited from: `research_state/EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z.json`

## ETH windows

| window | trades | bars | Sharpe | max-DD | trades taken | cost $ | perm p | CI |
|---|---|---|---|---|---|---|---|---|
| eth_w01 | 39000 | 421 | -2.9927 | 0.4932 | 109 | 149.12 | 0.6543 | [-26.6182,12.0163] |
| eth_w02 | 23300 | 421 | 6.0598 | 0.1999 | 129 | 144.84 | 0.3886 | [-2.7779,17.2446] |
| eth_w03 | 12900 | 422 | 6.0265 | 0.1545 | 173 | 144.30 | 0.3646 | [-6.0605,16.1870] |
| eth_w04 | 59700 | 421 | 2.8198 | 0.1978 | 168 | 148.73 | 0.5964 | [-8.4519,13.8447] |
| eth_w05 | 37200 | 422 | -19.8035 | 0.6214 | 157 | 148.01 | 0.0340 | [-40.8857,-8.3752] |

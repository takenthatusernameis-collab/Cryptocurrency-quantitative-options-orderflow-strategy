# EVAL_43_ORDERFLOW_FULL_ROSTER_META — orderflow full-roster net-of-cost meta-analysis

- **Report ID:** `EVAL_43_ORDERFLOW_FULL_ROSTER_META`
- **Generated:** 2026-11-14T22:45:16.210996Z
- **Task ID:** `INIT-2026-11-14T22:45:16.210996Z-EVAL-43-ORDERFLOW-FULL-ROSTER-META`
- **Verdict:** **NO-GO CONFIRMED (PASS)**
- **Scope:** FULL_ROSTER
- **Reason:** orderflow-only net-of-cost Sharpe > 0 on only 1/5 tapes (bar: >= 3/5) and 5 kill-switch breach(es) -> Track A NO-GO corroborated across the full roster; the orderflow pillar is definitively closed.

## Inputs
- Full roster met: True
- present `41a`: `data/raw/orderflow_okx_41a.json`
- present `41b`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP_41b_20261113T132756Z.json`
- present `41c`: `data/raw/orderflow_okx_41c.json`
- present `41d_fresh`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json`
- present `midday`: `data/raw/orderflow_okx_BTC-USD-SWAP.json`

## Per-tape results
| tape | bars | Sharpe | max-DD | trades | cost $ | perm p | CI | kill-switch | IC mean |
|---|---|---|---|---|---|---|---|---|---|
| 41a | 1553 | 0.2387 | 0.4414 | 475 | 591.02 | 0.9321 | [-5.5674,5.2980] | True | -0.000140 |
| 41b | 1555 | -8.7851 | 0.9492 | 618 | 635.05 | 0.0030 | [-15.0438,-3.3784] | True | -0.015649 |
| 41c | 1551 | -0.8573 | 0.4647 | 589 | 675.45 | 0.7592 | [-7.0865,4.9187] | True | 0.006067 |
| 41d_fresh | 1552 | -6.3031 | 0.8770 | 677 | 652.66 | 0.0300 | [-13.4319,-1.6901] | True | 0.030685 |
| midday | 1555 | -0.1382 | 0.6897 | 540 | 635.94 | 0.9600 | [-6.9951,5.1641] | True | 0.042009 |

## Pooled verdict
- Tapes: 5; positive Sharpe: 1 (bar >= 3/5)
- Kill-switch breaches: 5 (max-DD > 0.2)
- Passed: False
- BH-FDR: {"alpha": 0.1, "m_tests": 5, "method": "Benjamini-Hochberg", "rejected": ["41b", "41d_fresh"], "thresholds": {"41a": 0.08, "41b": 0.02, "41c": 0.06000000000000001, "41d_fresh": 0.04, "midday": 0.1}}
- Pooled PBO: {"config_details": {"41a": {"mean_is_sharpe": 0.18706009005137145, "mean_oos_sharpe": -0.3246394253869727, "pbo": 0.484375, "valid_combinations": 4}, "41b": {"mean_is_sharpe": -8.98245651638895, "mean_oos_sharpe": -10.369020944415869, "pbo": 0.625, "valid_combinations": 4}, "41c": {"mean_is_sharpe": -0.8691389606193596, "mean_oos_sharpe": -1.0464456449252706, "pbo": 0.53125, "valid_combinations": 4}, "41d_fresh": {"mean_is_sharpe": -6.5520669523239725, "mean_oos_sharpe": -8.04371693192418, "pbo": 0.546875, "valid_combinations": 4}, "midday": {"mean_is_sharpe": -0.16373427389886852, "mean_oos_sharpe": -0.5150592198521724, "pbo": 0.5, "valid_combinations": 4}}, "k_folds": 4, "n_combinations_used": 16, "overall_pbo": 0.6, "pbo_per_config": {"41a": 0.484375, "41b": 0.625, "41c": 0.53125, "41d_fresh": 0.546875, "midday": 0.5}}

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

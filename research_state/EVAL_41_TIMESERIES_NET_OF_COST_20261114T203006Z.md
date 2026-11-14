# EVAL_41_TIMESERIES_NET_OF_COST — Dense options time-series net-of-cost decisive test (EVAL-41 Track B)

- **Report ID:** `EVAL_41_TIMESERIES_NET_OF_COST`
- **Generated:** 2026-11-14T20:30:06.021404Z
- **Task ID:** `INIT-2026-11-14T20:30:06.021404Z-EVAL-41-TRACK-B-DECISIVE`
- **Verdict:** **REPLICATION/NO-GO**
- **Reason:** No options-only variant passed all four criteria on both windows. Best mean OOS Sharpe = options_only_short_thresh0.2 (1.341202); per-window details in the artifact.
- **Provenance:** real_public_exchange_export (authenticity_verified=False)
- Caveat: Public read-only OKX exports; no signed venue attestation.
- Caveat: Options snapshots are OKX option candle closes with reconstructed bid/ask spreads (price_mode=candle_close_with_reconstructed_spread); mid-price parity is meaningful, the bid-ask bound test is not.
- Caveat: Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.
- Caveat: Paper-only; no live trading; .env absent.

## Options inputs
- Snapshots: 101; distinct signal levels: 26
- Window: 2026-11-14T11:35:00Z → 2026-11-14T19:55:00Z

## Window: 41d_fresh (`data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json`)
- Tape: 1552 bars, 2026-11-14T13:22:33.993000Z → 2026-11-14T19:50:29.020000Z
- Held-out slice: 1552 bars, 2026-11-14T13:22:48.993000Z → 2026-11-14T19:50:33.993000Z
- Distinct levels in slice: 24; signal stdev: 0.302157
- IC by horizon: {"1": -0.0012726935009563908, "20": 0.002873148625976845, "5": -0.003370288912030059}
- IC mean: -5.899446e-04; non_constant=True
- Controls: best=flat (Sharpe 0.000000); orderflow_only Sharpe -6.303106 (677 trades); flat Sharpe 0.000000

| variant | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| options_only_long_thresh0.01 | -23.5746 | 702 | 614.73 | 0.0010 | [-34.2316,-17.6095] | False |
| options_only_long_thresh0.02 | -23.5746 | 702 | 614.73 | 0.0010 | [-34.2316,-17.6095] | False |
| options_only_long_thresh0.05 | -23.5746 | 702 | 614.73 | 0.0010 | [-34.2316,-17.6095] | False |
| options_only_long_thresh0.1 | -23.5746 | 702 | 614.73 | 0.0010 | [-34.2316,-17.6095] | False |
| options_only_long_thresh0.2 | -23.5746 | 702 | 614.73 | 0.0010 | [-34.2316,-17.6095] | False |
| options_only_long_thresh0.5 | -23.5746 | 702 | 614.73 | 0.0010 | [-34.2316,-17.6095] | False |
| options_only_short_thresh0.01 | -0.0572 | 80 | 62.41 | 0.7542 | [-3.8501,3.8335] | False |
| options_only_short_thresh0.02 | -0.0572 | 80 | 62.41 | 0.7542 | [-3.8501,3.8335] | False |
| options_only_short_thresh0.05 | -0.0572 | 80 | 62.41 | 0.7542 | [-3.8501,3.8335] | False |
| options_only_short_thresh0.1 | -0.0572 | 80 | 62.41 | 0.7542 | [-3.8501,3.8335] | False |
| options_only_short_thresh0.2 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |
| options_only_short_thresh0.5 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |

## Window: midday_robustness (`data/raw/orderflow_okx_BTC-USD-SWAP.json`)
- Tape: 1555 bars, 2026-11-14T09:05:22.330000Z → 2026-11-14T15:33:56.432000Z
- Held-out slice: 1555 bars, 2026-11-14T09:05:37.330000Z → 2026-11-14T15:34:07.330000Z
- Distinct levels in slice: 17; signal stdev: 0.298018
- IC by horizon: {"1": -0.0595527532313341, "20": -0.3303245943598048, "5": -0.149472811009778}
- IC mean: -1.797834e-01; non_constant=True
- Controls: best=flat (Sharpe 0.000000); orderflow_only Sharpe -0.138183 (540 trades); flat Sharpe 0.000000

| variant | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| options_only_long_thresh0.01 | -11.0328 | 279 | 328.55 | 0.0010 | [-16.4951,-6.3698] | False |
| options_only_long_thresh0.02 | -11.0328 | 279 | 328.55 | 0.0010 | [-16.4951,-6.3698] | False |
| options_only_long_thresh0.05 | -4.7892 | 64 | 128.29 | 0.0619 | [-7.8017,0.7416] | False |
| options_only_long_thresh0.1 | -4.7892 | 64 | 128.29 | 0.0619 | [-7.8017,0.7416] | False |
| options_only_long_thresh0.2 | -4.7892 | 64 | 128.29 | 0.0619 | [-7.8017,0.7416] | False |
| options_only_long_thresh0.5 | -4.7892 | 64 | 128.29 | 0.0619 | [-7.8017,0.7416] | False |
| options_only_short_thresh0.01 | 1.9169 | 120 | 135.68 | 0.4715 | [-5.0328,5.5907] | False |
| options_only_short_thresh0.02 | 1.9169 | 120 | 135.68 | 0.4715 | [-5.0328,5.5907] | False |
| options_only_short_thresh0.05 | 1.9169 | 120 | 135.68 | 0.4715 | [-5.0328,5.5907] | False |
| options_only_short_thresh0.1 | 1.9188 | 114 | 122.20 | 0.4715 | [-5.0209,5.5922] | False |
| options_only_short_thresh0.2 | 2.6824 | 12 | 23.44 | 1.0000 | [-3.8501,5.6100] | False |
| options_only_short_thresh0.5 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |

## Aggregated variants
| variant | mean Sharpe | passed both windows |
|---|---|---|
| options_only_long_thresh0.01 | -17.3037 | False |
| options_only_long_thresh0.02 | -17.3037 | False |
| options_only_long_thresh0.05 | -14.1819 | False |
| options_only_long_thresh0.1 | -14.1819 | False |
| options_only_long_thresh0.2 | -14.1819 | False |
| options_only_long_thresh0.5 | -14.1819 | False |
| options_only_short_thresh0.01 | 0.9299 | False |
| options_only_short_thresh0.02 | 0.9299 | False |
| options_only_short_thresh0.05 | 0.9299 | False |
| options_only_short_thresh0.1 | 0.9308 | False |
| options_only_short_thresh0.2 | 1.3412 | False |
| options_only_short_thresh0.5 | 0.0000 | False |

## Statistical defensibility
- Best variant: options_only_short_thresh0.2 (mean Sharpe 1.341202)
- Per-window PBO/CI: {"41d_fresh": {"bootstrap_ci": [0.0, 0.0, 0.0], "pbo_cscv": {"k_folds": 4, "overall_pbo": 0.3333333333333333, "pbo_per_config": {"flat": 0.0, "options_only_short_thresh0.2": 0.0, "orderflow_only": 0.59375}}, "permutation_p_vs_best_control": 1.0}, "midday_robustness": {"bootstrap_ci": [2.682404755199951, -3.850133687518488, 5.609978816303265], "pbo_cscv": {"k_folds": 4, "overall_pbo": 0.6666666666666666, "pbo_per_config": {"flat": 0.0, "options_only_short_thresh0.2": 0.75, "orderflow_only": 0.53125}}, "permutation_p_vs_best_control": 1.0}}
- BH-FDR: {"alpha": 0.1, "m_tests": 2, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"41d_fresh__options_only_short_thresh0.2": 0.05, "midday_robustness__options_only_short_thresh0.2": 0.1}}

## Commands
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
```
```bash
python3 -m py_compile scripts/eval41_options_timeseries_net_of_cost.py tests/test_eval41_options_timeseries_net_of_cost.py
```
```bash
python3 -m pytest -q tests/test_eval41_options_timeseries_net_of_cost.py
```
```bash
python3 scripts/eval41_options_timeseries_net_of_cost.py
```

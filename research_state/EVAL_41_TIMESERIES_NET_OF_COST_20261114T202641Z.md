# EVAL_41_TIMESERIES_NET_OF_COST — Dense options time-series net-of-cost decisive test (EVAL-41 Track B)

- **Report ID:** `EVAL_41_TIMESERIES_NET_OF_COST`
- **Generated:** 2026-11-14T20:26:41.974676Z
- **Task ID:** `INIT-2026-11-14T20:26:41.974676Z-EVAL-41-TRACK-B-DECISIVE`
- **Verdict:** **REPLICATION/NO-GO**
- **Reason:** No options-only variant passed all four criteria on both windows. Best mean OOS Sharpe = options_only_short_thresh0.01 (2.424684); per-window details in the artifact.
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
- Held-out slice: 480 bars, 2026-11-14T17:50:48.993000Z → 2026-11-14T19:50:33.993000Z
- Distinct levels in slice: 1; signal stdev: 0.000000
- IC by horizon: {"1": 0.0, "20": 0.0, "5": 0.0}
- IC mean: 0.000000e+00; non_constant=False
- Controls: best=flat (Sharpe 0.000000); orderflow_only Sharpe -5.597338 (128 trades); flat Sharpe 0.000000

| variant | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| options_only_long_thresh0.01 | -26.6523 | 157 | 166.71 | 0.0030 | [-77.4175,-16.3864] | False |
| options_only_long_thresh0.02 | -26.6523 | 157 | 166.71 | 0.0030 | [-77.4175,-16.3864] | False |
| options_only_long_thresh0.05 | -26.6523 | 157 | 166.71 | 0.0030 | [-77.4175,-16.3864] | False |
| options_only_long_thresh0.1 | -26.6523 | 157 | 166.71 | 0.0030 | [-77.4175,-16.3864] | False |
| options_only_long_thresh0.2 | -26.6523 | 157 | 166.71 | 0.0030 | [-77.4175,-16.3864] | False |
| options_only_long_thresh0.5 | -26.6523 | 157 | 166.71 | 0.0030 | [-77.4175,-16.3864] | False |
| options_only_short_thresh0.01 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |
| options_only_short_thresh0.02 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |
| options_only_short_thresh0.05 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |
| options_only_short_thresh0.1 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |
| options_only_short_thresh0.2 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |
| options_only_short_thresh0.5 | 0.0000 | 0 | 0.00 | 1.0000 | [0.0000,0.0000] | False |

## Window: midday_robustness (`data/raw/orderflow_okx_BTC-USD-SWAP.json`)
- Tape: 1555 bars, 2026-11-14T09:05:22.330000Z → 2026-11-14T15:33:56.432000Z
- Held-out slice: 480 bars, 2026-11-14T13:34:22.330000Z → 2026-11-14T15:34:07.330000Z
- Distinct levels in slice: 14; signal stdev: 0.424252
- IC by horizon: {"1": -0.04404983332997052, "20": -0.2461127887402151, "5": -0.10981073085483703}
- IC mean: -1.333245e-01; non_constant=True
- Controls: best=orderflow_only (Sharpe 3.304091); orderflow_only Sharpe 3.304091 (121 trades); flat Sharpe 0.000000

| variant | Sharpe | trades | cost $ | perm p | CI | pass |
|---|---|---|---|---|---|---|
| options_only_long_thresh0.01 | -11.1890 | 70 | 122.94 | 0.2468 | [-22.3180,-4.6840] | False |
| options_only_long_thresh0.02 | -11.1890 | 70 | 122.94 | 0.2468 | [-22.3180,-4.6840] | False |
| options_only_long_thresh0.05 | -11.1890 | 70 | 122.94 | 0.2468 | [-22.3180,-4.6840] | False |
| options_only_long_thresh0.1 | -11.1890 | 70 | 122.94 | 0.2468 | [-22.3180,-4.6840] | False |
| options_only_long_thresh0.2 | -11.1890 | 70 | 122.94 | 0.2468 | [-22.3180,-4.6840] | False |
| options_only_long_thresh0.5 | -11.1890 | 70 | 122.94 | 0.2468 | [-22.3180,-4.6840] | False |
| options_only_short_thresh0.01 | 4.8494 | 66 | 43.54 | 0.7772 | [-5.6125,10.5490] | False |
| options_only_short_thresh0.02 | 4.8494 | 66 | 43.54 | 0.7772 | [-5.6125,10.5490] | False |
| options_only_short_thresh0.05 | 4.8494 | 66 | 43.54 | 0.7772 | [-5.6125,10.5490] | False |
| options_only_short_thresh0.1 | 4.8494 | 66 | 43.54 | 0.7772 | [-5.6125,10.5490] | False |
| options_only_short_thresh0.2 | 0.0000 | 0 | 0.00 | 0.4805 | [0.0000,0.0000] | False |
| options_only_short_thresh0.5 | 0.0000 | 0 | 0.00 | 0.4805 | [0.0000,0.0000] | False |

## Aggregated variants
| variant | mean Sharpe | passed both windows |
|---|---|---|
| options_only_long_thresh0.01 | -18.9206 | False |
| options_only_long_thresh0.02 | -18.9206 | False |
| options_only_long_thresh0.05 | -18.9206 | False |
| options_only_long_thresh0.1 | -18.9206 | False |
| options_only_long_thresh0.2 | -18.9206 | False |
| options_only_long_thresh0.5 | -18.9206 | False |
| options_only_short_thresh0.01 | 2.4247 | False |
| options_only_short_thresh0.02 | 2.4247 | False |
| options_only_short_thresh0.05 | 2.4247 | False |
| options_only_short_thresh0.1 | 2.4247 | False |
| options_only_short_thresh0.2 | 0.0000 | False |
| options_only_short_thresh0.5 | 0.0000 | False |

## Statistical defensibility
- Best variant: options_only_short_thresh0.01 (mean Sharpe 2.424684)
- Per-window PBO/CI: {"41d_fresh": {"bootstrap_ci": [0.0, 0.0, 0.0], "pbo_cscv": {"k_folds": 4, "overall_pbo": 0.3333333333333333, "pbo_per_config": {"flat": 0.0, "options_only_short_thresh0.01": 0.0, "orderflow_only": 0.609375}}, "permutation_p_vs_best_control": 1.0}, "midday_robustness": {"bootstrap_ci": [4.849367573216655, -5.612486080160913, 10.548974546131957], "pbo_cscv": {"k_folds": 4, "overall_pbo": 0.6666666666666666, "pbo_per_config": {"flat": 0.0, "options_only_short_thresh0.01": 0.828125, "orderflow_only": 0.53125}}, "permutation_p_vs_best_control": 0.7772227772227772}}
- BH-FDR: {"alpha": 0.1, "m_tests": 2, "method": "Benjamini-Hochberg", "rejected": [], "thresholds": {"41d_fresh__options_only_short_thresh0.01": 0.1, "midday_robustness__options_only_short_thresh0.01": 0.05}}

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

# EVAL_49_PREREGISTRATION — pre-registration (EVAL-46 integrated options+orderflow)

- **Report ID:** `EVAL_49_PREREGISTRATION`
- **Generated:** 2026-11-15T10:11:49.663337Z
- **Task ID:** `INIT-2026-11-15T10:11:49.663337Z-EVAL-49-ETH-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL`
- **Status:** PREREGISTERED

## Hypothesis
The fused options+orderflow strategy is net-of-cost tradable when the options leg is sourced from Deribit ETH (a different venue) while orderflow is the same real OKX ETH tape: at least one pre-declared fusion rule yields combined Sharpe > 0 with no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on all real ETH orderflow tapes.

## Options dataset
- snapshots: 109; distinct levels: 10
- span: 2026-11-14T20:20:00Z → 2026-11-15T05:20:00Z
- manifest sha256: `5efb3988f6ac275f11ced6505dba305bc8f2cd264ab3160a575d9df449b3f33f`

## Orderflow tapes
- `eth_w05`: `data/raw/eval45/orderflow_okx_ETH_w05_507849899.json` — 71200 trades, 428 bars, sha256 `cf249c1f4e7f3ca8…`
- `eth_w04`: `data/raw/eval45/orderflow_okx_ETH_w04_507921099.json` — 27000 trades, 421 bars, sha256 `9142bcf5c8921960…`
- `eth_w03`: `data/raw/eval45/orderflow_okx_ETH_w03_507948099.json` — 42200 trades, 422 bars, sha256 `b6c68145b04a6cdd…`
- `eth_w02`: `data/raw/eval45/orderflow_okx_ETH_w02_507990299.json` — 54900 trades, 421 bars, sha256 `2ec36212f811c7b2…`
- `eth_w01`: `data/raw/eval45/orderflow_okx_ETH_w01_508045199.json` — 12300 trades, 421 bars, sha256 `e9ef4da654f2df25…`

## Protocol
- bar_duration_seconds: 15.0
- signal_lookback_seconds: 60.0
- signal_threshold: 0.1
- toxicity_window_trades: 5
- toxicity_threshold: 0.7
- train_window: 120
- test_window: 40
- step_size: 40
- purge: 10
- embargo: 5
- max_position_pct: 0.2
- fusion_rules: ['sign_agreement', 'regime_filter', 'continuous_zscore']
- z_threshold: 0.5
- z_min_periods: 5
- cost_model_bps_nav_per_window: 2.0
- guardrail_bps: 0.5
- kill_switch_max_drawdown: 0.2
- permutation_perms: 1000
- bootstrap_resamples: 1000
- bootstrap_block: 2
- pbo_k_folds: 4
- pbo_n_combinations: 16
- fdr_alpha: 0.1
- seed: 42
- go_bar: GO only if, across all 5 real ETH orderflow tapes, at least one fusion rule shows combined net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05 and bootstrap 95% CI lower > 0; otherwise NO-GO CONFIRMED (PASS).

## Fusion rules
- `sign_agreement`: both pillars agree in sign (_fuse_positions), toxicity gate
- `regime_filter`: options sign as causal regime gate x orderflow direction (product of thresholded signs), toxicity gate
- `continuous_zscore`: causal expanding z-score of each pillar, summed, thresholded at z_threshold, toxicity gate

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

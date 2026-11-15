# EVAL_48_PREREGISTRATION — pre-registration (EVAL-46 integrated options+orderflow)

- **Report ID:** `EVAL_48_PREREGISTRATION`
- **Generated:** 2026-11-15T08:19:51.680403Z
- **Task ID:** `INIT-2026-11-15T08:19:51.680403Z-EVAL-48-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL`
- **Status:** PREREGISTERED

## Hypothesis
The fused options+orderflow strategy is net-of-cost tradable when the options leg is sourced from Deribit (a different venue) while orderflow is the same real OKX BTC tape: at least one pre-declared fusion rule yields combined Sharpe > 0 with no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on both real BTC orderflow tapes.

## Options dataset
- snapshots: 133; distinct levels: 46
- span: 2026-11-14T09:00:00Z → 2026-11-14T20:00:00Z
- manifest sha256: `2a235328da9dd47761f5bab65d4bb18bdebede58c3b16bf79fdb921fdd538be8`

## Orderflow tapes
- `41d_fresh`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json` — 120000 trades, 1552 bars, sha256 `ebebd473845ba4bf…`
- `midday`: `data/raw/eval41/orderflow_okx_BTC-USD-SWAP_midday_20261114T090522Z.json` — 77698 trades, 1555 bars, sha256 `045660c21d4b9873…`

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
- go_bar: GO only if, across both real BTC orderflow tapes, at least one fusion rule shows combined net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05 and bootstrap 95% CI lower > 0; otherwise NO-GO CONFIRMED (PASS).

## Fusion rules
- `sign_agreement`: both pillars agree in sign (_fuse_positions), toxicity gate
- `regime_filter`: options sign as causal regime gate x orderflow direction (product of thresholded signs), toxicity gate
- `continuous_zscore`: causal expanding z-score of each pillar, summed, thresholded at z_threshold, toxicity gate

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

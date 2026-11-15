# EVAL_46_PREREGISTRATION — pre-registration (EVAL-46 integrated options+orderflow)

- **Report ID:** `EVAL_46_PREREGISTRATION`
- **Generated:** 2026-11-15T04:16:21.171410Z
- **Task ID:** `INIT-2026-11-15T04:16:21.171410Z-EVAL-46-INTEGRATED-OPTIONS-ORDERFLOW-NET-OF-COST-FALSIFY-AND-SEAL`
- **Status:** PREREGISTERED

## Hypothesis
The fused options+orderflow strategy is net-of-cost tradable on dense real BTC data: at least one pre-declared fusion rule yields combined Sharpe > 0 with no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on both tapes.

## Options dataset
- snapshots: 101; distinct levels: 26
- span: 2026-11-14T11:35:00Z → 2026-11-14T19:55:00Z
- manifest sha256: `49f58f4fa76bad6b66e01749b499c0ddf113e021572d4af337d9749784d6e986`

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
- go_bar: GO only if, across both real BTC tapes, at least one fusion rule shows combined net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05 and bootstrap 95% CI lower > 0; otherwise NO-GO CONFIRMED (PASS).

## Fusion rules
- `sign_agreement`: both pillars agree in sign (_fuse_positions), toxicity gate
- `regime_filter`: options sign as causal regime gate x orderflow direction (product of thresholded signs), toxicity gate
- `continuous_zscore`: causal expanding z-score of each pillar, summed, thresholded at z_threshold, toxicity gate

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

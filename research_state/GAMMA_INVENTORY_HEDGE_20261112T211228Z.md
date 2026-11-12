# GAMMA/INVENTORY HEDGE + ORDERFLOW TOXICITY GATE REPORT — EVAL-09

- Report ID: GAMMA_INVENTORY_HEDGE_EVAL_09
- Generated at: 2026-11-12T21:12:46.177261Z
- Symbols: BTC, ETH, SOL
- Venues: synthetic_a, synthetic_b, synthetic_c
- Seeds: [1, 2, 3, 4, 5]
- Target delta: 0.0 | Toxicity threshold: 0.7 | Hedge cost: 1.0 bps | Spread: 0.5 bps
- Impact coeff: 10.0 | Max participation: 0.2 | Cost budget: 2.0 bps/window

## AGGREGATE (with hedge+gate vs without)

- num_seeds: 5
- mean_oos_return_with_hedge: -0.5580107668605527
- mean_oos_return_without_hedge: 0.2590709968068878
- return_delta_with_vs_without_hedge: -0.8170817636674406
- mean_oos_sharpe_with_hedge: -22.765929562035716
- mean_oos_sharpe_without_hedge: 5.586740988848094
- sharpe_delta_with_vs_without_hedge: -28.352670550883808
- mean_oos_max_drawdown_with_hedge: 0.6650281596585674
- mean_oos_max_drawdown_without_hedge: 0.07613149245412579
- mean_abs_delta_usd_with_hedge: 385.35085619156484
- mean_toxicity_score: 0.713277330797748
- toxic_gate_active_fraction: 0.3333333333333333
- total_hedges: 844
- total_skipped_due_to_toxicity: 4856
- total_cost_usd: 1429.6848986289629
- total_traded_notional: 13689424.313120896
- total_trades: 1515
- total_bars: 5700

## Per-seed headline (with hedge+gate vs without)

- seed 1: ret_with=-0.518750, ret_without=0.161198, sharpe_with=-45.641844, sharpe_without=4.915864, maxdd_with=0.644609, maxdd_without=0.092899, toxicity=0.7133, tox_frac=0.3333, hedges=187, skipped=953, abs_delta=412.4699
- seed 2: ret_with=-0.718327, ret_without=-0.023260, sharpe_with=-23.093939, sharpe_without=-0.805559, maxdd_with=0.718327, maxdd_without=0.105750, toxicity=0.7133, tox_frac=0.3333, hedges=173, skipped=967, abs_delta=173.7803
- seed 3: ret_with=-0.517960, ret_without=0.564579, sharpe_with=-7.763543, sharpe_without=10.709375, maxdd_with=0.671613, maxdd_without=0.041900, toxicity=0.7133, tox_frac=0.3333, hedges=156, skipped=984, abs_delta=445.0022
- seed 4: ret_with=-0.519759, ret_without=0.276381, sharpe_with=-11.851918, sharpe_without=5.190677, maxdd_with=0.617836, maxdd_without=0.064611, toxicity=0.7133, tox_frac=0.3333, hedges=116, skipped=1024, abs_delta=333.0365
- seed 5: ret_with=-0.515257, ret_without=0.316457, sharpe_with=-25.478404, sharpe_without=7.923349, maxdd_with=0.672755, maxdd_without=0.075497, toxicity=0.7133, tox_frac=0.3333, hedges=212, skipped=928, abs_delta=562.4654

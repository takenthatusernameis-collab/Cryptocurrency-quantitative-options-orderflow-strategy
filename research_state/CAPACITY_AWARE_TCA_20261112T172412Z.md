# CAPACITY-AWARE TCA REPORT — EVAL-07

- Report ID: CAPACITY_AWARE_TCA_EVAL_07
- Generated at: 2026-11-12T17:24:29.932828Z
- Symbols: BTC, ETH, SOL
- Seeds: [1, 2, 3, 4, 5]
- Spread: 0.5 bps | Impact coeff: 10.0 bps/sqrt(pr)
- Max participation: 0.2 | Cost budget: 2.0 bps/window

## AGGREGATE (capacity-aware vs flat-cost baseline)

- num_seeds: 5
- mean_capacity_net_sharpe: 8.25049148859019
- mean_capacity_net_return: 0.26785468818953473
- mean_baseline_net_sharpe: 9.197960400437712
- mean_baseline_net_return: 0.32330666916324297
- capacity_vs_baseline_sharpe: -0.9474689118475208
- capacity_vs_baseline_return: -0.05545198097370824
- total_capacity_limited_orders: 294
- total_budget_limited_orders: 294

## Cost grid (mean net Sharpe / net return across seeds, flat baseline)

- 0.0 bps: net_sharpe=9.197960, net_return=0.323307
- 1.0 bps: net_sharpe=9.157067, net_return=0.321648
- 5.0 bps: net_sharpe=8.992882, net_return=0.315030
- 10.0 bps: net_sharpe=8.786285, net_return=0.306800

## Per-seed summary (capacity-aware)

- seed 1: capacity net_sharpe=8.246722, net_return=0.163745, max_dd=0.041123, trades=190, windows=10 | baseline net_sharpe=4.415173, net_return=0.094761
- seed 2: capacity net_sharpe=-3.292368, net_return=-0.028673, max_dd=0.032440, trades=155, windows=10 | baseline net_sharpe=3.509129, net_return=0.044706
- seed 3: capacity net_sharpe=18.541833, net_return=0.576003, max_dd=0.000000, trades=210, windows=10 | baseline net_sharpe=19.772313, net_return=0.752830
- seed 4: capacity net_sharpe=7.933925, net_return=0.295441, max_dd=0.023821, trades=134, windows=10 | baseline net_sharpe=8.095658, net_return=0.361902
- seed 5: capacity net_sharpe=9.822345, net_return=0.332758, max_dd=0.030602, trades=240, windows=10 | baseline net_sharpe=10.197530, net_return=0.362335

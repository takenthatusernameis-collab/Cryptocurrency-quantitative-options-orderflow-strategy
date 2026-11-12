# CROSS-VENUE DELTA NETTING REPORT — EVAL-08

- Report ID: CROSS_VENUE_NETTING_EVAL_08
- Generated at: 2026-11-12T20:09:23.410168Z
- Symbols: BTC, ETH, SOL
- Venues: synthetic_a, synthetic_b, synthetic_c
- Venue count: 3 | sign pattern: [1.0, -1.0, 1.0]
- Seeds: [1, 2, 3, 4, 5]
- Spread: 1.0 bps | Impact coeff: 10.0 bps/sqrt(pr)
- Max participation: 0.2 | Cost budget: 2.0 bps/window

## AGGREGATE (with netting vs without netting)

- num_seeds: 5
- mean_gross_notional: 2534948.0450330623
- mean_net_notional: 904597.7002670342
- mean_net_notional_ratio: 0.35566569003105825
- mean_cost_saved_usd: 163.03503447660282
- mean_cost_saved_bps: 1.6303503447660284
- mean_oos_sharpe_with_netting: 8.006530221409474
- mean_oos_sharpe_without_netting: 5.796607763078798
- sharpe_delta_with_vs_without_netting: 2.2099224583306754
- mean_oos_return_with_netting: 0.08870178614400395
- mean_oos_return_without_netting: 0.21764015361877648
- return_delta_with_vs_without_netting: -0.12893836747477253
- mean_oos_max_drawdown_with_netting: 0.014245078634484713
- mean_oos_max_drawdown_without_netting: 0.030160781440439
- total_trades: 612
- total_windows: 50
- total_capacity_limited_orders: 1839

## Per-seed summary

- seed 1: gross_notional=2745328.98, net_notional=902653.14, ratio=0.328796, cost_saved_usd=184.267584, cost_saved_bps=1.842676, trades=133, windows=10, sharpe_with=6.933673, sharpe_without=5.722410, ret_with=0.058584, ret_without=0.100221
- seed 2: gross_notional=2194585.88, net_notional=855181.10, ratio=0.389678, cost_saved_usd=133.940478, cost_saved_bps=1.339405, trades=105, windows=10, sharpe_with=-2.192284, sharpe_without=-11.842969, ret_with=-0.013721, ret_without=-0.060494
- seed 3: gross_notional=2643598.60, net_notional=804533.44, ratio=0.304333, cost_saved_usd=183.906517, cost_saved_bps=1.839065, trades=128, windows=10, sharpe_with=18.035802, sharpe_without=18.792604, ret_with=0.190947, ret_without=0.494145
- seed 4: gross_notional=2081978.83, net_notional=702621.27, ratio=0.337478, cost_saved_usd=137.935756, cost_saved_bps=1.379358, trades=94, windows=10, sharpe_with=8.173999, sharpe_without=7.435763, ret_with=0.099837, ret_without=0.243823
- seed 5: gross_notional=3009247.94, net_notional=1257999.55, ratio=0.418045, cost_saved_usd=175.124838, cost_saved_bps=1.751248, trades=152, windows=10, sharpe_with=9.081462, sharpe_without=8.875231, ret_with=0.107862, ret_without=0.310505

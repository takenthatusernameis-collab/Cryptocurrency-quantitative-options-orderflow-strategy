# STRATEGY FALSIFICATION REPORT — EVAL-06 (Net-of-Cost OOS Falsification)

- Report ID: STRATEGY_FALSIFICATION_EVAL_06
- Generated at: 2026-11-12T16:35:37.307662Z
- Symbols: BTC, ETH, SOL
- Seeds: [1, 2, 3, 4, 5]
- Cost grid (bps): [0, 1, 5, 10] (net baseline: 1.0 bp)
- Permutations: 1000

## VERDICT

## NO-GO

## Aggregate

- num_seeds: 5
- seeds_passing: 3
- pass_fraction: 0.6
- go_seed_fraction: 0.7
- mean_net_sharpe: 8.860771301305718
- mean_net_return: 0.025482060068668044
- mean_gross_sharpe: 8.99456039326873
- mean_gross_return: 0.025916152477790933
- sharpe_advancement_vs_gross: -0.13378909196301159
- return_advancement_vs_gross: -0.00043409240912288885
- mean_bootstrap_lower_bound: 0.0005288765105698277
- mean_permutation_p_value: 0.752
- mean_deflated_sharpe: 0.0

## Cost grid (mean net Sharpe / net return across seeds)

- 0.0 bps: net_sharpe=8.994560, net_return=0.025916
- 1.0 bps: net_sharpe=8.860771, net_return=0.025482
- 5.0 bps: net_sharpe=8.074472, net_return=0.023146
- 10.0 bps: net_sharpe=7.373425, net_return=0.020983

## Gates

- net_sharpe_positive: pass=True | mean net Sharpe > 0 across seeds
- bootstrap_or_permutation: pass=True | mean bootstrap lower bound > 0 or mean permutation p < 0.05
- net_return_positive: pass=True | mean net return > 0 across seeds
- seed_majority: pass=False | >= 0.7 of seeds pass all conditions

## Failing conditions

- seed 1: bootstrap_or_permutation
- seed 4: bootstrap_or_permutation

## Per-seed summary

- seed 1: net_sharpe=8.851718, net_return=0.027294, max_dd=0.006193, trades=319, windows=10, bootstrap_lo=-0.000546, perm_p=0.5960, deflated_sharpe=0.000000, pass=False
- seed 2: net_sharpe=8.457322, net_return=0.016688, max_dd=0.005680, trades=255, windows=10, bootstrap_lo=0.000383, perm_p=0.8510, deflated_sharpe=0.000000, pass=True
- seed 3: net_sharpe=10.516874, net_return=0.036148, max_dd=0.003140, trades=368, windows=10, bootstrap_lo=0.001719, perm_p=0.7000, deflated_sharpe=0.000000, pass=True
- seed 4: net_sharpe=5.953321, net_return=0.010240, max_dd=0.001862, trades=221, windows=10, bootstrap_lo=-0.000168, perm_p=0.8610, deflated_sharpe=0.000000, pass=False
- seed 5: net_sharpe=10.524622, net_return=0.037040, max_dd=0.003338, trades=408, windows=10, bootstrap_lo=0.001256, perm_p=0.7520, deflated_sharpe=0.000000, pass=True

## Regime-conditioned performance (net baseline, last seed shown structure; see JSON for all seeds)

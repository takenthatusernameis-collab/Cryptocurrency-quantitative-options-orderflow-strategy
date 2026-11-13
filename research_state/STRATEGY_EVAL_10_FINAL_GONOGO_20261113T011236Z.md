# FINAL NET-OF-COST GO/NO-GO CERTIFICATION REPORT — EVAL-10

- Report ID: STRATEGY_EVAL_10_FINAL_GONOGO
- Generated at: 2026-11-13T01:12:55.492368Z
- Symbols: BTC, ETH, SOL
- Seeds: [1, 2, 3, 4, 5]
- Cost grid (bps): [0, 1, 5, 10] (net baseline: 1.0 bp)
- Permutations: 1000

## VERDICT

## NO-GO

## Aggregate (15 seed×symbol series at 1 bp net baseline)

- num_seeds: 5
- seeds_passing: 0
- pass_fraction: 0.0
- series_pass_fraction: 0.2
- go_seed_fraction: 0.7
- verdict: NO-GO
- mean_net_return: -0.5580107668605527
- mean_net_sharpe: -22.765929562035716
- total_series: 15
- passing_series: 3

## Block-bootstrap CI (seed-fixed, deterministic, 2000 resamples, block=3)

- bootstrap_ci_mean_net_return: point=-0.558011, lo=-0.642078, hi=-0.505736, block_size=3, n_bootstrap=2000
- bootstrap_ci_mean_net_sharpe: point=-22.765930, lo=-36.746608, hi=-11.137883, block_size=3, n_bootstrap=2000

## Paired permutation: with-hedge vs without-hedge (all series)

- observed_difference: -0.230609
- p_value: 0.000500
- significant_at_05: True
- paired: True, n_permutations: 2000
- statistic_a (with-hedge): -0.206877
- statistic_b (without-hedge): 0.023732

## Cost grid (mean net Sharpe / mean net return across series)

- 0.0 bps: mean_net_sharpe=-22.759877, mean_net_return=-0.557641, series=15
- 1.0 bps: mean_net_sharpe=-22.765930, mean_net_return=-0.558011, series=15
- 5.0 bps: mean_net_sharpe=-22.790230, mean_net_return=-0.559488, series=15
- 10.0 bps: mean_net_sharpe=-22.820814, mean_net_return=-0.561329, series=15

## EVAL-06 flat-cost baseline (reference only)

- present: True
- artifact: research_state/STRATEGY_FALSIFICATION_20261112T163240Z.json
- verdict: NO-GO
- pass_fraction: 0.6
- mean_net_sharpe: 8.860771301305718
- mean_net_return: 0.025482060068668044

## Failing conditions

- BTC: net_sharpe_positive
- BTC: bootstrap_lower_positive
- BTC: net_return_positive
- SOL: net_sharpe_positive
- SOL: net_return_positive
- BTC: net_sharpe_positive
- BTC: net_return_positive
- ETH: net_sharpe_positive
- ETH: bootstrap_lower_positive
- ETH: net_return_positive
- SOL: net_sharpe_positive
- SOL: net_return_positive
- BTC: net_sharpe_positive
- BTC: net_return_positive
- SOL: net_sharpe_positive
- SOL: net_return_positive
- BTC: net_sharpe_positive
- BTC: bootstrap_lower_positive
- BTC: net_return_positive
- ETH: bootstrap_lower_positive
- SOL: net_sharpe_positive
- SOL: net_return_positive
- BTC: net_sharpe_positive
- BTC: net_return_positive
- SOL: net_sharpe_positive
- SOL: net_return_positive

## Per-seed summary

- seed 1: seed_pass=False, symbols_passing=1/3, failing=['BTC: net_sharpe_positive', 'BTC: bootstrap_lower_positive', 'BTC: net_return_positive', 'SOL: net_sharpe_positive', 'SOL: net_return_positive']
- seed 2: seed_pass=False, symbols_passing=0/3, failing=['BTC: net_sharpe_positive', 'BTC: net_return_positive', 'ETH: net_sharpe_positive', 'ETH: bootstrap_lower_positive', 'ETH: net_return_positive', 'SOL: net_sharpe_positive', 'SOL: net_return_positive']
- seed 3: seed_pass=False, symbols_passing=1/3, failing=['BTC: net_sharpe_positive', 'BTC: net_return_positive', 'SOL: net_sharpe_positive', 'SOL: net_return_positive']
- seed 4: seed_pass=False, symbols_passing=0/3, failing=['BTC: net_sharpe_positive', 'BTC: bootstrap_lower_positive', 'BTC: net_return_positive', 'ETH: bootstrap_lower_positive', 'SOL: net_sharpe_positive', 'SOL: net_return_positive']
- seed 5: seed_pass=False, symbols_passing=1/3, failing=['BTC: net_sharpe_positive', 'BTC: net_return_positive', 'SOL: net_sharpe_positive', 'SOL: net_return_positive']

# HEDGE-DRAG / COST-EFFICIENCY OPTIMIZER REPORT — EVAL-11

- Report ID: HEDGE_COST_OPTIMIZER_EVAL_11
- Generated at: 2026-11-13T00:45:10.222228Z
- Verdict: FEASIBLE_POSITIVE_SHARPE
- Search seeds: [1, 2, 3] | Final seeds: [1, 2, 3, 4, 5]
- Grids: target_delta=[-20000.0, 0.0, 20000.0], toxicity=[0.5, 0.7, 0.9], cost_budget_bps=[0.5, 2.0, 5.0]
- Delta constraint: |mean_abs_delta_usd| <= 50000.0
- hedge_cost_bps=1.0 is inert in EVAL-09; cost_budget_bps is the effective cost lever.

## SEARCH SURFACE (27 configs, 18 feasible)

| target_delta_usd | toxicity_threshold | cost_budget_bps | mean_net_sharpe | mean_net_return | mean_abs_delta_usd | total_hedges | feasible |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| -20000 | 0.50 | 0.50 | 7.400682 | 0.142271 | 391.24 | 0 | False |
| -20000 | 0.50 | 2.00 | 4.939893 | 0.234172 | 1274.54 | 0 | False |
| -20000 | 0.50 | 5.00 | 4.913259 | 0.298322 | 1783.11 | 0 | False |
| -20000 | 0.70 | 0.50 | 15.476855 | 0.476859 | 150.82 | 2280 | True |
| -20000 | 0.70 | 2.00 | 12.127522 | 0.832557 | 375.17 | 2280 | True |
| -20000 | 0.70 | 5.00 | 13.747670 | 6.315821 | 524.74 | 2280 | True |
| -20000 | 0.90 | 0.50 | 15.476855 | 0.476859 | 150.82 | 2280 | True |
| -20000 | 0.90 | 2.00 | 12.127522 | 0.832557 | 375.17 | 2280 | True |
| -20000 | 0.90 | 5.00 | 13.747670 | 6.315821 | 524.74 | 2280 | True |
| 0 | 0.50 | 0.50 | 7.400682 | 0.142271 | 391.24 | 0 | False |
| 0 | 0.50 | 2.00 | 4.939893 | 0.234172 | 1274.54 | 0 | False |
| 0 | 0.50 | 5.00 | 4.913259 | 0.298322 | 1783.11 | 0 | False |
| 0 | 0.70 | 0.50 | -54.561694 | -0.510312 | 104.95 | 471 | True |
| 0 | 0.70 | 2.00 | -25.499775 | -0.585013 | 343.75 | 516 | True |
| 0 | 0.70 | 5.00 | -16.983234 | -0.540208 | 508.73 | 641 | True |
| 0 | 0.90 | 0.50 | -54.561694 | -0.510312 | 104.95 | 471 | True |
| 0 | 0.90 | 2.00 | -25.499775 | -0.585013 | 343.75 | 516 | True |
| 0 | 0.90 | 5.00 | -16.983234 | -0.540208 | 508.73 | 641 | True |
| 20000 | 0.50 | 0.50 | 7.400682 | 0.142271 | 391.24 | 0 | False |
| 20000 | 0.50 | 2.00 | 4.939893 | 0.234172 | 1274.54 | 0 | False |
| 20000 | 0.50 | 5.00 | 4.913259 | 0.298322 | 1783.11 | 0 | False |
| 20000 | 0.70 | 0.50 | -37.671804 | -0.591136 | 226.86 | 2280 | True |
| 20000 | 0.70 | 2.00 | -19.743006 | -0.600039 | 465.67 | 2280 | True |
| 20000 | 0.70 | 5.00 | -18.073931 | -0.541359 | 630.64 | 2280 | True |
| 20000 | 0.90 | 0.50 | -37.671804 | -0.591136 | 226.86 | 2280 | True |
| 20000 | 0.90 | 2.00 | -19.743006 | -0.600039 | 465.67 | 2280 | True |
| 20000 | 0.90 | 5.00 | -18.073931 | -0.541359 | 630.64 | 2280 | True |

## BEST FEASIBLE CONFIG (SEARCH)

- target_delta_usd=-20000.0, toxicity_threshold=0.7, cost_budget_bps=0.5
- mean_net_sharpe=15.476855
- mean_net_return=0.476859
- mean_abs_delta_usd=150.82
- total_hedges=2280

## BEST FEASIBLE CONFIG (FINAL MULTI-SEED)

- mean_net_sharpe=13.188322
- mean_net_return=0.399995
- mean_abs_delta_usd=161.89
- total_hedges=3800
- feasible=True
- failure_reasons=[]

## NO-HEDGE CONTROL (FINAL MULTI-SEED)

- mean_oos_return=0.113854
- mean_oos_sharpe=5.590936

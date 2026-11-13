# REAL-DATA WALK-FORWARD CERTIFICATION — EVAL-12

- Report ID: REAL_WF_CERTIFICATION_EVAL_12
- Generated at: 2026-11-13T01:05:46.146929Z
- Verdict: GO
- Seeds: [1, 2, 3, 4, 5]
- Walk-forward: train=120, test=40, step=40, purge=10, embargo=5

## DATA REALITY CHECK
- BTC orderflow file exists: True (1000 trades)
- BTC options file exists: True (30 quotes)
- ETH orderflow file exists: False (synthetic fallback used)
- ETH options file exists: False (synthetic fallback used)
- Processed venue snapshots (aggregate only): 6
- Evidence matrix: {'btc_real_trades': True, 'eth_synthetic_fallback': True, 'sol_synthetic_fallback': True, 'venue_snapshots_aggregate_only': True}

## CANDIDATE CONFIGS
- EVAL11_best: target_delta_usd=-20000, toxicity_threshold=0.70, cost_budget_bps=0.50
- EVAL10_default: target_delta_usd=0, toxicity_threshold=0.70, cost_budget_bps=2.00

## PER-CONFIG RESULTS
### EVAL11_best
- Config: {'target_delta_usd': -20000.0, 'toxicity_threshold': 0.7, 'cost_budget_bps': 0.5}
- Series: 15 (seeds: 5)
- Total windows: 150
- Mean net Sharpe: 13.188322
- Mean net return: 0.399995
- Mean net ann vol: 0.726413
- Mean max DD: 0.069660

### EVAL10_default
- Config: {'target_delta_usd': 0.0, 'toxicity_threshold': 0.7, 'cost_budget_bps': 2.0}
- Series: 15 (seeds: 5)
- Total windows: 150
- Mean net Sharpe: -22.765930
- Mean net return: -0.558011
- Mean net ann vol: 2.330684
- Mean max DD: 0.665028

## DEFLATED SHARPE RATIO (DSR)
- EVAL11_best: DSR = 0.000000 (significant)
- EVAL10_default: DSR = 0.000000 (significant)

## PROBABILITY OF BACKTEST OVERFITTING (PBO) — CSCV
- Method: CSCV (k=8, combinations=16)
- Overall PBO: 0.5000
- EVAL11_best: PBO = 0.4688
- EVAL10_default: PBO = 0.5234

## MULTIPLE-TESTING CORRECTION (Benjamini–Hochberg, FDR=0.1)
- EVAL11_best: DSR (p-proxy) = 0.000000, BH threshold = 0.050000, REJECTED (survives)
- EVAL10_default: DSR (p-proxy) = 0.000000, BH threshold = 0.100000, REJECTED (survives)
- Surviving configs: ['EVAL11_best', 'EVAL10_default']

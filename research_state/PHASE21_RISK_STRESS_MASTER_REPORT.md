# PHASE21_RISK_STRESS_MASTER_REPORT
Timestamp (UTC): 2026-11-01T14:21:11.160256Z
Campaign ID: p21_camp_303d76c9
Seed: 42
Symbols: BTC, ETH, SOL, XRP, ADA
Venues: deribit, okx, binance, bybit, bitget
Paper-only: True
Git SHA: 303d76c9e1995b004a91785e361b552ce110544a

## Gate Status: YELLOW
## Agg Passed: False | Stress Breaches: 0 | Pretrade Blocked: 6 | Monitor Healthy: False | Attr Lines: 100

## Components
- risk_aggregator: src/risk/phase21_risk_aggregator.py
- stress_tester: src/risk/phase21_stress_tester.py
- pre_trade_validator: src/risk/phase21_pre_trade_validator.py
- risk_monitor: src/monitoring/phase21_risk_monitor.py
- risk_attribution: src/analytics/phase21_risk_attribution.py
- campaign_script: scripts/run_phase21_risk_stress_campaign.py
- tests: tests/test_phase21_risk_stress.py

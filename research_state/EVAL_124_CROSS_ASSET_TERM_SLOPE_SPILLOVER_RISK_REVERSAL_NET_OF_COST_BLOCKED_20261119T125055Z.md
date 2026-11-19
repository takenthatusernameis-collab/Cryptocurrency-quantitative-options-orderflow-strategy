# EVAL_124_CROSS_ASSET_TERM_SLOPE_SPILLOVER_RISK_REVERSAL_NET_OF_COST_BLOCKED — cross-asset term_slope spillover -> risk reversal net-of-cost: BELOW FLOOR

- Generated: `2026-11-19T12:50:55Z`
- Task: `EVAL124-CROSS-ASSET-TERM-SLOPE-SPILLOVER-RISK-REVERSAL-NET-OF-COST`
- Verdict: **BLOCKED**
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`

The capture does not meet the sealed EVAL-64 feasible floor; no net-of-cost verdict is emitted (never a NO-GO). Do NOT weaken the EVAL-64 floor, do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.

## Errors

- BTC<-ETH::term_slope::bar60.0: AttributeError("module 'scripts.eval61_orderflow_realized_vol_net_of_cost' has no attribute '_expiry_date'")
- BTC<-ETH::term_slope::bar300.0: AttributeError("module 'scripts.eval61_orderflow_realized_vol_net_of_cost' has no attribute '_expiry_date'")
- ETH<-BTC::term_slope::bar60.0: AttributeError("module 'scripts.eval61_orderflow_realized_vol_net_of_cost' has no attribute '_expiry_date'")
- ETH<-BTC::term_slope::bar300.0: AttributeError("module 'scripts.eval61_orderflow_realized_vol_net_of_cost' has no attribute '_expiry_date'")

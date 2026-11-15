# EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED — Real Deribit options surface x options order flow net-of-cost falsification

- Generated: `2026-11-15T16:50:18Z`
- Task: `EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor

| underlying | snaps | surf inst | 5m bars | trades | of inst | span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|
| BTC | 289 | 102 | 289 | 4688 | 99 | 86262 | 288 | True |
| ETH | 289 | 102 | 289 | 3122 | 101 | 86204 | 287 | True |

## Per-underlying (best config)

| underlying | configs | best Sharpe | best config | any pass |
|---|---|---|---|---|
| BTC | 18 | -0.7473 | continuous_zscore::call_minus_put::bar300.0 | False |
| ETH | 18 | -1.6028 | sign_agreement::imbalance::bar300.0 | False |

## Pooled

- Overall PBO: 0.6389
- BH-FDR rejected: ['BTC::sign_agreement::imbalance::bar60.0', 'BTC::sign_agreement::notional_imbalance::bar60.0', 'BTC::sign_agreement::call_minus_put::bar60.0', 'BTC::regime_filter::imbalance::bar60.0', 'BTC::regime_filter::notional_imbalance::bar60.0', 'BTC::regime_filter::call_minus_put::bar60.0', 'BTC::regime_filter::call_minus_put::bar300.0', 'BTC::continuous_zscore::imbalance::bar60.0', 'BTC::continuous_zscore::notional_imbalance::bar60.0', 'BTC::continuous_zscore::call_minus_put::bar60.0', 'ETH::sign_agreement::imbalance::bar60.0', 'ETH::sign_agreement::notional_imbalance::bar60.0', 'ETH::sign_agreement::call_minus_put::bar60.0', 'ETH::regime_filter::imbalance::bar60.0', 'ETH::regime_filter::notional_imbalance::bar60.0', 'ETH::regime_filter::call_minus_put::bar60.0', 'ETH::continuous_zscore::imbalance::bar60.0', 'ETH::continuous_zscore::notional_imbalance::bar60.0', 'ETH::continuous_zscore::call_minus_put::bar60.0', 'BTC::continuous_zscore::imbalance::bar300.0', 'BTC::continuous_zscore::notional_imbalance::bar300.0', 'ETH::continuous_zscore::call_minus_put::bar300.0', 'ETH::regime_filter::call_minus_put::bar300.0', 'BTC::sign_agreement::imbalance::bar300.0', 'BTC::sign_agreement::notional_imbalance::bar300.0', 'ETH::sign_agreement::call_minus_put::bar300.0', 'ETH::continuous_zscore::imbalance::bar300.0', 'ETH::continuous_zscore::notional_imbalance::bar300.0', 'BTC::regime_filter::imbalance::bar300.0', 'BTC::regime_filter::notional_imbalance::bar300.0', 'ETH::regime_filter::imbalance::bar300.0', 'ETH::regime_filter::notional_imbalance::bar300.0']
- All underlyings pass: False

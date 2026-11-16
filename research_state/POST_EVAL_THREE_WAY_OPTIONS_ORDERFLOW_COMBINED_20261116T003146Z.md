# POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED — real three-way options+orderflow net-of-cost falsification

- Generated: `2026-11-16T00:31:46Z`
- Task: `POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor

| underlying | snaps | surf inst | 5m bars | deribit trades | of inst | deribit span s | okx trades | okx span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 289 | 104 | 289 | 3068 | 99 | 86314 | 356839 | 86398 | 288 | True |
| ETH | 289 | 276 | 289 | 4289 | 238 | 86296 | 231050 | 86393 | 288 | True |

## Per-underlying (best config)

| underlying | configs | best Sharpe | best config | any pass |
|---|---|---|---|---|
| BTC | 18 | -1.1388 | three_way_continuous_zscore::call_minus_put::bar300.0 | False |
| ETH | 18 | -1.4729 | three_way_continuous_zscore::call_minus_put::bar300.0 | False |

## Pooled

- Overall PBO: 0.7500
- BH-FDR rejected: ['BTC::three_way_sign_agreement::imbalance::bar60.0', 'BTC::three_way_sign_agreement::notional_imbalance::bar60.0', 'BTC::three_way_sign_agreement::call_minus_put::bar60.0', 'BTC::three_way_regime_filter::imbalance::bar60.0', 'BTC::three_way_regime_filter::imbalance::bar300.0', 'BTC::three_way_regime_filter::notional_imbalance::bar60.0', 'BTC::three_way_regime_filter::notional_imbalance::bar300.0', 'BTC::three_way_regime_filter::call_minus_put::bar60.0', 'BTC::three_way_regime_filter::call_minus_put::bar300.0', 'BTC::three_way_continuous_zscore::imbalance::bar60.0', 'BTC::three_way_continuous_zscore::notional_imbalance::bar60.0', 'BTC::three_way_continuous_zscore::call_minus_put::bar60.0', 'ETH::three_way_sign_agreement::imbalance::bar60.0', 'ETH::three_way_sign_agreement::notional_imbalance::bar60.0', 'ETH::three_way_sign_agreement::call_minus_put::bar60.0', 'ETH::three_way_regime_filter::imbalance::bar60.0', 'ETH::three_way_regime_filter::notional_imbalance::bar60.0', 'ETH::three_way_regime_filter::call_minus_put::bar60.0', 'ETH::three_way_regime_filter::call_minus_put::bar300.0', 'ETH::three_way_continuous_zscore::imbalance::bar60.0', 'ETH::three_way_continuous_zscore::imbalance::bar300.0', 'ETH::three_way_continuous_zscore::notional_imbalance::bar60.0', 'ETH::three_way_continuous_zscore::notional_imbalance::bar300.0', 'ETH::three_way_continuous_zscore::call_minus_put::bar60.0', 'BTC::three_way_sign_agreement::call_minus_put::bar300.0', 'BTC::three_way_sign_agreement::imbalance::bar300.0', 'BTC::three_way_sign_agreement::notional_imbalance::bar300.0', 'ETH::three_way_regime_filter::imbalance::bar300.0', 'ETH::three_way_regime_filter::notional_imbalance::bar300.0', 'BTC::three_way_continuous_zscore::imbalance::bar300.0', 'BTC::three_way_continuous_zscore::notional_imbalance::bar300.0', 'ETH::three_way_sign_agreement::call_minus_put::bar300.0', 'ETH::three_way_sign_agreement::imbalance::bar300.0', 'ETH::three_way_sign_agreement::notional_imbalance::bar300.0']
- All underlyings pass: False

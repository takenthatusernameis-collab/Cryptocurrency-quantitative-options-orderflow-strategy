# EVAL_51_OPTIONS_ORDERFLOW_COMBINED — Real Deribit options order flow net-of-cost falsification

- Generated: `2026-11-15T15:20:05Z`
- Task: `EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH; per-underlying floor 2000 trades / 240 bars / 50 instruments / 79200s)

## Per-underlying (best config)

| underlying | configs | best Sharpe | best config | any pass |
|---|---|---|---|---|
| BTC | 6 | -1.8644 | imbalance::bar5.0 | False |
| ETH | 6 | -1.8973 | call_minus_put::bar15.0 | False |

## Per-config (Sharpe / max-DD / perm p / CI / breach / pass)

- BTC imbalance bar5.0: Sharpe -1.8644 / DD 0.0486 / p 0.0549 / CI [-3.553, -0.111] / breach False / pass False
- BTC imbalance bar15.0: Sharpe -2.0417 / DD 0.0566 / p 0.0240 / CI [-3.913, -0.229] / breach False / pass False
- BTC notional_imbalance bar5.0: Sharpe -1.8644 / DD 0.0486 / p 0.0549 / CI [-3.553, -0.111] / breach False / pass False
- BTC notional_imbalance bar15.0: Sharpe -2.0417 / DD 0.0566 / p 0.0240 / CI [-3.913, -0.229] / breach False / pass False
- BTC call_minus_put bar5.0: Sharpe -2.1246 / DD 0.0423 / p 0.0230 / CI [-3.607, -0.518] / breach False / pass False
- BTC call_minus_put bar15.0: Sharpe -2.3981 / DD 0.0591 / p 0.0110 / CI [-4.419, -0.600] / breach False / pass False
- ETH imbalance bar5.0: Sharpe -2.2850 / DD 0.0607 / p 0.0140 / CI [-4.063, -0.602] / breach False / pass False
- ETH imbalance bar15.0: Sharpe -2.0905 / DD 0.0576 / p 0.0250 / CI [-3.906, -0.216] / breach False / pass False
- ETH notional_imbalance bar5.0: Sharpe -2.2850 / DD 0.0607 / p 0.0140 / CI [-4.063, -0.602] / breach False / pass False
- ETH notional_imbalance bar15.0: Sharpe -2.0906 / DD 0.0576 / p 0.0250 / CI [-3.906, -0.216] / breach False / pass False
- ETH call_minus_put bar5.0: Sharpe -2.0845 / DD 0.0441 / p 0.0190 / CI [-3.912, -0.354] / breach False / pass False
- ETH call_minus_put bar15.0: Sharpe -1.8973 / DD 0.0502 / p 0.0400 / CI [-3.673, -0.157] / breach False / pass False

## Pooled

- Overall PBO: 0.5000
- BH-FDR rejected: ['ETH::imbalance::bar5.0', 'ETH::notional_imbalance::bar5.0', 'ETH::call_minus_put::bar5.0', 'BTC::call_minus_put::bar5.0', 'BTC::imbalance::bar15.0', 'BTC::notional_imbalance::bar15.0', 'ETH::imbalance::bar15.0', 'ETH::notional_imbalance::bar15.0', 'ETH::call_minus_put::bar15.0', 'BTC::imbalance::bar5.0', 'BTC::notional_imbalance::bar5.0']
- All underlyings pass: False

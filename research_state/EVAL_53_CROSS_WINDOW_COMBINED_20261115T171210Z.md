# EVAL_53_CROSS_WINDOW_COMBINED — EVAL-53 cross-window surface x options order-flow replication

- Generated: `2026-11-15T17:12:10Z`
- Task: `INIT-2026-11-15T17:12:10Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION`
- Verdict: **NO-GO CONFIRMED (PASS)** (GO: False)
- Floor OK window A: True | window B: True
- Pooled PBO window A: 0.6389 | window B: 0.5556
- Replicated configs: 0 (none)
- Replicated underlyings: none

## Per-underlying floor — window A (sealed eval52)

- BTC: snaps 289 / surf inst 102 / 5m bars 289 / trades 4688 / of inst 99 / span 86262s / common 5m 288 / ok True
- ETH: snaps 289 / surf inst 102 / 5m bars 289 / trades 3122 / of inst 101 / span 86204s / common 5m 287 / ok True

## Per-underlying floor — window B (new capture)

- BTC: snaps 289 / surf inst 102 / 5m bars 289 / trades 4547 / of inst 99 / span 86036s / common 5m 287 / ok True
- ETH: snaps 289 / surf inst 102 / 5m bars 289 / trades 3066 / of inst 101 / span 85928s / common 5m 287 / ok True

## Per-underlying best — window A

- BTC: 18 configs, best Sharpe -0.7473, BTC::continuous_zscore::call_minus_put::bar300.0, any pass False
- ETH: 18 configs, best Sharpe -1.6028, ETH::sign_agreement::imbalance::bar300.0, any pass False

## Per-underlying best — window B

- BTC: 18 configs, best Sharpe -0.7315, BTC::continuous_zscore::call_minus_put::bar300.0, any pass False
- ETH: 18 configs, best Sharpe -1.7099, ETH::sign_agreement::imbalance::bar300.0, any pass False

# EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION — options order-flow toxicity -> signal-timed delta-hedged ATM straddle (correct mark-path P&L) net-of-cost falsification

- Generated: `2026-11-16T03:21:05Z`
- Task: `INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL`
- Hypothesis: Real options order-flow toxicity predicts subsequent realized volatility, and a signal-timed delta-hedged ATM straddle measured with the correct mark-path net-of-cost P&L is tradable for the BTC/ETH perpetual on real, synchronized data.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Supersedes: EVAL-61 (P&L artifact: un-normalized dollar P&L treated as returns -> max-DD=1.0 -> false NO-GO; EVAL-62 uses EVAL-57 correct mark-path ret=(gross-cost)/S)

## Pre-declared protocol

- Tox signals: ['tox', 'imbalance']
- Position: side_k = sign(tox_z_k); exposure_k = clip(|tox_z_k|, 0, size_cap); causal decision at bar k; delta-hedged in the perp
- Straddle: front-expiry common strike nearest spot, both legs priced from real marks (EVAL-57 _pick_straddle_quotes/_iv_and_greeks, reused)
- P&L per bar: dOption_k = side_k*exposure_k*(mark_{k+1}-mark_k)*S_k; gross_k = dOption_k + hedge_k*dS_k; ret_k = (gross_k - cost_k)/S_k
- Bar grid (s): [60.0, 300.0]
- z-window: 20; cost: net-of-cost: hedge_fee_bps on |Δhedge|*S; half real 2-leg spread at entry/exit; full spread on side flip (identical to EVAL-57)
- Stats: perm 1000 paired / bootstrap 1000 block 2 / PBO k=4 / BH-FDR alpha 0.1 / seed 42
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower > 0, and pooled PBO < 0.5; else NO-GO.

## Heavy-work floor (must be met to seal a verdict)

- min surface snapshots/underlying: 100
- min bars/underlying: 240
- min instruments/underlying: 50
- min Deribit options-venue trades/underlying: 2000
- min span seconds/underlying: 79200.0
- min common 5m bars/underlying: 240
- min underlyings: 2

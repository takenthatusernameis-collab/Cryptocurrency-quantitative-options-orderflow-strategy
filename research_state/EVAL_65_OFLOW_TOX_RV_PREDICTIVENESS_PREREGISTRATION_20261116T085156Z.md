# EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION — options order-flow toxicity -> realized-vol predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-16T08:51:56Z`
- Task: `EVAL65-OFLOW-TOX-RV-PREDICTIVENESS`
- Hypothesis: The causal options order-flow toxicity signal (tox / signed-aggressor imbalance) has a positive monotone (Spearman rank) relationship with subsequent forward realized volatility on the BTC/ETH perpetual, independent of any trading wrapper; tested on the already-acquired real 7d captures at the EVAL-64 feasible floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval63`
- Extends: EVAL-62/EVAL-64 (identical causal toxicity signal + spot series via sealed build_states; feasible floor reused verbatim from EVAL-64; no P&L, no wrapper)

## Pre-declared protocol

- Tox signals: ['tox', 'imbalance']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: signal_z_k = expanding-zscore of per-bar options order-flow toxicity (tox) / signed-aggressor imbalance (imbalance), reused verbatim from EVAL-61/EVAL-62 (causal, end-of-bar k)
- Target: rv_{k+1..k+H} = sqrt(mean(log-return^2)) over the next H perp 1m/5m bars (forward realized vol, strictly after the decision at k)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, rv_forward_k)
- Stats: perm 1000 (directional (H1: IC>0), shuffle realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)

- min surface snapshots/underlying: 1000
- min surface 5m bars/underlying: 1000
- min Deribit option trades/underlying: 2000
- min perp 5m bars/underlying: 1000
- min perp span seconds/underlying: 300000.0
- min common 5m bars/underlying: 240
- min underlyings: 2

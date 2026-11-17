# EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION — underlying order-flow -> realized-vol / signed-return predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-17T02:37:55Z`
- Task: `EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS`
- Hypothesis: The causal underlying (OKX perp) order-flow imbalance / toxicity has a positive monotone (Spearman rank) relationship with subsequent forward realized volatility and signed return, independent of any trading wrapper; tested on the already-acquired real on-disk captures at the pre-registered perp-tape floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-65 (identical Spearman rank-IC statistic) but a different, on-charter signal source: the underlying perp tape rather than the options tape; no options surface needed; no new acquisition

## Pre-declared protocol

- Signals: ['tox', 'imbalance']
- Signal -> target pairs: [['tox', 'rv'], ['imbalance', 'rv'], ['imbalance', 'signed_return']]
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar signed-aggressor order-flow imbalance (buy_vol - sell_vol)/(buy_vol + sell_vol) from real OKX perp trades, and its absolute (tox) variant, expanding-zscored end-of-bar k (reused e61.expanding_zscore)
- Target: over the next H perp bars: rv = sqrt(mean(log-return^2)); signed_return = sum(log-return) (strictly after the decision at k)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, target_forward_k)
- Stats: perm 1000 (directional (H1: IC>0), shuffle target series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered feasible floor (perp-tape; NOT the EVAL-64 floor)

- EVAL-70 measures a perp-tape order-flow signal, so it carries its own pre-registered floor (perp trades/candles/span). This is NOT a weakening of the EVAL-64 options-surface floor, which governs the EVAL-67/68/69 ladder and is reused verbatim there.
- min underlyings: 2
- min perp trades/underlying: 50000
- min perp candles/underlying: 1000
- min perp span seconds/underlying: 82000.0
- min perp 5m bars/underlying: 240

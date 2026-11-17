# EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_PREREGISTRATION — options implied-vol surface -> realized-vol predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-17T04:15:13Z`
- Task: `EVAL71-SURFACE-IV-RV-PREDICTIVENESS`
- Hypothesis: The causal options implied-volatility surface (near-ATM IV level and put-call skew, reconstructed from the real Deribit option trade tape) has a positive monotone (Spearman rank) relationship with subsequent forward realized volatility of the BTC/ETH perpetual, independent of any trading wrapper; tested on the already-acquired real on-disk captures at the pre-registered trade-tape IV floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-65 (identical Spearman rank-IC statistic) but a different, on-charter signal source: the options *surface* (trade-tape IV) rather than the options *order-flow* tape; no new acquisition

## Pre-declared protocol

- Surface signals: ['atm_iv', 'skew']
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar near-ATM implied-vol surface from the real Deribit option trade tape: atm_iv = amount-weighted mean iv of near-ATM trades (|strike/spot-1|<=atm_band) over the trailing window; skew = mean(put iv) - mean(call iv) over the same trades; both forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore)
- Target: rv = sqrt(mean(log-return^2)) over the next H perp bars (forward realized vol, strictly after the decision at k)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, rv_forward_k)
- Stats: perm 1000 (directional (H1: IC>0), shuffle realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered feasible floor (trade-tape IV; NOT the EVAL-64 floor)

- EVAL-71 measures a trade-tape implied-vol surface signal, so it carries its own pre-registered floor (option trades / near-ATM trades / perp candles / span). This is NOT a weakening of the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is reused verbatim there.
- min underlyings: 2
- min option trades/underlying: 1000
- min near-ATM option trades/underlying: 400
- min perp candles/underlying: 1000
- min perp span seconds/underlying: 82000.0

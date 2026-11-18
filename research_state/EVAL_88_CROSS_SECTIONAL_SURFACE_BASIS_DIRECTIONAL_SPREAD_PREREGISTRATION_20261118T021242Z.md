# EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_PREREGISTRATION — cross-sectional options implied-vol surface basis -> relative *direction* predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-18T02:12:42Z`
- Task: `EVAL88-CROSS-SECTIONAL-SURFACE-BASIS-DIRECTIONAL-SPREAD`
- Hypothesis: The causal cross-sectional options implied-volatility surface basis (BTC-vs-ETH relative near-ATM IV / put-call skew, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent relative *direction* (BTC-minus-ETH forward signed return spread): relative implied-vol richness mean-reverts in direction. Tested on the already-acquired real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-77 (same cross-sectional BTC-vs-ETH surface basis and aligned common-bar reconstruction, reused verbatim) and EVAL-71 (surface bars + expanding z-score) but a DISTINCT target: the forward relative *direction* (signed return spread), not the relative RV *magnitude*; and EVAL-81 (order-flow -> own signed return) is single-asset order-flow, not the cross-sectional surface; no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_z_k = expanding_z( signal[ETH](k) - signal[BTC](k) )
- Target: y_k = mean_logret[BTC](k+1..k+H) - mean_logret[ETH](k+1..k+H) (forward relative direction / signed return spread)
- Surface signals: ['atm_iv', 'skew']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar near-ATM implied-vol surface (EVAL-71 build_surface_bars) for BTC and ETH: atm_iv = amount-weighted mean iv of near-ATM trades; skew = mean(put iv) - mean(call iv); the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore via EVAL-77)
- Target detail: forward relative direction = mean per-bar log-return of BTC minus that of ETH over the next H perp bars, computed per underlying on the common aligned bar grid (strictly after the decision at bar k)
- Statistic: Spearman rank correlation IC = rho(rel_z_k, y_k) over the common aligned bar-ends (H1: IC > 0, ETH richness predicts BTC outperforms ETH — relative-value directional mean reversion)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the relative-return spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if at least one config (surface signal x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- EVAL-88 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused verbatim, neither weakened) with a cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

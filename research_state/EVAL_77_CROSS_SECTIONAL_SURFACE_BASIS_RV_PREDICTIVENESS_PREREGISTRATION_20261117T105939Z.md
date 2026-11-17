# EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_PREREGISTRATION — cross-sectional options implied-vol surface basis -> relative realized-vol predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-17T10:59:39Z`
- Task: `EVAL77-CROSS-SECTIONAL-SURFACE-BASIS-RV`
- Hypothesis: The causal cross-sectional options implied-volatility surface basis (BTC-vs-ETH relative near-ATM IV / put-call skew, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent relative realized volatility (BTC-minus-ETH forward RV spread): relative implied-vol richness mean-reverts. Tested on the already-acquired real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71 / EVAL-73 / EVAL-74 (identical Spearman rank-IC statistic and surface reconstruction) but a different, on-charter signal family: the *cross-sectional* BTC-vs-ETH implied-vol basis rather than a single-underlying level/skew or term structure; no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_k = signal[ETH](k) - signal[BTC](k)
- Target: spread_k = rv[BTC](k+1..k+H) - rv[ETH](k+1..k+H)
- Surface signals: ['atm_iv', 'skew']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar near-ATM implied-vol surface (EVAL-71 build_surface_bars) for BTC and ETH: atm_iv = amount-weighted mean iv of near-ATM trades; skew = mean(put iv) - mean(call iv); the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore)
- Target detail: rv = sqrt(mean(log-return^2)) over the next H perp bars, computed per underlying on the common aligned bar grid; target = rv[BTC] - rv[ETH] (relative realized vol)
- Statistic: Spearman rank correlation IC = rho(rel_z_k, spread_k) over the common aligned bar-ends (H1: IC > 0, relative richness mean-reverts)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the realized-vol spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if at least one config (surface signal x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- EVAL-77 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused verbatim, neither weakened) with a cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

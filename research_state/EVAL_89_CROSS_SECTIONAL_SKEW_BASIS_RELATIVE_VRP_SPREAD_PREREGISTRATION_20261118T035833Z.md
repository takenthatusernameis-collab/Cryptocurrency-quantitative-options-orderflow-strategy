# EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_PREREGISTRATION — cross-sectional put-call skew basis -> relative *VRP* spread predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-18T03:58:33Z`
- Task: `EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD`
- Hypothesis: The causal cross-sectional put-call skew basis (BTC-vs-ETH relative skew, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent relative *variance risk premium* spread (BTC-minus-ETH forward atm_iv - forward_RV): relative skew richness mean-reverts in VRP. Tested on the already-acquired real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-77 (same cross-sectional BTC-vs-ETH surface basis and aligned common-bar reconstruction, reused verbatim; skew basis) and EVAL-86 (forward VRP definition atm_iv - forward_RV, reused verbatim) but a DISTINCT target: the forward relative VRP *spread* (BTC minus ETH), not the relative RV spread (EVAL-77), not the relative return direction (EVAL-88), not own-asset VRP (EVAL-86); no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_z_k = expanding_z( skew[ETH](k) - skew[BTC](k) )
- Target: y_k = VRP_BTC(k) - VRP_ETH(k) with VRP_i(k) = atm_iv_i(k) - forward_RV_i(k+1..k+H) (forward relative variance risk premium spread)
- Surface signals: ['skew']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar put-call skew surface (EVAL-71 build_surface_bars) for BTC and ETH: skew = mean(put iv) - mean(call iv) over near-ATM trades; the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore via EVAL-77). The skew basis is used (not atm_iv) so the signal does not mechanically appear inside the target.
- Target detail: forward relative VRP = per underlying VRP = atm_iv at bar k minus forward realized vol sqrt(mean(log-return^2)) over the next H perp bars (strictly after the decision at bar k, EVAL-71 _forward_rv via EVAL-77 _rv_series), then BTC minus ETH on the common aligned bar grid
- Statistic: Spearman rank correlation IC = rho(rel_z_k, y_k) over the common aligned bar-ends (H1: IC > 0, ETH skew-richness predicts BTC carries the richer forward VRP — relative-value VRP mean reversion)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the relative-VRP spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if at least one config (skew basis x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- EVAL-89 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused verbatim, neither weakened) with a cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

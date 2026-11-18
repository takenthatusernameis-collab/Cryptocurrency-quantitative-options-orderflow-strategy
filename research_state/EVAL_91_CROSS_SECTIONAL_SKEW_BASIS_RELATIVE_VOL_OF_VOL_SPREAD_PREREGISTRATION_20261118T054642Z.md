# EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION — cross-sectional put-call SKEW basis -> relative *vol-of-vol* spread predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-18T05:46:42Z`
- Task: `EVAL91-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VOL-OF-VOL-SPREAD`
- Hypothesis: The causal cross-sectional put-call SKEW basis (BTC-vs-ETH relative put-call skew, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent relative *vol-of-vol* spread (BTC-minus-ETH forward std of squared log returns): relative skew richness precedes relatively more turbulent realized variance paths. Tested on the already-acquired real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-77 (same cross-sectional BTC-vs-ETH surface basis and aligned common-bar reconstruction, reused verbatim; skew basis) and EVAL-84 (forward vol-of-vol definition std(squared log returns), reused verbatim) but a DISTINCT target: the forward relative vol-of-vol *spread* (BTC minus ETH), not the relative RV spread (EVAL-77), not the relative return direction (EVAL-88), not the relative VRP spread (EVAL-89), not EVAL-90's atm_iv-basis relative vol-of-vol, not own-asset vol-of-vol (EVAL-84); no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_z_k = expanding_z( skew[ETH](k) - skew[BTC](k) )
- Target: y_k = Vov_BTC(k) - Vov_ETH(k) with Vov_i(k) = sqrt(mean((v_j - mean(v))^2)), v_j = r_j^2, r_j = log(close_j/close_{j-1}) over next H perp bars (forward relative vol-of-vol spread)
- Surface signals: ['skew']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar put-call skew surface (EVAL-71 build_surface_bars) for BTC and ETH; the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore via EVAL-77). The skew basis is used (distinct from EVAL-90's atm_iv basis); skew is not inside the vol-of-vol target.
- Target detail: forward relative vol-of-vol = per underlying vol-of-vol sqrt(mean((v_j - mean(v))^2)) with v_j = r_j^2 (squared log returns) over the next H perp bars (strictly after the decision at bar k, EVAL-84 definition on EVAL-77 aligned common closes), then BTC minus ETH on the common aligned bar grid
- Statistic: Spearman rank correlation IC = rho(rel_z_k, y_k) over the common aligned bar-ends (H1: IC > 0, ETH skew richness predicts BTC carries the richer forward vol-of-vol — relative turbulence)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the relative-vol-of-vol spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if at least one config (skew basis x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- EVAL-91 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused verbatim, neither weakened) with a cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

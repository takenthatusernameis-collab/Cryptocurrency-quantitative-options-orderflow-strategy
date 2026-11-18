# EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION — cross-sectional near-ATM IV basis -> relative *vol-of-vol* spread predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-18T04:48:40Z`
- Task: `EVAL90-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VOL-OF-VOL-SPREAD`
- Hypothesis: The causal cross-sectional near-ATM IV basis (BTC-vs-ETH relative near-ATM implied vol, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent relative *vol-of-vol* spread (BTC-minus-ETH forward std of squared log returns): relative iv richness precedes relatively more turbulent realized variance paths. Tested on the already-acquired real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-77 (same cross-sectional BTC-vs-ETH surface basis and aligned common-bar reconstruction, reused verbatim; atm_iv basis) and EVAL-84 (forward vol-of-vol definition std(squared log returns), reused verbatim) but a DISTINCT target: the forward relative vol-of-vol *spread* (BTC minus ETH), not the relative RV spread (EVAL-77), not the relative return direction (EVAL-88), not the relative VRP spread (EVAL-89), not own-asset vol-of-vol (EVAL-84); no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_z_k = expanding_z( atm_iv[ETH](k) - atm_iv[BTC](k) )
- Target: y_k = Vov_BTC(k) - Vov_ETH(k) with Vov_i(k) = sqrt(mean((v_j - mean(v))^2)), v_j = r_j^2, r_j = log(close_j/close_{j-1}) over next H perp bars (forward relative vol-of-vol spread)
- Surface signals: ['atm_iv']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar near-ATM implied vol surface (EVAL-71 build_surface_bars) for BTC and ETH; the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore via EVAL-77). The atm_iv basis is used (a vol level, not inside the vol-of-vol target), distinct from EVAL-89's skew basis.
- Target detail: forward relative vol-of-vol = per underlying vol-of-vol sqrt(mean((v_j - mean(v))^2)) with v_j = r_j^2 (squared log returns) over the next H perp bars (strictly after the decision at bar k, EVAL-84 definition on EVAL-77 aligned common closes), then BTC minus ETH on the common aligned bar grid
- Statistic: Spearman rank correlation IC = rho(rel_z_k, y_k) over the common aligned bar-ends (H1: IC > 0, ETH iv-richness predicts BTC carries the richer forward vol-of-vol — relative turbulence)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the relative-vol-of-vol spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if at least one config (atm_iv basis x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- EVAL-90 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused verbatim, neither weakened) with a cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

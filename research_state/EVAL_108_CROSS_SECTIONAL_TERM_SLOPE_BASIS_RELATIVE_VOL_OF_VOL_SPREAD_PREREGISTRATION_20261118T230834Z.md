# EVAL_108_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION — cross-sectional term-slope basis -> relative *vol-of-vol* spread predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-18T23:08:34Z`
- Task: `EVAL108-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-VOL-OF-VOL-SPREAD`
- Hypothesis: The causal cross-sectional options implied-vol term-slope basis (BTC-vs-ETH relative near-to-far ATM IV term slope, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent relative *vol-of-vol* spread (BTC-minus-ETH forward std of squared log returns): relative term-slope richness predicts relative turbulence. Tested on the already-acquired real on-disk captures at the composed EVAL-74 term + EVAL-77 alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-74 (same causal term_slope reconstruction ``term_slope = (IV(near) - IV(far)) / (T_near - T_far)`` from the real Deribit option trade tape, reused verbatim) and EVAL-77 (same cross-sectional BTC-vs-ETH alignment and ``_relative_signal_series``, reused verbatim) and EVAL-84/90 (same forward vol-of-vol definition, reused verbatim) but a DISTINCT cell: the *cross-sectional term-slope basis* (not the single-underlying term_slope of EVAL-84/96/99/104, not the cross-sectional atm_iv basis of EVAL-90, not the cross-sectional term-ratio basis of EVAL-107, not the cross-sectional tail-asymmetry basis of EVAL-106) with the forward relative *vol-of-vol* spread (not the relative tail-asymmetry spread of EVAL-106, not the relative RV spread of EVAL-93); no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_z_k = expanding_z( term_slope[ETH](k) - term_slope[BTC](k) )
- Target: y_k = Vov_BTC(k) - Vov_ETH(k) with Vov_i(k) = sqrt(mean((v_j - mean(v))^2)), v_j = r_j^2, r_j = log(close_j/close_{j-1}) over next H perp bars (forward relative vol-of-vol spread)
- Term signals: ['term_slope']
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Min trades per expiry bucket: 5
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar implied-vol term slope from the real Deribit option trade tape (EVAL-74 ``_term_bars``): near-ATM trades grouped by expiry; term_slope = (IV(near) - IV(far)) / (T_near - T_far); the term_slope field is overlaid by bar_open_ms onto EVAL-77's common aligned cross-section; the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k (reused e77._relative_signal_series / e61.expanding_zscore).
- Target detail: forward relative vol-of-vol = per underlying vol-of-vol sqrt(mean((v_j - mean(v))^2)) with v_j = r_j^2 (squared log returns) over the next H perp bars (strictly after the decision at bar k, EVAL-84/90 verbatim), then BTC minus ETH on the common aligned bar grid
- Statistic: Spearman rank correlation IC = rho(rel_z_k, y_k) over the common aligned bar-ends (H1: IC > 0, ETH term-slope-richness predicts BTC subsequently carries the richer forward vol-of-vol — relative turbulence)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the relative vol-of-vol spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH floors satisfied, at least one config (term_slope basis x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-74 term both underlyings + EVAL-77 alignment)

- EVAL-108 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-74 term-structure floor (EVAL-71 surface floor + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each, and >= MIN_BARS_WITH_TERM bars carrying a term signal; applied to BOTH BTC and ETH, reused verbatim, neither weakened) with the sealed EVAL-77 cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal surface bar on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min distinct near-ATM expiries: 2
- Min trades per expiry bucket: 5
- Min bars with a term signal: 40
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

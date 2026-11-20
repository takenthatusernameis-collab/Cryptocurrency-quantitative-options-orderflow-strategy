# EVAL_126_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_PREREGISTRATION — cross-sectional term-slope basis -> forward relative realized return kurtosis spread predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-20T20:09:53Z`
- Task: `EVAL126-CROSS-SECTIONAL-TERM-SLOPE-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD`
- Hypothesis: The causal cross-sectional options implied-vol term-slope basis (BTC-vs-ETH relative near-to-far ATM IV term slope, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent forward relative realized return kurtosis spread (kurtosis[ETH] - kurtosis[BTC] over the next H perp log returns): relative term-slope richness predicts relative return kurtosis. Tested on the already-acquired real on-disk captures at the composed EVAL-74 term + EVAL-77 alignment floor.
- Capture dir: `/home/runner/work/_temp/kilo-tmp/tmpzjb57v4j/captures`
- Extends: EVAL-118 (same causal term_slope reconstruction ``term_slope = IV(near) - IV(far)`` from the real Deribit option trade tape, reused verbatim) and EVAL-77 (same cross-sectional BTC-vs-ETH alignment and ``_relative_signal_series``, reused verbatim) and EVAL-125 (same forward return-kurtosis target, reused verbatim) but a DISTINCT cell: the *cross-sectional term-slope basis* with forward *relative realized return kurtosis spread*; no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_z_k = expanding_z( term_slope[ETH](k) - term_slope[BTC](k) )
- Target: spread_k = forward_kurtosis[ETH](k+1..k+H) - forward_kurtosis[BTC](k+1..k+H) with forward kurtosis = fourth standardized moment m4 / m2**2 of log returns over the next H perp bars (strictly after the decision at bar k, ``_forward_return_kurtosis`` verbatim)
- Term signals: ['term_slope']
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Min trades per expiry bucket: 5
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar implied-vol term slope from the real Deribit option trade tape (EVAL-74 ``_term_bars``): near-ATM trades grouped by expiry; term_slope = IV(near expiry) - IV(far expiry); the term_slope field is overlaid by bar_open_ms onto EVAL-77's common aligned cross-section; the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k (reused e77._relative_signal_series / e61.expanding_zscore).
- Target detail: forward relative realized return kurtosis spread: per underlying forward kurtosis = fourth standardized moment m4 / m2**2 of log returns over the next H perp bars (strictly after the decision at bar k, ``_forward_return_kurtosis`` verbatim), then ETH minus BTC on the common aligned bar grid
- Statistic: Spearman rank correlation IC = rho(rel_z_k, spread_k) over the common aligned bar-ends (H1: IC > 0, ETH term-slope-richness predicts ETH subsequently carries a richer forward return kurtosis spread relative to BTC)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the relative forward-return-kurtosis spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if at least one config (term_slope basis x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-74 term both underlyings + EVAL-77 alignment)

- EVAL-126 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-74 term-structure floor (EVAL-71 surface floor + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each, and >= MIN_BARS_WITH_TERM bars carrying a term signal; applied to BOTH BTC and ETH, reused verbatim, neither weakened) with the sealed EVAL-77 cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal surface bar on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min distinct near-ATM expiries: 2
- Min trades per expiry bucket: 5
- Min bars with a term signal: 40
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

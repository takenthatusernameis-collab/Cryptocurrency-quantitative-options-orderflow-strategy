# EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_PREREGISTRATION — cross-sectional term-ratio basis (ETH - BTC) -> forward relative realized return skewness spread (Spearman rank IC)

- Generated: `2026-11-19T06:16:07Z`
- Task: `EVAL120-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-RETURN-SKEWNESS-SPREAD`
- Hypothesis: The causal cross-sectional options implied-vol term-ratio basis (term_ratio_ETH - term_ratio_BTC, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent forward relative realized return skewness spread (skewness[ETH] - skewness[BTC] over the next H perp log returns), independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-77 surface basis floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-77 (cross-sectional surface basis atm_iv+skew -> forward realized-vol spread) and EVAL-105 (cross-sectional term-ratio basis -> relative tail-asymmetry spread) and EVAL-116 (cross-sectional skew basis -> relative return skewness spread): same Spearman rank-IC statistic and sealed signal/target reconstructions reused verbatim, but a distinct on-charter signal x target cell — the *cross-sectional term-ratio basis* (term_ratio_ETH - term_ratio_BTC) -> forward *relative realized return skewness spread*; no new acquisition

## Pre-declared protocol

- Term signals: ['term_ratio']
- Target: forward realized-return skewness = third standardized moment mean((r - mu)^3) / std^3 of log returns over the next H perp bars, computed per underlying on the common aligned bar grid; target = skewness[ETH] - skewness[BTC] (relative realized return skewness spread) — None
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar implied-vol term ratio from the real Deribit option trade tape (EVAL-74 ``_term_bars``): near-ATM trades grouped by expiry; term_ratio = IV(near expiry) / IV(far expiry) - 1; the term_ratio field is overlaid by bar_open_ms onto EVAL-77's common aligned cross-section; the relative series (ETH - BTC) is forward-filled then expanding-z-scored end-of-bar k (reused e77._relative_signal_series / e61.expanding_zscore).
- Statistic: Spearman rank correlation IC = rho(rel_z_k, spread_k) over the common aligned bar-ends (H1: IC > 0)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if at least one config (signal x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-77 surface basis, not the EVAL-64 ladder floor)

- EVAL-77 consumes both underlyings' trade-tape IV surfaces and both perp series. It composes the sealed EVAL-71 surface floor (applied to BOTH BTC and ETH, reused verbatim, neither weakened) with a cross-sectional alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min aligned common bars: 200
- Min usable pairs per config: 120

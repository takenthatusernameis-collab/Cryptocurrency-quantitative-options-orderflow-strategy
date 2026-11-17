# EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_PREREGISTRATION — EVAL-71 predictive-surface temporal stability (disjoint early/late split)

- Generated: `2026-11-17T05:32:37Z`
- Task: `EVAL73-SURFACE-IV-RV-STABILITY-SPLIT`
- Hypothesis: EVAL-71's predictive-surface GO (causal options implied-vol surface -> forward realized vol) is TEMPORALLY STABLE: the positive Spearman rank IC sign replicates across two DISJOINT temporal halves of the same real on-disk BTC/ETH captures, not an artifact of one period; tested at the sealed EVAL-71 floor plus a derived per-half adequacy floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71 (identical Spearman rank-IC statistic, identical surface signals / bar grid / horizons) but a different question: does EVAL-71's predictive-surface GO replicate across two DISJOINT temporal halves, or is it a one-period regime artifact?; no new acquisition

## Pre-declared protocol

- Surface signals: ['atm_iv', 'skew']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Split: each underlying capture is split into two DISJOINT temporal halves at the perp-candle midpoint (early ts < midpoint; late ts >= midpoint); the full-sample IC/permutation are EVAL-71 verbatim and each half carries its own Spearman rank IC (e65._spearman)
- Stability rule: a config is STABLE iff n_pairs in EACH half >= 30, IC_early > 0 and IC_late > 0, and the full-sample directional permutation p < 0.05
- Statistic: Spearman rank correlation IC = rho(signal_z_k, rv_forward_k); per-half IC via e65._spearman; full-sample IC + directional permutation via e71.evaluate_predictiveness
- Stats: perm 1000 (directional (H1: IC>0), shuffle realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, the config is STABLE (both half ICs > 0, each half >= min_half_pairs, full-sample directional permutation p < 0.05) and pooled BH-FDR rejects its full-sample p; else NO-GO CONFIRMED (PASS) -- EVAL-71's predictive surface GO does not replicate across the disjoint temporal split.

## Pre-registered feasible floor (EVAL-71 floor + per-half adequacy; NOT EVAL-64)

- EVAL-73 reuses the sealed EVAL-71 trade-tape IV floor verbatim on the full capture (NOT weakened) and additionally requires each disjoint early/late half to be independently analyzable (perp candles / near-ATM trades per half) -- a derived, stricter per-half adequacy floor. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- min underlyings: 2
- min perp candles/half: 300
- min near-ATM trades/half: 100
- min aligned pairs/half: 30

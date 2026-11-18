# EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_PREREGISTRATION — cross-sectional skew basis -> relative tail-asymmetry spread predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-18T23:18:11Z`
- Task: `EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD`
- Hypothesis: The causal cross-sectional options implied-vol put-call skew basis (BTC-vs-ETH relative near-ATM skew, reconstructed from the real Deribit option trade tapes) has a positive monotone (Spearman rank) relationship with the subsequent relative return-tail-asymmetry spread (BTC-minus-ETH forward tail-asymmetry spread): relative skew richness predicts relative tail asymmetry. Tested on the already-acquired real on-disk captures at the composed EVAL-71 surface + EVAL-77 alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-77 (same cross-sectional BTC-vs-ETH alignment and ``_relative_signal_series``, reused verbatim) and EVAL-85 (same forward return-tail-asymmetry target, reused verbatim) but a DISTINCT cell: the *cross-sectional skew basis* (not the single-underlying skew of EVAL-85, not the skew basis -> relative VRP of EVAL-89, not the skew basis -> relative vol-of-vol of EVAL-91, not the term basis -> relative tail asymmetry of EVAL-105/106) with the forward relative *tail-asymmetry* spread; no new acquisition

## Pre-declared protocol

- Cross-section: baseline `BTC`, relative `ETH`
- Relative signal: rel_z_k = expanding_z( skew[ETH](k) - skew[BTC](k) )
- Target: y_k = tail_asym_BTC(k) - tail_asym_ETH(k) with tail_asym_i(k) = (q95 - median) - (median - q05) over the next H perp log returns strictly after k (relative tail-asymmetry spread)
- Surface signals: ['skew']
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar near-ATM put-call skew (EVAL-71 ``build_surface_bars``: skew = mean(put iv) - mean(call iv) over near-ATM trades); the relative series (ETH - BTC) is forward-filled then expanding-zscored end-of-bar k on the EVAL-77 common aligned bar grid (reused e77._relative_signal_series / e61.expanding_zscore).
- Target detail: forward relative tail-asymmetry spread: per underlying tail_asym = (q95 - median) - (median - q05) over the next H perp log returns (strictly after the decision at bar k, EVAL-85 ``_forward_return_tail_asym`` verbatim), then BTC minus ETH on the common aligned bar grid
- Statistic: Spearman rank correlation IC = rho(rel_z_k, y_k) over the common aligned bar-ends (H1: IC > 0, relatively positive ETH-minus-BTC skew basis predicts BTC subsequently carries a relatively richer forward tail-asymmetry spread)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the relative tail-asymmetry spread) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH floors satisfied, at least one config (skew basis x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 surface both underlyings + EVAL-77 alignment)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s) PLUS the sealed EVAL-77 cross-sectional alignment floor (>= min_aligned_common_bars=200 aligned common bar-ends on the coarsest grid), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120

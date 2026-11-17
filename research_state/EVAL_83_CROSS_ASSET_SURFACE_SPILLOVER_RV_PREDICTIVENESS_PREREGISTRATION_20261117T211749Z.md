# EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_PREREGISTRATION — cross-asset options surface lead-lag spillover -> subsequent forward realized volatility (wrapper-free Spearman rank IC)

- Generated: `2026-11-17T21:17:49Z`
- Task: `EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS`
- Hypothesis: The causal options implied-volatility surface of one crypto (EVAL-71 near-ATM IV level / put-call skew, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent forward realized volatility of the OTHER crypto, reconstructed from the real Deribit option trade tape and real perp candles of both underlyings, beyond the target's own surface (partial-over-own-surface IC > 0). Tested on the already-acquired real on-disk captures at the composed EVAL-71 + cross-asset common-bar floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71/73 (own-asset surface -> own-asset forward RV) and EVAL-77 (contemporaneous cross-sectional basis -> RV spread): the same Spearman rank-IC statistic and all sealed signal reconstructions reused verbatim, but a distinct, on-charter signal x target cell — the *cross-asset temporal* leader surface vs the *target* forward RV; no new acquisition

## Pre-declared protocol

- Leader surface signals: ['atm_iv', 'skew']
- Target: forward_rv — target forward realized volatility = sqrt(mean(r^2)) over the TARGET's next H perp bars (strictly after the decision at bar k); the subsequent realized vol of the OTHER crypto
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal options-implied-vol surface (near-ATM IV level / put-call skew) z (EVAL-71 build_surface_bars + EVAL-61 expanding_zscore, end-of-bar k)
- Statistic: Spearman rank correlation IC = rho(leader_signal_z_k, target_fwd_rv_k) over common bar timestamps (H1: IC > 0); plus a partial Spearman rho(., . | target own surface z) as an incremental-over-own-surface control
- Stats: perm 1000 (directional (H1: IC>0), shuffle the target forward-RV series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 100

## Pre-declared GO bar

GO only if, for EACH target underlying, at least one incoming-spillover config (from the other asset; bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, partial-over-own-surface IC > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS). Per-direction detail is reported so a one-directional spillover is not misread as bidirectional.

## Pre-registered composed floor (EVAL-71 surface + cross-asset common-bar)

- EVAL-83 consumes each underlying's causal options-surface series (real option trade tape for the IV surface, real perp candles for forward RV) and requires cross-asset overlap. It composes the sealed EVAL-71 surface floor (applied to EACH underlying, reused verbatim, neither weakened) with a cross-asset common-bar floor (>= min_common_bars_per_pair common bar timestamps between each ordered pair on the coarser 300 s grid). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min common bars per ordered pair: 150
- Min usable pairs per config: 100

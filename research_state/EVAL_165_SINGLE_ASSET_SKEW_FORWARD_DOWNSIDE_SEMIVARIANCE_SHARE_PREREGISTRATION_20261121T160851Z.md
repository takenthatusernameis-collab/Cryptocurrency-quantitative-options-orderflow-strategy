# EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION — causal near-ATM implied-vol skew -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-21T16:08:51Z`
- Task: `EVAL165-SINGLE-ASSET-SKEW-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Hypothesis: The causal near-ATM implied-vol surface SKEW (near-dated near-ATM mean put IV minus mean call IV over the trailing 900s window, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent forward downside-semivariance share (downside variance as a fraction of total variance over the next H perp log returns) of the SAME underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-71 surface floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71 (own-asset surface atm_iv+skew -> own forward RV level) + EVAL-115 (single-asset atm_iv -> forward downside-semivariance share): same Spearman rank-IC statistic, signal reconstruction and target reused verbatim, but a distinct on-charter signal x target cell — near-ATM SKEW (surface) -> forward downside-semivariance share; no new acquisition

## Pre-declared protocol

- Surface signals: ['skew']
- Target: forward_downside_semivariance_share — forward downside-semivariance share = downside_semivariance / total_variance over the SAME underlying's next H perp log returns (strictly after the decision at bar k); downside semivariance = mean(min(r - mu, 0)^2), total variance = mean((r - mu)^2)
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal near-ATM implied-vol surface SKEW z (EVAL-71 build_surface_bars + EVAL-61 expanding_zscore, end-of-bar k)
- Statistic: Spearman rank correlation IC = rho(skew_z_k, downside_semivariance_share_k); directional permutation H1: IC > 0
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 100

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 surface, not the EVAL-64 ladder floor)

- EVAL-165 consumes each underlying's causal options-surface series (real option trade tape for the IV surface, real perp candles for forward returns) and reuses the sealed EVAL-71 surface floor for EACH underlying (verbatim, neither weakened). Below the composed floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min usable pairs per config: 100

# EVAL_166_SINGLE_ASSET_TERM_RATIO_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_PREREGISTRATION — single-asset term ratio -> forward downside-semivariance share predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-21T16:28:30Z`
- Task: `EVAL166-SINGLE-ASSET-TERM-RATIO-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Hypothesis: The causal options implied-volatility TERM RATIO (near-dated divided by far-dated near-ATM IV, minus one) has a positive monotone (Spearman rank) relationship with the subsequent forward downside-semivariance share (downside variance as a fraction of total variance over the next H perp log returns) of the same underlying's perpetual, independent of any trading wrapper; tested on the already-acquired real on-disk captures at the composed EVAL-74 term floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-74 (identical term_ratio signal via _term_bars) + EVAL-102 (single-asset term_ratio signal path verbatim) + EVAL-115/EVAL-165 (forward downside-semivariance-share target verbatim) + EVAL-65 (permutation / bootstrap inference) + EVAL-62 (FDR / seed / zwindow); distinct cell: single-asset term_ratio -> forward downside-semivariance share

## Pre-declared protocol

- Term signal: term_ratio
- Target: forward_downside_semivariance_share
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Min trades per expiry bucket: 5
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar implied-vol term structure from the real Deribit option trade tape: term_ratio = IV(near expiry)/IV(far expiry) - 1, forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore)
- Target detail: forward downside-semivariance share = downside_semivariance / total_variance over the SAME underlying's next H perp log returns (strictly after the decision at bar k); downside semivariance = mean(min(r - mu, 0)^2), total variance = mean((r - mu)^2)
- Statistic: Spearman rank correlation IC = rho(term_ratio_z_k, downside_share_forward_k); directional permutation H1: IC>0 (higher near/far IV ratio -> higher forward downside-semivariance share)
- Stats: perm 1000 (directional (H1: IC>0), shuffle downside-semivariance-share series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered feasible floor (EVAL-74 term floor; NOT EVAL-64)

- Reuses the sealed EVAL-74 term floor verbatim (EVAL-71 surface floor: min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each and >= MIN_BARS_WITH_TERM bars with a non-null term signal), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- min underlyings: 2
- min distinct near-ATM expiries: 2
- min trades per expiry bucket: 5
- min bars with a term signal: 40

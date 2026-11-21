# EVAL_161_SINGLE_ASSET_TERM_SLOPE_FORWARD_CVAR_PREREGISTRATION — single-asset term slope -> forward CVaR (expected shortfall) predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-21T09:44:13Z`
- Task: `EVAL161-SINGLE-ASSET-TERM-SLOPE-FORWARD-CVAR`
- Hypothesis: The causal options implied-volatility TERM SLOPE (near-dated minus far-dated near-ATM IV slope) has a positive monotone (Spearman rank) relationship with subsequent forward expected shortfall / CVaR of the signed log-return of the same underlying's perpetual, independent of any trading wrapper; tested on the already-acquired real on-disk captures at the composed EVAL-74 term floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-74 (identical term_slope signal via _term_bars) + EVAL-104 (single-asset term_slope signal path verbatim) + EVAL-65 (permutation / bootstrap inference) + EVAL-62 (FDR / seed / zwindow); distinct cell: single-asset term_slope -> forward CVaR (expected shortfall) of signed return

## Pre-declared protocol

- Term signal: term_slope
- Target: forward_cvar (CVaR alpha = 0.05)
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Min trades per expiry bucket: 5
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar implied-vol term structure from the real Deribit option trade tape: term_slope = IV(near expiry) - IV(far expiry) (vol points), forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore)
- Target detail: forward CVaR (expected shortfall) of signed log-returns = mean of the worst CVAR_ALPHA-tail of the next H perp log returns, strictly after the decision at bar k
- Statistic: Spearman rank correlation IC = rho(term_slope_z_k, cvar_forward_k); directional permutation H1: IC>0 (higher near-minus-far IV slope -> higher forward expected shortfall)
- Stats: perm 1000 (directional (H1: IC>0), shuffle CVaR series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / cvar_alpha 0.05

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered feasible floor (EVAL-74 term floor; NOT EVAL-64)

- Reuses the sealed EVAL-74 term floor verbatim (EVAL-71 surface floor: min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each and >= MIN_BARS_WITH_TERM bars with a non-null term signal), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- min underlyings: 2
- min distinct near-ATM expiries: 2
- min trades per expiry bucket: 5
- min bars with a term signal: 40

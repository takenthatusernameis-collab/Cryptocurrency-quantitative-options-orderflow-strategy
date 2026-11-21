# EVAL_172_SINGLE_ASSET_ATM_IV_FORWARD_VARIANCE_PREREGISTRATION — single-asset atm_iv -> forward realized return variance predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-21T21:14:58Z`
- Task: `EVAL172-SINGLE-ASSET-ATM-IV-FORWARD-VARIANCE`
- Hypothesis: The causal options implied-volatility surface ATM_IV level (near-dated near-ATM amount-weighted mean IV over the trailing 900s window) has a positive monotone (Spearman rank) relationship with subsequent forward realized return variance of the signed log-return of the same underlying's perpetual, independent of any trading wrapper; tested on the already-acquired real on-disk captures at the pre-registered EVAL-71 surface floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71 (identical atm_iv surface signal via build_surface_bars, 900s window) + EVAL-101 (single-asset atm_iv signal path verbatim) + EVAL-159 (forward realized return variance target verbatim) + EVAL-65 (permutation / bootstrap inference) + EVAL-62 (FDR / seed / zwindow); distinct cell: single-asset atm_iv -> forward realized return variance of signed return

## Pre-declared protocol

- Surface signal: atm_iv
- Target: forward_variance (forward realized return variance)
- Signal window (s): 900.0
- Near-ATM band: 0.05
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal per-bar near-ATM implied-vol surface level from the real Deribit option trade tape: atm_iv = amount-weighted mean iv of near-ATM trades (|strike/spot-1|<=atm_band) over the trailing 900s window, forward-filled then expanding-zscored end-of-bar k (reused e61.expanding_zscore)
- Target detail: forward realized return variance = mean((r - mean(r))**2) of the next H perp log returns, strictly after the decision at bar k; transcribed verbatim from sealed EVAL-159
- Statistic: Spearman rank correlation IC = rho(atm_iv_z_k, var_forward_k); directional permutation H1: IC>0 (higher near-ATM IV level -> higher forward realized variance)
- Stats: perm 1000 (directional (H1: IC>0), shuffle variance series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered feasible floor (EVAL-71 surface floor; NOT EVAL-64)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- min underlyings: 2
- min option trades/underlying: 1000
- min near-ATM option trades/underlying: 400
- min perp candles/underlying: 1000
- min perp span seconds/underlying: 82000.0

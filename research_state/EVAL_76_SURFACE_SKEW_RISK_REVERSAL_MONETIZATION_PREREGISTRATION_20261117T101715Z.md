# EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_PREREGISTRATION — surface skew -> signal-timed delta-hedged risk reversal net-of-cost monetization falsification

- Generated: `2026-11-17T10:17:15Z`
- Task: `EVAL76-SURFACE-SKEW-RISK-REVERSAL-MONETIZATION`
- Hypothesis: The causal options implied-volatility surface SKEW (EVAL-71 put-minus-call near-ATM IV skew) can be monetized net-of-cost by a signal-timed delta-hedged RISK REVERSAL (nearest OTM call + nearest OTM put) on the BTC/ETH perpetual, on the already-acquired real on-disk captures at the composed floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-72 / EVAL-75 (identical correct mark-path net-of-cost delta-hedged traded form) but a different, on-charter traded structure: a RISK REVERSAL (nearest OTM call + nearest OTM put) driven by the EVAL-71 surface SKEW rather than an ATM straddle driven by level/skew or term structure; no new acquisition

## Pre-declared protocol

- Surface signals: ['skew']
- Signal detail: skew = mean(put near-ATM iv) - mean(call near-ATM iv) over the trailing window (EVAL-71 helper, reused verbatim)
- Bar grid (s): [60.0, 300.0]
- Position: side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal decision at bar k; z_k = expanding-z of the causal EVAL-71 surface skew
- Traded form: risk reversal (front expiry; nearest OTM call = smallest strike > spot; nearest OTM put = largest strike < spot; IV backed out of the real mark via EVAL-57 helpers) with the EVAL-62 mark-path net-of-cost P&L on the signed long-call/short-put aggregate mark/delta: delta-hedge + half real 2-leg spread + hedge fee, spot-normalized
- Stats: perm 1000 (True) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / size_cap 1.0
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (both sealed floors; neither weakened)

- EVAL-76 consumes both the traded-instrument data (surface snapshots / perp candles / option trades; EVAL-61/62 floor) and the surface skew signal data (per-bar near-ATM option trade tape; EVAL-71 surface floor). Both sealed floors are reused verbatim and BOTH must pass; neither is weakened. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Composed of: ['EVAL-61/62 traded-instrument floor', 'EVAL-71 surface floor']
- Min underlyings: 2

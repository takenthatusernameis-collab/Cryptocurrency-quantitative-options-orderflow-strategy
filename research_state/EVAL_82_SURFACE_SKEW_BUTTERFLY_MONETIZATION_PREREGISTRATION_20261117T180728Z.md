# EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_PREREGISTRATION — surface -> signal-timed delta-hedged butterfly (smile-convexity) net-of-cost monetization falsification

- Generated: `2026-11-17T18:07:28Z`
- Task: `EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION`
- Hypothesis: The causal options implied-volatility surface (EVAL-71 near-ATM IV level and put-call skew) can be monetized net-of-cost by a signal-timed delta-hedged BUTTERFLY (long OTM call wing + long OTM put wing, short ATM body) on the BTC/ETH perpetual -- the smile-convexity traded form -- on the already-acquired real on-disk captures at the composed floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-72 (identical causal EVAL-71 surface signal set {atm_iv, skew} and identical correct EVAL-62 mark-path net-of-cost delta-hedged traded form) but a different, on-charter traded structure: a four-leg BUTTERFLY (long OTM call wing + long OTM put wing, short ATM body) that isolates smile CONVEXITY rather than the ATM straddle's level/vega; no new acquisition

## Pre-declared protocol

- Surface signals: ['atm_iv', 'skew']
- Signal detail: atm_iv = amount-weighted mean near-ATM iv; skew = mean(put iv) - mean(call iv) over the trailing window (EVAL-71 helper, reused verbatim via EVAL-76)
- Bar grid (s): [60.0, 300.0]
- Position: side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal decision at bar k; z_k = expanding-z of the causal EVAL-71 surface signal
- Traded form: butterfly (front expiry; ATM body = common strike nearest spot; upper wing = nearest OTM call; lower wing = nearest OTM put; all four legs' IV/greeks backed out of the real mark via EVAL-57 helpers) with the EVAL-62 mark-path net-of-cost P&L on the signed long-wings/short-body aggregate mark/delta: delta-hedge + half real 4-leg spread + hedge fee, spot-normalized
- Butterfly aggregation: mark = (wing_call_mark + wing_put_mark) - (atm_call_mark + atm_put_mark); delta = (wing_call_delta + wing_put_delta) - (atm_call_delta + atm_put_delta)
- Stats: perm 1000 (True) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / size_cap 1.0
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one config (signal x bar grid), net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, nonzero positions > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (all sealed floors + butterfly constructibility; none weakened)

- EVAL-82 consumes both the traded-instrument data (surface snapshots / perp candles / option trades; EVAL-61/62 floor) and the surface signal data (per-bar near-ATM option trade tape; EVAL-71 surface floor), AND it requires the four-leg butterfly (ATM body + both OTM wings) to be constructible from the real mark in >= min_butterfly_states_per_underlying per-bar states per underlying. All sealed floors are reused verbatim and must pass; none is weakened. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Composed of: ['EVAL-61/62 traded-instrument floor', 'EVAL-71 surface floor', 'butterfly-constructibility floor']
- Min underlyings: 2
- Min butterfly states per underlying: 200
- Min states per config: 100

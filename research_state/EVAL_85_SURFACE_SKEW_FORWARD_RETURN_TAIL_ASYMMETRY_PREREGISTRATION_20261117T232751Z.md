# EVAL_85_SURFACE_SKEW_FORWARD_RETURN_TAIL_ASYMMETRY_PREREGISTRATION — causal put-call skew -> forward return tail asymmetry predictiveness (Spearman rank IC)

- Generated: `2026-11-17T23:27:51Z`
- Task: `EVAL85-SURFACE-SKEW-FORWARD-RETURN-TAIL-ASYMMETRY`
- Hypothesis: The causal put-call skew (EVAL-71 near-ATM put-minus-call skew, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent forward return tail asymmetry of the SAME underlying (upper-tail spread minus lower-tail spread over the next H perp log returns), reconstructed from the real Deribit option trade tape and real perp candles, tested on the already-acquired real on-disk captures at the composed EVAL-71 surface floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71 (own-asset surface -> own forward RV level) and EVAL-81 (order-flow -> forward signed return mean): same Spearman rank-IC statistic and sealed signal reconstructions reused verbatim, but a distinct on-charter signal x target cell — put-call skew (surface) -> forward return *tail asymmetry*; no new acquisition

## Pre-declared protocol

- Surface signals: ['skew']
- Target: forward_return_tail_asymmetry — forward return tail asymmetry = (q95 - median) - (median - q05) over the SAME underlying's next H perp log returns (strictly after the decision at bar k)
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal put-call skew z (EVAL-71 build_surface_bars + EVAL-61 expanding_zscore, end-of-bar k)
- Statistic: Spearman rank correlation IC = rho(skew_z_k, forward_tail_asym_k); directional permutation H1: IC > 0
- Stats: perm 1000 (directional (H1: IC>0), shuffle target series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 100

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 surface, not the EVAL-64 ladder floor)

- EVAL-85 consumes each underlying's causal options-surface series (real option trade tape for the IV surface, real perp candles for forward returns) and reuses the sealed EVAL-71 surface floor for EACH underlying (verbatim, neither weakened). Below the composed floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min usable pairs per config: 100

# EVAL_87_SURFACE_ATM_IV_FORWARD_RETURN_TAIL_ASYMMETRY_PREREGISTRATION — causal near-ATM implied vol -> forward return tail asymmetry predictiveness (Spearman rank IC)

- Generated: `2026-11-18T00:54:36Z`
- Task: `EVAL87-SURFACE-ATM-IV-FORWARD-RETURN-TAIL-ASYMMETRY`
- Hypothesis: The causal near-ATM implied vol (EVAL-71 near-ATM IV, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent forward return tail asymmetry of the SAME underlying (upper-tail spread minus lower-tail spread over the next H perp log returns), reconstructed from the real Deribit option trade tape and real perp candles, tested on the already-acquired real on-disk captures at the composed EVAL-71 surface floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71 (own-asset surface atm_iv+skew -> own forward RV level) and EVAL-85 (skew -> forward return tail asymmetry): same Spearman rank-IC statistic and sealed signal reconstructions reused verbatim, but a distinct on-charter signal x target cell — near-ATM IV level (surface) -> forward return *tail asymmetry*; no new acquisition

## Pre-declared protocol

- Surface signals: ['atm_iv']
- Target: forward_return_tail_asymmetry — forward return tail asymmetry = (q95 - median) - (median - q05) over the SAME underlying's next H perp log returns (strictly after the decision at bar k)
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal near-ATM implied vol z (EVAL-71 build_surface_bars + EVAL-61 expanding_zscore, end-of-bar k)
- Statistic: Spearman rank correlation IC = rho(atm_iv_z_k, forward_tail_asym_k); directional permutation H1: IC > 0
- Stats: perm 1000 (directional (H1: IC>0), shuffle target series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 100

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 surface, not the EVAL-64 ladder floor)

- EVAL-87 consumes each underlying's causal options-surface series (real option trade tape for the IV surface, real perp candles for forward returns) and reuses the sealed EVAL-71 surface floor for EACH underlying (verbatim, neither weakened). Below the composed floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min usable pairs per config: 100

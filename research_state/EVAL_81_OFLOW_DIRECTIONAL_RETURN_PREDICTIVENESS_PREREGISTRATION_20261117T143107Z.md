# EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_PREREGISTRATION — options order-flow imbalance -> subsequent signed (directional) return predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-17T14:31:07Z`
- Task: `EVAL81-OFLOW-DIRECTIONAL-RETURN-PREDICTIVENESS`
- Hypothesis: The causal options order-flow signed-aggressor imbalance (EVAL-61/62 build_states, expanding-z-scored) has a positive monotone (Spearman rank) relationship with the subsequent signed log-return (direction) of the underlying, reconstructed from the real Deribit option trade tape and real perp candles. Tested on the already-acquired real on-disk captures at the composed EVAL-71 + order-flow floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-65 (unconditional options order-flow -> RV) and EVAL-70 (perp order-flow -> RV / signed return): the same Spearman rank-IC statistic and all sealed signal reconstructions reused verbatim, but a distinct, on-charter signal x target cell — the *options* order-flow imbalance vs the *signed return* of the underlying; no new acquisition

## Pre-declared protocol

- Order-flow signals: ['imbalance']
- Target: signed_return — signed = sum(log-return) over the next H perp bars (strictly after the decision at bar k); the subsequent direction of the underlying
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal options order-flow imbalance z (EVAL-61/62 build_states, expanding-z-scored, end-of-bar k)
- Statistic: Spearman rank correlation IC = rho(sig_z_k, signed_k) over the causal order-flow states (H1: IC > 0, buy-heavy options flow precedes a positive forward return)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the signed-return series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on EACH of BTC and ETH, at least one config (bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that (underlying, config); else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 surface + order-flow state)

- EVAL-81 consumes each underlying's causal options order-flow states (surface snapshots for spot + straddle quotes, option trade tape for signed-aggressor flow) and the real perp candles for the forward signed return. It composes the sealed EVAL-71 surface floor (applied to EACH underlying, reused verbatim, neither weakened) with an options order-flow adequacy floor (>= min_oflow_states_per_underlying priceable per-bar order-flow states per underlying). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min order-flow states per underlying: 200
- Min usable pairs per config: 120

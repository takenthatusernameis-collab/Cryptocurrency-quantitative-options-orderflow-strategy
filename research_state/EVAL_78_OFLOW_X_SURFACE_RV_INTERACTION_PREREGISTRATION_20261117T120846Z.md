# EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_PREREGISTRATION — options order-flow x implied-vol surface interaction -> realized-vol predictiveness (wrapper-free Spearman rank IC)

- Generated: `2026-11-17T12:08:46Z`
- Task: `EVAL78-OFLOW-X-SURFACE-RV-INTERACTION`
- Hypothesis: The causal interaction of the options order-flow imbalance with the near-ATM implied-volatility surface (product of the EVAL-61/62 order-flow z and the EVAL-71 surface z, reconstructed from the real Deribit option trade tape and real surface snapshots) has a positive monotone (Spearman rank) relationship with subsequent realized volatility: rich surface amplifies buy-heavy flow into higher subsequent realized vol. Tested on the already-acquired real on-disk captures at the composed EVAL-71 + order-flow floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-65 (unconditional options order-flow -> RV) and EVAL-71/77 (unconditional surface -> RV): identical Spearman rank-IC statistic and both signal reconstructions reused verbatim, but a different, on-charter signal family — the *interaction* (product) of the options order-flow imbalance and the near-ATM surface state; no new acquisition

## Pre-declared protocol

- Surface signals: ['atm_iv', 'skew']
- Order-flow signals: ['imbalance']
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal: causal options order-flow imbalance z (EVAL-61/62 build_states, expanding-z-scored) times causal near-ATM surface z (EVAL-71 build_surface_bars atm_iv / skew, forward-filled then expanding-z-scored end-of-bar k): x_k = oflow_z_k * surf_z_k
- Target detail: rv = sqrt(mean(log-return^2)) over the next H perp bars (EVAL-71 definition) on the common aligned bar grid
- Statistic: Spearman rank correlation IC = rho(x_k, rv_k) over the common aligned bar-ends (H1: IC > 0, rich surface amplifies buy-heavy flow into higher subsequent realized vol)
- Stats: perm 1000 (directional (H1: IC>0), shuffle the realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH, at least one config (interaction x bar grid x horizon) has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, at least min_usable_pairs_per_config usable pairs, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 surface + order-flow state)

- EVAL-78 consumes both the surface (EVAL-71) and the options order-flow leg (EVAL-61/62). It composes the sealed EVAL-71 surface floor (applied to EACH underlying, reused verbatim, neither weakened) with an options order-flow adequacy floor (>= min_oflow_states_per_underlying priceable per-bar order-flow states per underlying). This is NOT the EVAL-64 options-surface snapshot floor, which governs the EVAL-67/68/69 ladder and is untouched here.
- Min underlyings: 2
- Min order-flow states per underlying: 200
- Min usable pairs per config: 120

# EVAL_142_CROSS_ASSET_TERM_RATIO_SPILLOVER_RISK_REVERSAL_NET_OF_COST_PREREGISTRATION — cross-asset term_ratio spillover -> risk reversal net-of-cost monetization

- Generated: `2026-11-20T13:58:27Z`
- Task: `EVAL142-CROSS-ASSET-TERM-RATIO-SPILLOVER-RISK-REVERSAL-NET-OF-COST`
- Hypothesis: The causal near/far ATM IV term ratio of the OTHER underlying (cross-asset term_ratio spillover, expanding-z scored) has a positive net-of-cost relationship when timed as a delta-hedged risk reversal on the target underlying, tested on real on-disk captures at the sealed EVAL-64 feasible floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval68`
- Extends: EVAL-139 (cross-asset term_ratio spillover signal, GO) + EVAL-76 (risk-reversal trade construction, mark-path P&L) + EVAL-64 (feasible floor verbatim) + EVAL-65/62 inference

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: signal_k = z(term_ratio[OTHER](k))  (other asset's near/far ATM IV ratio minus one, causal, expanding-z)
- Signal: term_ratio — causal per-bar near/far ATM IV term ratio of the OTHER underlying (e74._term_bars term_ratio), aligned to the common BTC-vs-ETH bar grid (build_cross_section), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Traded form: risk reversal (front expiry; nearest OTM call + nearest OTM put; IV backed out of the real mark via EVAL-57 helpers) with the EVAL-62 mark-path net-of-cost P&L on the signed long-call/short-put aggregate mark/delta: delta-hedge + half real 2-leg spread + hedge fee, spot-normalized
- Bar grid (s): [60.0, 300.0]
- Position: side_k = sign(z_k); exposure_k = min(|z_k|, SIZE_CAP); causal decision at bar k; z_k = expanding-z of the causal cross-asset term_ratio of the OTHER underlying
- Cost model: net-of-cost: hedge_fee_bps on |dHedge|*S; half real 2-leg spread at entry/exit; full spread on side flip (identical to EVAL-57/62/76)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / size_cap None / hedge_fee_bps None
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, net-of-cost mean_return > 0, block-bootstrap 95% CI lower > 0, directional permutation p < 0.05, nonzero positions > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS); below the sealed EVAL-64 floor -> BLOCKED (never NO-GO).

## Pre-registered floor (sealed EVAL-64 feasible floor verbatim)

- Floor = sealed EVAL-64 feasible floor verbatim (scripts/eval64_orderflow_realized_vol_markpath_feasible.py: min_surface_snapshots=1000, min_surface_instruments=100, min_surface_bars_5m=1000, min_option_trades=2000, min_of_instruments=150, min_of_span_seconds=82000, min_of_bars_5m=240, min_perp_bars_5m=1000, min_perp_span_seconds=300000, min_common_bars=240, min_underlyings=2), applied to BOTH BTC and ETH, reused via e64._underlying_floor_strict, NOT weakened. This governs the EVAL-67/68/69 ladder and is untouched here. Below this floor the campaign seals BLOCKED, never NO-GO.
- Min underlyings: 2
- Min surface snapshots/underlying: 1000
- Min surface instruments/underlying: 100
- Min surface 5m bars/underlying: 1000
- Min option trades/underlying: 2000
- Min OF instruments/underlying: 150
- Min OF span seconds/underlying: 82000.0
- Min OF 5m bars/underlying: 240
- Min perp 5m bars/underlying: 1000
- Min perp span seconds/underlying: 300000.0
- Min common bars/underlying: 240

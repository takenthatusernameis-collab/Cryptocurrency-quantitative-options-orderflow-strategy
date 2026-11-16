# EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION — ETH OOS replication of suggestive EVAL-65 slice (tox/imbalance::bar60::h72, wrapper-free Spearman rank IC)

- Generated: `2026-11-16T12:19:25Z`
- Task: `EVAL66-ETH-OFLOW-TOX-RV-OOS`
- Hypothesis: The suggestive EVAL-65 ETH slice (tox/imbalance, bar60, horizon 72) replicates out-of-sample on a fresh disjoint real ETH 7d window: Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and BH-FDR rejects, at the sealed EVAL-64 feasible floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval66`
- Extends: EVAL-65 (identical signal/statistic/floor reused; restricted to the single ETH predictive slice on a fresh disjoint real window)
- Disjoint from: data/raw/eval63/three_way_ETH_20261116T064816Z.json (window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)

## Pre-declared protocol

- Underlyings: ['ETH']
- Tox signals: ['tox', 'imbalance']
- Bar grid (s): [60.0]
- Forward horizons (bars): [72]
- Signal: signal_z_k = expanding-zscore of per-bar options order-flow toxicity (tox) / signed-aggressor imbalance (imbalance), reused verbatim from EVAL-61/EVAL-62 (causal, end-of-bar k)
- Target: rv_{k+1..k+H} = sqrt(mean(log-return^2)) over the next H perp 1m/5m bars (forward realized vol, strictly after the decision at k)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, rv_forward_k)
- Stats: perm 1000 (directional (H1: IC>0), shuffle realized-vol series) / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42

## Pre-declared GO bar

GO only if, on ETH and at least one of the pre-registered configs (tox::bar60::h72, imbalance::bar60::h72), Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered feasible floor (reused verbatim from sealed EVAL-64)

- min surface snapshots/underlying: 1000
- min surface 5m bars/underlying: 1000
- min Deribit option trades/underlying: 2000
- min perp 5m bars/underlying: 1000
- min perp span seconds/underlying: 300000.0
- min common 5m bars/underlying: 240
- min underlyings (ETH-only): 1

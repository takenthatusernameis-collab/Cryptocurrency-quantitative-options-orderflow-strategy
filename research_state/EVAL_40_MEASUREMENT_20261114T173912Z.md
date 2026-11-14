# EVAL_40_MEASUREMENT_20261114T173912Z — EVAL-40 execution seal

- **Task:** `INIT-2026-11-14T17:33:33Z-EVAL-40-EXECUTE-SEAL`
- **Sealed:** 2026-11-14T17:39:12Z
- **Verdict:** **NO-GO (REPLICATION)**
- **Campaign status:** TERMINATED (EVAL-36 `TERMINATE_NO_GO` remains in force)
- **Provenance:** real (public OKX read-only export; `authenticity_verified=false`; `never_valid_true=true`; paper-only; `.env` absent; `LIVE_TRADING_ENABLED=false`)

## Sealed inputs (hashes verified pre-run, unchanged)

| Input | Path | SHA-256 | Facts |
|---|---|---|---|
| Orderflow | `data/raw/orderflow_okx_BTC-USD-SWAP-40.json` | `a105db1c323c9c64db75882c367f84a81f2ac87374ed62ad490d334af484bc4b` | 84,800 trades / 1,602 bars; `485439506..485524305` |
| Options | `data/raw/options_okx_BTC_20261114T171725Z.json` | `159bc3b8f27a605f2ac3d2430a51485a16c0781aee04c7f3ec79e295934f2eca` | 827 quotes / 14 expiries / 93 strikes |

- Pre-registration: `research_state/EVAL_40_PREREGISTRATION_20261114T172130Z.json` sha256 `eb326306fd772fc2025d41f3aa20c8a813247649fdaf1978a4195b139133b7e7`.

## Command (exit 0)

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m src.analytics.real_net_of_cost_evaluation \
  --data-dir data/raw --out research_state \
  --symbol BTC --bar-duration-seconds 15 \
  --orderflow-path data/raw/orderflow_okx_BTC-USD-SWAP-40.json
```

## Measurement artifact (referenced, immutable)

- `research_state/REAL_NET_OF_COST_EVAL_23_20261114T173647Z.json` sha256 `dd6c133ce2a8794a70aaf398125aa62fff1e6852b605c10b5c3d2eef97b9cd9e`
- `research_state/REAL_NET_OF_COST_EVAL_23_20261114T173647Z.md` sha256 `e46b2b68ffefea875e5bbf573d747a5cfa6bbeb636856ce55f97d8e7c5ecfea2`

## Measured numbers (window 02:25:00.798Z → 09:05:22.330Z; 84,800 trades / 1,602 bars)

- **Verdict: NO-GO, 8/11 checks passed.** Failed: `options_signal_exists`, `combined_net_of_cost_superior`, `options_signal_tradable`.
- `options_leg_degenerate = true`; distinct options signal values = 1; signal stdev = 0.0; `abs_options_ic = 3.97e-18`.
- combined_alpha `ic_mean = -0.029023` (t = -1.807); options_alpha `ic_mean = -3.97e-18`; orderflow_alpha `ic_mean = -0.010087` (t = -0.729).
- permutation: observed difference `-0.093161`, p = 0.000999 (combined significantly **worse** than best single pillar).
- walk-forward (38 windows): combined Sharpe `1.858414` (232 trades, cost $415.64); options-only Sharpe `4.246051` (688 trades); orderflow-only Sharpe `-5.349272` (614 trades, cost $646.34); flat 0.0.
- Fusion: both pillars produced time variation; the fusion rule is not the binding constraint.

## GO/NO-GO criteria

`combined_net_of_cost_superior=false`, `options_signal_tradable=false`, `options_leg_degenerate=true`, `permutation_not_worse_than_best_single_pillar=false`. Outcome: **REPLICATION (NO-GO)** — no GO; campaign termination unchanged.

## Bottleneck removed this session

The prior handoff's EVAL-40 deliverable (measured artifact) was missing; it is now produced and sealed. The pinned `--orderflow-path` avoids the recency-based discovery that would select the older base tape. `.env` absent; no `*.lock`/`*.pid`; `.venv-deps` present.
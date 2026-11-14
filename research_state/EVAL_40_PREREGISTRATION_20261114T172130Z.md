# EVAL-40 PREREGISTRATION — 2026-11-14T17:21:30Z

**Task ID:** `INIT-2026-11-14T16:53:42Z-EVAL-40-ACQUIRE-PREREG-EVAL`
**Sealing intent:** REPLICATION (expect NO-GO on a provably disjoint real window)

## New real dataset (non-overlapping)

| Artifact | Path | SHA-256 | Trades/Bars | Window |
|---|---|---|---|---|
| Orderflow | `data/raw/orderflow_okx_BTC-USD-SWAP-40.json` | `a105db1c323c9c64db75882c367f84a81f2ac87374ed62ad490d334af484bc4b` | 84,800 trades / 1,602 bars | 2026-11-14T02:25:00Z → 09:05:22Z |
| Options | `data/raw/options_okx_BTC_20261114T171725Z.json` | `159bc3b8f27a605f2ac3d2430a51485a16c0781aee04c7f3ec79e295934f2eca` | 827 quotes / 827 contracts / 14 expiries | live public chain |

**Disjointness proof:** new tape trade-id range `485439506..485524305`; existing
`orderflow_okx_BTC-USD-SWAP.json` range `485524306..485602005`. **0 overlapping
trade ids.** Acquired with `--after-cursor 485524306` (OKX `after` trade-id
pagination), so the new window is strictly older and cannot share a single
trade with the EVAL-23/38/39 window.

## Evaluation command (pre-registered, no evaluation before this seal)

```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m src.analytics.real_net_of_cost_evaluation \
  --data-dir data/raw --out research_state \
  --symbol BTC --bar-duration-seconds 15
```

`load_real_orderflow` selects the alphabetically-last real orderflow export
(`-40` > base name) and `load_real_options_chain` selects the alphabetically-last
real options export; both are real, non-synthetic, and `RealDataUnavailable` is
raised if either is absent. No synthetic fallback exists.

## GO/NO-GO criteria

A **GO** requires a verifying sealed artifact on the NEW real dataset with:
`combined_net_of_cost_superior == true`, `options_signal_tradable == true`,
`options_leg_degenerate == false`, no kill-switch breach, and a permutation
test showing the combined strategy not worse than the best single pillar.

**Expected verdict: REPLICATION (NO-GO).** Prior sealed measurements:
EVAL-36 `TERMINATE_NO_GO`; EVAL-38 REPLICATION (Sharpe -7.9539, 1221 trades,
$179.28 cost, max-DD 0.8679, kill-switch breach); EVAL-39 REPLICATION (NO-GO
8/11, `options_leg_degenerate=true`, `options_alpha` 0.0 across all horizons,
`combined_alpha.ic_mean=-0.000258`, `orderflow_alpha.ic_mean=0.041876`,
permutation p=0.000999 combined worse than best single pillar). A REFUTED
verdict would be the only outcome that changes the campaign termination.

## Constraints

Paper-only, `.env` absent, `LIVE_TRADING_ENABLED=false`, real data only,
no modification of sealed EVAL-02..39, no `phaseNN_*` orchestrator wrappers.
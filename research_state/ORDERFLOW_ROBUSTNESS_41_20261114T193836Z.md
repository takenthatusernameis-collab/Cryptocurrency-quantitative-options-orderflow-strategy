# ORDERFLOW_ROBUSTNESS_41 — EVAL-41 Track A Seal

**eval_id:** `ORDERFLOW_ROBUSTNESS_41`
**stamp:** `20261114T193836Z`
**campaign:** EVAL-41
**track:** A — Orderflow cross-window robustness
**verdict:** `NO-GO / REPLICATION`

---

## Question

Does orderflow have persistent net-of-cost edge, or was EVAL-33's +4.81 window-lucky?

## Answer

EVAL-33's +4.81 was window-lucky. Orderflow shows **no persistent net-of-cost edge** across three disjoint real windows: Sharpe > 0 on only 1/3 tapes, and all 3 tapes breach the kill-switch (max-DD > 0.20).

## Track A pre-declared bar

GO only if orderflow-only net-of-cost Sharpe > 0 on >= 2/3 new tapes **AND** no kill-switch breach (max-DD <= 0.20).

**Bar result: FAIL.**
- Tapes with Sharpe > 0: 1/3 (41a only)
- Tapes with kill-switch breach (max-DD > 0.20): 3/3 (41a 0.441, 41b 0.949, 41c 0.465)

## Per-tape results (all real OKX data, pinned eval `real_net_of_cost_evaluation`, bar duration 15 s)

| Tape | IDs | Trades | Bars | TS range | Orderflow-only Sharpe | Max-DD | Trades | Cost USD | Kill-switch | Verdict |
|------|-----|--------|------|----------|----------------------|--------|--------|----------|-------------|---------|
| 41a | 485397106..485439505 | 42,400 | 1553 | 2026-11-13T19:56:47Z..2026-11-14T02:25:00Z | **0.239** (>0) | 0.441 (breach) | 475 | 591.02 | YES | NO-GO |
| 41b | 485317106..485397105 | 80,000 | 1555 | 2026-11-13T13:27:56Z..2026-11-13T19:56:26Z | **-8.785** | 0.949 (breach) | 618 | 635.05 | YES | NO-GO |
| 41c | 485257706..485317105 | 59,400 | 1551 | 2026-11-13T07:00:09Z..2026-11-13T13:27:54Z | **-0.857** | 0.465 (breach) | 589 | 675.45 | YES | NO-GO |

All three tapes disjoint; walked downward from EVAL-40 tape oldest id `485439506` via OKX `after` cursor (returns older trades). Each tape spans >= 6.46 h.

Eval artifacts:
- 41a: `research_state/REAL_NET_OF_COST_EVAL_23_20261114T193509Z.json` (sha256 `86be4d3e...`) — NO-GO 8/11
- 41b: `research_state/REAL_NET_OF_COST_EVAL_23_20261114T193549Z.json` (sha256 `9eaaa012...`) — NO-GO 8/11
- 41c: `research_state/REAL_NET_OF_COST_EVAL_23_20261114T193710Z.json` (sha256 `faae2d82...`) — NO-GO 8/11

## Inputs provenance

- Source: OKX public read-only market data exports via `src.data.public_export_acquisition` (requests session, `--request-delay-seconds 0.15`)
- Cursor walk: `--after-cursor 485439506` returns older trades; 3 disjoint tapes
- Synthetic fallback: none. Synthetic files used: none. Real loaders only.

## Constraints honored

- Paper-only: `.env` absent, `LIVE_TRADING_ENABLED=false`, no live enablement/config/credential mutation, no order placement
- Never fall back to synthetic data; real loaders raise `RealDataUnavailable`
- Sealed artifacts EVAL-02..40 immutable; this is a new timestamped EVAL-41 artifact (append-only)
- Network: public read-only market data only, polite rate limiting
- No `phaseNN_*` orchestrator wrappers; reused existing `src.data` / `src.analytics` modules

## Next

Track A sealed **NO-GO / REPLICATION**. Orderflow pillar decisively closed as non-persistent on available real BTC/OKX data. Track B (dense real options time-series net-of-cost falsification, >= 12 snapshots at <= 10-min spacing over >= 2 h) remains the non-blocking follow-up; it requires a fresh no-cursor orderflow tape covering the snapshot window (see EVAL-41 Track B gotcha in `research_state/durable_handoff.md`). No GO without sealed evidence on new real data.

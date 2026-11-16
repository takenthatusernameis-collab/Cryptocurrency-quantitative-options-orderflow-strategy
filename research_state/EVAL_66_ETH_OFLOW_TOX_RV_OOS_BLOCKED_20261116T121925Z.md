# EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED — ETH OOS replication of suggestive EVAL-65 slice (below the pre-registered feasible floor)

- Generated: `2026-11-16T12:19:25Z`
- Task: `EVAL66-ETH-OFLOW-TOX-RV-OOS`
- Verdict: **BLOCKED** (measured; not NO-GO)
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval66`
- Underlyings: ETH
- Floor met: False

The capture does not meet the pre-registered feasible floor (reused from sealed EVAL-64), so no GO/NO-GO verdict is emitted. Do NOT weaken the floor, do NOT use synthetic data, and do NOT emit NO-GO on under-floor data.

## Per-underlying floor

- ETH: {"snapshots_ok": true, "surface_instruments_ok": false, "surface_bars_ok": true, "trades_ok": false, "of_instruments_ok": false, "of_span_ok": true, "of_bars_ok": true, "perp_bars_ok": true, "perp_span_ok": true, "common_overlap_ok": true}

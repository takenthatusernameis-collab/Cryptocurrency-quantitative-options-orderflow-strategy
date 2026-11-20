# EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED — BTC OOS replication of suggestive EVAL-65 slice (below the pre-registered feasible floor and/or overlapping the sealed BTC window)

- Generated: `2026-11-20T00:52:48Z`
- Task: `EVAL67-BTC-OFLOW-TOX-RV-OOS`
- Verdict: **BLOCKED** (measured; not NO-GO)
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval67`
- Underlyings: BTC
- Floor met: False
- Disjointness met: True

The capture does not meet the pre-registered feasible floor (reused from sealed EVAL-64) and/or overlaps the sealed EVAL-64/65 BTC window (2026-11-09T06:48:16Z..2026-11-16T06:48:16Z), so no GO/NO-GO verdict is emitted. Do NOT weaken the floor, do NOT use synthetic data, and do NOT emit NO-GO on under-floor or non-disjoint data.

## Disjointness

- BTC: {"underlying": "BTC", "ok": true, "reason": "disjoint", "capture_window": ["2026-11-16T07:36:28Z", "2026-11-20T00:24:28Z"], "sealed_window": ["2026-11-09T06:48:16Z", "2026-11-16T06:48:16Z"], "overlap_seconds": 0.0, "capture_span_seconds": 319680.0, "meets_min_span": true}

## Per-underlying floor

- BTC: {"snapshots_ok": true, "surface_instruments_ok": true, "surface_bars_ok": true, "trades_ok": true, "of_instruments_ok": false, "of_span_ok": true, "of_bars_ok": true, "perp_bars_ok": true, "perp_span_ok": true, "common_overlap_ok": true}

#!/usr/bin/env python3
"""EVAL-63: **extended-duration + extended-breadth** replication of the repo's
namesake hypothesis (real options order-flow toxicity -> subsequent realized
volatility, traded via a signal-timed delta-hedged ATM straddle with the correct
EVAL-57 mark-path net-of-cost P&L) on a **fresh, heavier, longer real three-way
BTC+ETH capture**.

Why this rung exists
--------------------
EVAL-62 sealed ``NO-GO CONFIRMED (PASS)`` on a ~24h capture (BTC 289 snaps / 92
surface instruments / 2748 option trades; ETH 289 / 280 / 3558; ~288 common 5m
bars). ETH's best config printed a positive Sharpe (+0.6163) but failed the GO bar
on replication/permutation/bootstrap; BTC's best was -0.0443. That leaves a
power/breadth/duration gap: the namesake hypothesis was falsified on a *narrow*
sample, not on a *heavy* one.

EVAL-63 keeps the EVAL-62 measurement **byte-for-byte identical** (it reuses
``scripts/eval62_orderflow_realized_vol_markpath.py`` helpers verbatim:
``build_states``, ``markpath_returns``, ``evaluate_config``) and changes only the
**data** and the **pre-registered heavy-work floor**:

* **Extended breadth:** a much wider real roster (more expiries x more strikes ->
  more instruments and more real option trades per underlying), strictly heavier
  than the EVAL-62 floor.
* **Extended surface/perp duration:** a >=7 day real surface + perpetual window,
  so the vol-mark / realized-vol leg and the flat-bar horizon are materially longer
  than EVAL-62's single day.

Measured data-availability ceiling (public read-only Deribit/OKX, 2026-11-16)
---------------------------------------------------------------------------
* Deribit **option tick trades** (``get_last_trades_by_instrument_and_time``) retain
  only **~24h**: 1d/2d/3d/5d/7d lookbacks all return the same trade set / ~83.4ks
  span. So the options **order-flow** leg can never span 7d from the free public
  API -- the EVAL-63 floor therefore requires the OF leg to clear a *24h* span
  (heavier than EVAL-62's 79.2ks floor) with **much greater breadth**, and it does
  NOT demand a 7d options-flow span (which is physically impossible and would
  guarantee a false BLOCKED loop).
* Deribit **5m option candles** (``get_tradingview_chart_data``) DO scale with the
  requested window for still-active instruments (1d->289, 2d->577, 3d->865 pts),
  so the surface/perp legs can reach 7d.

Consequence for the measurement: because ``build_states`` is reused verbatim, on a
7d capture the strategy is **flat** (``side=0``, ``ret=0``) on every bar without
option-trade toxicity. The extended duration therefore enters the P&L as
additional flat bars -- a **conservative, honest** extension that *penalizes* the
Sharpe (more bars, same ~24h of nonzero signal) rather than inflating it. This is
the correct way to ask "does the namesake signal survive a heavier, longer,
lower-power test?" without reintroducing any P&L artifact.

Hypothesis / GO bar (fixed, pre-registered; identical in spirit to EVAL-62)
--------------------------------------------------------------------------
Per 5m bar: ``tox_k = (call_notional - put_notional)/(call_notional+put_notional)``
from real Deribit option trades (and signed-aggressor ``imbalance`` variant).
Position: ``side_k = sign(tox_z_k)``, ``exposure_k = clip(|tox_z_k|, 0, size_cap)``,
delta-hedged each bar in the perp. P&L (EVAL-57 correct):
``ret_k = (side_k*exposure_k*(mark_{k+1}-mark_k)*S_k + hedge_k*dS_k - cost_k)/S_k``.
Grid = {tox, imbalance} x {60s, 300s}. **GO only if, on BOTH BTC and ETH and at
least one config:** net Sharpe > 0, no kill-switch breach (max-DD <= 0.20),
permutation p < 0.05, bootstrap 95% CI lower > 0, pooled PBO < 0.5; else
``NO-GO CONFIRMED (PASS)``.

Heavy-work floor (stricter than EVAL-62; heavy but achievable)
--------------------------------------------------------------
Per underlying: surface >= 1000 snapshots / >= 100 instruments / >= 1500 5m bars;
perp >= 1500 5m bars / >= 600000 s span; Deribit option trades >= 4000 / >= 150
instruments / >= 82000 s span / >= 240 5m bars; common 5m bars >= 240; roster >= 2
underlyings. Below floor seals ``EVAL_63_..._BLOCKED_<UTC>`` (never a NO-GO).

Seal ``EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_PREREGISTRATION_<UTC>.{json,md}`` (before
measurement) then ``EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_COMBINED_<UTC>.{json,md}``
(or ``..._BLOCKED_<UTC>``).
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed EVAL-61 / EVAL-62 helpers verbatim (no edits to sealed files).
import scripts.eval61_orderflow_realized_vol_net_of_cost as e61  # noqa: E402
import scripts.eval62_orderflow_realized_vol_markpath as e62  # noqa: E402
from src.analytics.integrated_options_orderflow_evaluation import (  # noqa: E402
    _dsr_of_returns,
)
from src.analytics.real_walkforward_certification import (  # noqa: E402
    _benjamini_hochberg,
    _cscv_pbo,
)

OUT_DIR = ROOT / "research_state"
REPORT_ID = "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_COMBINED"
PREREG_ID = "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_PREREGISTRATION"
BLOCKED_ID = "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH_BLOCKED"

# --- Strict heavy-work floor (per underlying) ------------------------------
# Surface / perp are 7d-capable (Deribit 5m candles scale with window).
# Options order flow is ~24h-capped by Deribit tick-trade retention, so its
# span floor is a heavier-than-EVAL-62 24h bar, and its weight comes from a much
# wider instrument/trade roster.
MIN_SNAPSHOTS = 1000
MIN_SURFACE_INSTRUMENTS = 100
MIN_SURFACE_BARS_5M = 1500
MIN_OPTION_TRADES = 4000
MIN_OF_INSTRUMENTS = 150
MIN_OF_SPAN_SECONDS = 82000.0
MIN_OF_BARS_5M = 240
MIN_PERP_BARS_5M = 1500
MIN_PERP_SPAN_SECONDS = 600000.0
MIN_COMMON_BARS = 240
MIN_UNDERLYINGS = 2

# Reused EVAL-62 pre-registered measurement constants (identical => comparable).
TOX_SIGNALS: Tuple[str, ...] = e62.TOX_SIGNALS
GRID_BAR_SECONDS: Tuple[float, ...] = e62.GRID_BAR_SECONDS


# ---------------------------------------------------------------------------
# Strict floor (re-implemented with SPLIT surface/perp vs order-flow thresholds;
# EVAL-61 uses a single MIN_BARS/MIN_SPAN_SECONDS for all three legs, which would
# wrongly fail a 7d capture whose order-flow leg is 24h-capped).
# ---------------------------------------------------------------------------
def _underlying_floor_strict(capture: Dict[str, Any]) -> Dict[str, Any]:
    inst = capture.get("underlying", "?")
    surface = capture.get("surface", {})
    snaps = surface.get("snapshots", []) or []
    trades = capture.get("option_trades", []) or []
    perp = capture.get("perp_candles", []) or []

    n_snapshots = len(snaps)
    surface_instruments = len({
        q.get("symbol") for s in snaps for q in (s.get("quotes") or [])
    })
    surface_bars_5m = len(e61._bar_ends(perp, 300.0))

    of_ts = [int(t["ts"]) for t in trades if int(t.get("ts") or 0) > 0]
    n_trades = len(trades)
    of_instruments = len({t.get("instrument") for t in trades if t.get("instrument")})
    of_span = ((max(of_ts) - min(of_ts)) / 1000.0) if len(of_ts) >= 2 else 0.0
    of_bars_5m = int(of_span // 300.0) if of_span > 0 else 0

    perp_ts = [int(c["ts"]) for c in perp if int(c.get("ts") or 0) > 0]
    perp_span = ((max(perp_ts) - min(perp_ts)) / 1000.0) if len(perp_ts) >= 2 else 0.0
    perp_bars_5m = int(perp_span // 300.0) if perp_span > 0 else 0

    # Common-grid overlap (identical definition to EVAL-61/EVAL-62).
    surf_avail = e61.straddle_series_from_surface(capture)
    avail_times = [t for t, _ in surf_avail]
    common = 0
    if of_ts and perp_ts and avail_times:
        lo = max(min(of_ts), min(perp_ts))
        hi = min(max(of_ts), max(perp_ts))
        for be in e61._bar_ends(perp, 300.0):
            if be < lo or be > hi:
                continue
            if any(at <= be for at in avail_times):
                common += 1

    checks = {
        "snapshots_ok": bool(n_snapshots >= MIN_SNAPSHOTS),
        "surface_instruments_ok": bool(surface_instruments >= MIN_SURFACE_INSTRUMENTS),
        "surface_bars_ok": bool(surface_bars_5m >= MIN_SURFACE_BARS_5M),
        "trades_ok": bool(n_trades >= MIN_OPTION_TRADES),
        "of_instruments_ok": bool(of_instruments >= MIN_OF_INSTRUMENTS),
        "of_span_ok": bool(of_span >= MIN_OF_SPAN_SECONDS),
        "of_bars_ok": bool(of_bars_5m >= MIN_OF_BARS_5M),
        "perp_bars_ok": bool(perp_bars_5m >= MIN_PERP_BARS_5M),
        "perp_span_ok": bool(perp_span >= MIN_PERP_SPAN_SECONDS),
        "common_overlap_ok": bool(common >= MIN_COMMON_BARS),
    }
    return {
        "underlying": inst,
        "n_surface_snapshots": n_snapshots,
        "n_surface_instruments": surface_instruments,
        "n_surface_bars_5m": surface_bars_5m,
        "n_option_trades": n_trades,
        "n_of_instruments": of_instruments,
        "of_span_seconds": round(of_span, 3),
        "n_of_bars_5m": of_bars_5m,
        "n_perp_candles": len(perp),
        "perp_span_seconds": round(perp_span, 3),
        "n_perp_bars_5m": perp_bars_5m,
        "n_common_bars_5m": common,
        "checks": checks,
        "ok": bool(all(checks.values())),
    }


# ---------------------------------------------------------------------------
# Protocol + orchestration (mirrors EVAL-62 run_eval62; strict floor + EVAL-63 ids)
# ---------------------------------------------------------------------------
def build_protocol(capture_dir: str) -> Dict[str, Any]:
    return {
        "eval": "EVAL-63",
        "title": "Extended-duration + extended-breadth real options order-flow "
                 "toxicity -> signal-timed delta-hedged ATM straddle with correct "
                 "mark-path net-of-cost P&L on the BTC/ETH perpetual",
        "extends": "EVAL-62 (identical measurement, heavier/longer real sample; "
                   "EVAL-62 stays sealed/immutable)",
        "supersedes": "none (EVAL-62 remains the sealed ~24h baseline; EVAL-63 is the "
                      "heavy extended replication)",
        "capture_dir": str(capture_dir),
        "tox_signals": list(TOX_SIGNALS),
        "tox_detail": {
            "tox": "(call_notional - put_notional)/(call_notional + put_notional) "
                   "from real Deribit option trades per bar (EVAL-61 helper, reused)",
            "imbalance": "(aggressive_buy_amt - aggressive_sell_amt)/total_amt "
                         "(signed aggressor variant, EVAL-61 helper, reused)",
        },
        "position": "side_k = sign(tox_z_k); exposure_k = clip(|tox_z_k|, 0, size_cap); "
                    "causal decision at bar k; delta-hedged in the perp",
        "straddle": "front-expiry common strike nearest spot, both legs priced from real "
                    "marks (EVAL-57 _pick_straddle_quotes/_iv_and_greeks, reused)",
        "pnl_per_bar": "dOption_k = side_k*exposure_k*(mark_{k+1}-mark_k)*S_k; "
                       "gross_k = dOption_k + hedge_k*dS_k; ret_k = (gross_k - cost_k)/S_k",
        "duration_note": "states are built with the identical EVAL-62 causal routine; on a "
                         ">=7d capture the strategy is flat (side=0, ret=0) on bars without "
                         "option-trade toxicity, so the extended duration enters as additional "
                         "flat bars (conservative: it dilutes Sharpe, never inflates it). Only "
                         "the ~24h options-order-flow overlap carries nonzero signal because "
                         "Deribit tick-trade retention is ~24h.",
        "data_availability": {
            "deribit_option_trade_retention_seconds_approx": 86400,
            "deribit_option_trade_retention_note": "1d/2d/3d/5d/7d lookbacks return the same "
                                                   "trade set (~83.4ks); options order flow is "
                                                   "24h-capped, so no 7d options-flow floor is set",
            "deribit_5m_candle_scaling_note": "1d->289, 2d->577, 3d->865 pts; surface/perp "
                                              "legs reach 7d",
        },
        "cost_model": "net-of-cost: hedge_fee_bps on |dHedge|*S; half real 2-leg spread at "
                      "entry/exit; full spread on side flip (identical to EVAL-57/62)",
        "bar_seconds_grid": [float(b) for b in GRID_BAR_SECONDS],
        "zwindow": int(e62.ZWINDOW),
        "cost_bps": float(e62.COST_BPS),
        "hedge_fee_bps": float(e62.HEDGE_FEE_BPS),
        "size_cap": float(e62.SIZE_CAP),
        "walkforward": {"train_frac": "1/3", "test_frac": "1/5", "step_frac": "1/5"},
        "stats": {
            "permutation_perms": e62.PERMUTATION_PERMS,
            "permutation_paired": True,
            "bootstrap_resamples": e62.BOOTSTRAP_RESAMPLES,
            "bootstrap_block": e62.BOOTSTRAP_BLOCK,
            "pbo_k_folds": e62.PBO_K_FOLDS,
            "pbo_n_combinations": e62.PBO_N_COMBINATIONS,
            "fdr_alpha": e62.FDR_ALPHA,
            "seed": e62.SEED,
        },
        "kill_switch_max_dd": e62.KILL_SWITCH_MAX_DD,
        "go_bar": (
            "GO only if, on both BTC and ETH and at least one grid config, net-of-cost "
            "Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, "
            "bootstrap 95% CI lower > 0, and pooled PBO < 0.5; else NO-GO."
        ),
        "floor": {
            "min_surface_snapshots_per_underlying": MIN_SNAPSHOTS,
            "min_surface_instruments_per_underlying": MIN_SURFACE_INSTRUMENTS,
            "min_surface_bars_5m_per_underlying": MIN_SURFACE_BARS_5M,
            "min_option_trades_per_underlying": MIN_OPTION_TRADES,
            "min_of_instruments_per_underlying": MIN_OF_INSTRUMENTS,
            "min_of_span_seconds_per_underlying": MIN_OF_SPAN_SECONDS,
            "min_of_bars_5m_per_underlying": MIN_OF_BARS_5M,
            "min_perp_bars_5m_per_underlying": MIN_PERP_BARS_5M,
            "min_perp_span_seconds_per_underlying": MIN_PERP_SPAN_SECONDS,
            "min_common_bars_per_underlying": MIN_COMMON_BARS,
            "min_underlyings": MIN_UNDERLYINGS,
            "note": "order-flow span floor is a heavier-than-EVAL-62 24h bar because Deribit "
                    "tick-trade retention is ~24h; surface/perp floors require the full >=7d",
        },
    }


def run_eval63(
    *,
    capture_dir: str = "data/raw/eval63",
    write: bool = True,
    task_label: str = "EVAL63-EXTENDED-OFLOW-RV-MARKPATH",
) -> Dict[str, Any]:
    generated_at = e62._utc_now_iso()
    capture_dir_abs = Path(capture_dir)
    if not capture_dir_abs.is_absolute():
        capture_dir_abs = ROOT / capture_dir_abs
    captures = e61._capture_inventory(str(capture_dir_abs))

    per_underlying_floor: Dict[str, Dict[str, Any]] = {}
    for c in captures:
        inst = c.get("underlying", "?")
        per_underlying_floor[inst] = _underlying_floor_strict(c)

    floor_ok = bool(
        len(captures) >= MIN_UNDERLYINGS
        and per_underlying_floor
        and all(v["ok"] for v in per_underlying_floor.values())
    )

    per_config: List[Dict[str, Any]] = []
    returns_by_config: Dict[str, List[float]] = {}
    errors: List[str] = []
    for cap in captures:
        inst = cap.get("underlying", "?")
        for sig in TOX_SIGNALS:
            for bar_s in GRID_BAR_SECONDS:
                try:
                    res = e62.evaluate_config(cap, tox_signal=sig, bar_seconds=bar_s)
                except BaseException as exc:  # noqa: BLE001
                    errors.append(f"{inst}::{sig}::bar{bar_s}: {exc!r}")
                    continue
                per_config.append(res)
                if res.get("n_returns", 0) > 0:
                    states = e62.build_states(cap, tox_signal=sig, bar_seconds=bar_s)
                    returns_by_config[
                        f"{inst}::{sig}::bar{bar_s}"
                    ] = e62.markpath_returns(states)["returns"]

    pbo = _cscv_pbo(returns_by_config, n_combinations=e62.PBO_N_COMBINATIONS,
                    k_folds=e62.PBO_K_FOLDS, seed=e62.SEED) if len(returns_by_config) >= 2 else {
                    "overall_pbo": 0.0, "note": "insufficient configs"}
    p_values = {
        f"{r['underlying']}::{r['signal']}::bar{r['bar_seconds']}": e62._finite(
            r.get("permutation_p"), 1.0
        )
        for r in per_config if r.get("n_returns", 0) > 0
    }
    bh = _benjamini_hochberg(p_values, alpha=e62.FDR_ALPHA) if p_values else {"rejected": []}

    by_inst: Dict[str, List[Dict[str, Any]]] = {}
    for r in per_config:
        by_inst.setdefault(r["underlying"], []).append(r)
    inst_summary: List[Dict[str, Any]] = []
    for inst, rows in by_inst.items():
        best = max(rows, key=lambda r: e62._finite(r.get("sharpe"), -1e9))
        inst_summary.append({
            "underlying": inst,
            "n_configs": len(rows),
            "best_sharpe": e62._finite(best.get("sharpe"), 0.0),
            "best_config": f"{best['signal']}::bar{best['bar_seconds']}",
            "any_pass": bool(any(r.get("pass") for r in rows)),
        })

    all_pass = bool(inst_summary) and all(s["any_pass"] for s in inst_summary)
    pooled_pbo = e62._finite(pbo.get("overall_pbo"), 0.0)
    go = bool(floor_ok and all_pass and pooled_pbo < 0.5)
    verdict = "GO CONFIRMED" if go else "NO-GO CONFIRMED (PASS)"
    campaign_state = "EVAL_63_EXTENDED_OFLOW_RV_MARKPATH" if floor_ok else "EVAL_63_BLOCKED_FLOOR"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task": task_label,
        "verdict": verdict if floor_ok else "BLOCKED",
        "verdict_detail": (
            "extended-duration + extended-breadth real options order-flow toxicity -> "
            "signal-timed delta-hedged ATM straddle with correct mark-path net-of-cost P&L "
            "(EVAL-62 measurement, heavier/longer real sample)"
            if floor_ok else "capture below heavy-work floor; no verdict"
        ),
        "floor_ok": bool(floor_ok),
        "capture_dir": str(capture_dir_abs),
        "underlyings": sorted(per_underlying_floor),
        "floor": build_protocol(capture_dir)["floor"],
        "per_underlying_floor": per_underlying_floor,
        "protocol": build_protocol(capture_dir),
        "per_config": per_config,
        "per_underlying": inst_summary,
        "pooled": {
            "overall_pbo": pooled_pbo,
            "bh_fdr": bh,
            "all_underlyings_pass": all_pass,
            "campaign_state": campaign_state,
        },
        "errors": errors,
    }

    if not write:
        return report

    prereg = build_prereg(report)
    e62._seal(PREREG_ID, prereg, e62.build_prereg_md)

    if not floor_ok:
        e62._seal(BLOCKED_ID, _build_blocked_report(report), build_blocked_md)
        return report

    e62._seal(REPORT_ID, report, e62.build_md)
    return report


def build_prereg(report: Dict[str, Any]) -> Dict[str, Any]:
    p = report["protocol"]
    return {
        "prereg_id": PREREG_ID,
        "generated_at": report["generated_at"],
        "task": report["task"],
        "hypothesis": (
            "Real options order-flow toxicity predicts subsequent realized volatility, and "
            "a signal-timed delta-hedged ATM straddle measured with the correct mark-path "
            "net-of-cost P&L is tradable for the BTC/ETH perpetual on a fresh, heavier, "
            "longer real synchronized sample (extended-duration + extended-breadth "
            "replication of EVAL-62)."
        ),
        "extends": p["extends"],
        "data_availability": p["data_availability"],
        "protocol": p,
        "capture_dir": report["capture_dir"],
    }


def build_blocked_md(r: Dict[str, Any]) -> str:
    lines = [
        f"# {BLOCKED_ID} — options order-flow toxicity -> signal-timed delta-hedged "
        f"ATM straddle (extended duration/breadth, below heavy-work floor)",
        "",
        f"- Generated: `{r['generated_at']}`",
        f"- Task: `{r['task']}`",
        "- Verdict: **BLOCKED** (measured; not NO-GO)",
        f"- Capture dir: `{r['capture_dir']}`",
        f"- Underlyings: {', '.join(r['underlyings'])}",
        f"- Floor met: {r['floor_ok']}",
        "",
        "The capture does not meet the pre-registered heavy-work floor, so no",
        "GO/NO-GO verdict is emitted. Widen the real roster (more expiries x strikes) and/or",
        "extend the surface/perp window toward 7d, then re-run. Do NOT weaken the floor, do",
        "NOT use synthetic data, and do NOT emit NO-GO on under-floor data. Reuse",
        "`scripts/eval60_acquire_three_way.py` (already proven) for fresh real data, e.g.:",
        "",
        "```bash",
        "python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH "
        "--days 7 --max-per-expiry 24 --max-expiry-days 90 "
        "--max-trades-per-instrument 20000 --out-dir data/raw/eval63 --seal",
        "python3 scripts/eval63_orderflow_realized_vol_markpath_extended.py "
        "--capture-dir data/raw/eval63 --seal "
        "--task-label EVAL63-EXTENDED-OFLOW-RV-MARKPATH",
        "```",
        "",
        "## Per-underlying floor",
        "",
    ]
    for inst, fl in r["per_underlying_floor"].items():
        lines.append(f"- {inst}: {json.dumps(fl['checks'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _build_blocked_report(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": r["generated_at"],
        "task": r["task"],
        "verdict": "BLOCKED",
        "capture_dir": r["capture_dir"],
        "underlyings": r["underlyings"],
        "per_underlying_floor": r["per_underlying_floor"],
        "floor": r["floor"],
        "floor_ok": r["floor_ok"],
        "errors": r.get("errors", []),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-63: extended-duration + extended-breadth real options order-flow "
                    "toxicity -> signal-timed delta-hedged ATM straddle (correct mark-path "
                    "net-of-cost P&L)"
    )
    ap.add_argument("--capture-dir", default="data/raw/eval63")
    ap.add_argument("--no-write", action="store_true", help="compute + print, seal nothing")
    ap.add_argument("--seal", action="store_true", help="seal prereg + combined (default)")
    ap.add_argument("--task-label", default="EVAL63-EXTENDED-OFLOW-RV-MARKPATH")
    args = ap.parse_args(argv)

    write = not args.no_write
    try:
        report = run_eval63(
            capture_dir=args.capture_dir, write=write, task_label=args.task_label
        )
    except BaseException as exc:  # noqa: BLE001
        traceback.print_exc()
        if write:
            blocked = _build_blocked_report({
                "generated_at": e62._utc_now_iso(),
                "task": args.task_label,
                "verdict": "BLOCKED",
                "capture_dir": args.capture_dir,
                "underlyings": [],
                "per_underlying_floor": {},
                "floor": build_protocol(args.capture_dir)["floor"],
                "floor_ok": False,
                "errors": [repr(exc)],
            })
            e62._seal(BLOCKED_ID, blocked, build_blocked_md)
        return 1

    print(json.dumps({
        "verdict": report.get("verdict"),
        "floor_ok": report.get("floor_ok"),
        "underlyings": report.get("underlyings"),
        "per_underlying_floor": report.get("per_underlying_floor"),
        "per_underlying": report.get("per_underlying"),
        "overall_pbo": report.get("pooled", {}).get("overall_pbo"),
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
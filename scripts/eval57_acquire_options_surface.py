#!/usr/bin/env python3
"""EVAL-57 acquisition: capture real Deribit **options SURFACE** + **options-venue
ORDER FLOW** + **underlying perpetual** over the **same** ~24h window, synchronized
by construction, for the pure options-native **volatility risk premium /
realized-vs-implied vol net-of-cost** campaign.

The repository charter (``Cryptocurrency-quantitative-options-orderflow-strategy``)
is a quantitative **options** + orderflow strategy evaluated **net of cost**. Every
options+orderflow *fusion* cell (EVAL-46..53) and the options greeks ladder rungs
EVAL-54 (delta-hedged short-vol), EVAL-55 (long-gamma gamma-scalping) and EVAL-56
(term-structure calendar-spread) are sealed ``NO-GO CONFIRMED (PASS)``; re-litigating
fused options+orderflow or EVAL-54/55/56 is prohibited. The unmeasured heavy rung per
the charter is **real options pricing / greeks / vol-surface -> net-of-cost
evaluation**. EVAL-57 is the *volatility risk premium* pure options-native campaign:
it backs real IV out of Deribit option marks, compares to realized vol of the
perpetual, and trades the perpetual delta-hedged to harvest (or fail to harvest, net
of cost) the vol risk premium -- the pure options-native vega/VRP rung not yet
measured, requiring fresh real data (Deribit option trades are ~24h-capped).

Design (why a *single* combined capture file per underlying):

* Surface leg (drives the VRP IV): real Deribit ``get_tradingview_chart_data``
  5m option candles per instrument, assembled into one chain snapshot per 5m bar
  (mirrors the sealed EVAL-48 ``build_snapshots``: ``mark`` = measured 5m candle
  close, ``bid``/``ask`` reconstructed around the mark via the ``constant_fallback``
  spread). This is the real vol surface the VRP IV is backed out of.
* Order-flow leg (kept for the heavy-work floor parity): real Deribit option trades
  via ``get_last_trades_by_instrument_and_time`` (signed aggressor ``direction``,
  ``amount`` in underlying units, ``index_price``, ``iv``). Deribit caps signed trade
  history at ~24h per instrument, so the common window must sit inside the last ~24h.
* Underlying leg (drives the hedge + realized vol): real ``{BTC,ETH}-PERPETUAL``
  ``get_tradingview_chart_data`` 1m candles (Deribit's finest resolution) so the
  measurement can build a genuine 300s hedge grid and compute realized vol.

No synthetic data, no relabelling: every field is a measured Deribit public value.
``schema``/``source`` record the real provenance. Paper-only, public read-only market
data. Writes one capture file per underlying under ``--out-dir`` and, with ``--seal``,
an acquisition manifest into ``research_state/`` (never a GO/verdict). The manifest
records the term-structure viability (≥2 distinct expiries each with a common
strike nearest spot present in ≥100 snapshots) so the VRP measurement can gate on it.

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval57_acquire_options_surface.py
    # full heavy cross-asset synchronized acquisition (+ manifest):
    python3 scripts/eval57_acquire_options_surface.py \
        --underlying BTC --underlying ETH --days 1 \
        --out-dir data/raw/eval57 --seal
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the sealed acquisition primitives (EVAL-48 surface reconstruction, EVAL-51
# order-flow capture, EVAL-52 synchronized helper set). Do not duplicate them, and
# do not edit them.
import scripts.eval48_acquire_deribit_options as acq48  # noqa: E402
import scripts.eval51_acquire_options_orderflow as acq51  # noqa: E402
import scripts.eval52_acquire_synchronized_options as acq52  # noqa: E402
from src.ingestion.deribit import DeribitClient  # noqa: E402

SCHEMA = "deribit_options_surface_capture_v1"
MANIFEST_ID = "EVAL_57_SYNCHRONIZED_ACQUISITION"

# Surface leg is 5m (sealed EVAL-48 cadence; the heavy-work floor is stated in 5m
# bars). Underlying leg is fetched at Deribit's finest resolution (1m) so the
# measurement can build a genuine 300s hedge grid and compute realized vol.
SURFACE_RESOLUTION = acq48.BAR_RESOLUTION          # "5"
SURFACE_BAR_SECONDS = acq48.BAR_SECONDS            # 300
PERP_RESOLUTION = "1"
PERP_BAR_SECONDS = 60

DEFAULT_DAYS = 1.0
DEFAULT_MAX_PER_EXPIRY = 12
DEFAULT_MAX_EXPIRY_DAYS = 45
DEFAULT_MAX_TRADES_PER_INSTRUMENT = 5000
DEFAULT_MIN_QUOTES = 8
DEFAULT_DELAY = 0.12

# Term-structure viability floor (recorded in the acquisition manifest): ≥2 distinct
# expiries each with a common strike nearest spot present in ≥100 snapshots.
TERM_STRUCTURE_MIN_EXPIRIES = 2
TERM_STRUCTURE_MIN_SNAPSHOTS_PER_EXPIRY = 100


def summarize_orderflow(capture: Dict[str, Any]) -> Dict[str, Any]:
    return acq51.summarize(capture)


def _expiry_date(expiry_iso: Any) -> Optional[str]:
    try:
        return str(expiry_iso).strip()[:10]
    except (TypeError, ValueError):
        return None


def _term_structure_viability(capture: Dict[str, Any]) -> Dict[str, Any]:
    """Count, per expiry, snapshots holding a common strike (call+put both quoted)
    nearest to spot. Viable iff >= TERM_STRUCTURE_MIN_EXPIRIES expiries each reach
    TERM_STRUCTURE_MIN_SNAPSHOTS_PER_EXPIRY snapshots."""
    snaps = capture.get("surface", {}).get("snapshots", []) or []
    expiry_counts: Dict[str, int] = {}
    for snap in snaps:
        spot = float(snap.get("spot") or 0.0)
        if spot <= 0.0:
            continue
        quotes = snap.get("quotes") or []
        by_expiry: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for q in quotes:
            exp = _expiry_date(q.get("expiry"))
            if not exp:
                continue
            ot = str(q.get("option_type") or "").lower()
            if ot not in ("call", "put"):
                continue
            by_expiry.setdefault(exp, {}).setdefault(ot, []).append(q)
        for exp, legs in by_expiry.items():
            calls = legs.get("call", [])
            puts = legs.get("put", [])
            common = sorted(
                {float(q.get("strike") or 0.0) for q in calls}
                & {float(q.get("strike") or 0.0) for q in puts}
            )
            if common and spot > 0.0:
                expiry_counts[exp] = expiry_counts.get(exp, 0) + 1
    viable = sorted(
        exp for exp, n in expiry_counts.items()
        if n >= TERM_STRUCTURE_MIN_SNAPSHOTS_PER_EXPIRY
    )
    return {
        "viable": len(viable) >= TERM_STRUCTURE_MIN_EXPIRIES,
        "n_viable_expiries": len(viable),
        "viable_expiries": viable,
        "expiry_snapshot_counts": {exp: expiry_counts.get(exp, 0) for exp in sorted(expiry_counts)},
        "min_snapshots_per_expiry": TERM_STRUCTURE_MIN_SNAPSHOTS_PER_EXPIRY,
        "min_expiries": TERM_STRUCTURE_MIN_EXPIRIES,
    }


def acquire_underlying(
    client: DeribitClient,
    underlying: str,
    start_ms: int,
    end_ms: int,
    out_dir: Path,
    stamp: str,
    *,
    max_per_expiry: int,
    max_expiry_days: int,
    max_trades: int,
    min_quotes: int,
    delay: float,
) -> Dict[str, Any]:
    window_start = datetime.fromtimestamp(start_ms / 1000.0, tz=timezone.utc)
    window_end = datetime.fromtimestamp(end_ms / 1000.0, tz=timezone.utc)
    ref_spot = acq51._spot(client, underlying)

    # One roster for ALL legs (synchronization by construction).
    instruments = acq51.discover_instruments(
        client, underlying, window_start, window_end,
        max_per_expiry, max_expiry_days, ref_spot,
    )
    print(json.dumps({
        "event": "instruments_selected", "underlying": underlying,
        "n": len(instruments), "ref_spot": ref_spot,
        "expiries": sorted({i["expiry"].date().isoformat() for i in instruments}),
    }))

    # ---- Order-flow leg: real signed option trades ----
    trades: List[Dict[str, Any]] = []
    for probe_i, row in enumerate(instruments):
        raw = acq51.fetch_trades_paginated(
            client, row["instrument_name"], start_ms, end_ms, max_trades, delay
        )
        for t in raw:
            trades.append(acq51.normalize_trade(t, row))
        if delay > 0 and probe_i < len(instruments) - 1:
            time.sleep(delay * 0.5)
    trades.sort(key=lambda t: (int(t["ts"]), t["instrument"]))
    print(json.dumps({"event": "orderflow_leg_done", "underlying": underlying,
                      "n_option_trades": len(trades)}))

    # ---- Surface leg: real 5m option candles -> chain snapshots ----
    candles_by_instrument: Dict[str, Dict[int, float]] = {}
    for probe_i, row in enumerate(instruments):
        candle = acq48.fetch_candles(client, row["instrument_name"], start_ms, end_ms)
        if candle:
            candles_by_instrument[row["instrument_name"]] = candle
        if delay > 0 and probe_i < len(instruments) - 1:
            time.sleep(delay)
    step_ms = SURFACE_BAR_SECONDS * 1000
    aligned_start = (start_ms // step_ms) * step_ms
    bar_grid = list(range(aligned_start, end_ms + 1, step_ms))
    built = acq48.build_snapshots(
        candles_by_instrument, instruments, bar_grid, min_quotes, underlying
    )

    # ---- Underlying leg: 1m perpetual candles (finest Deribit resolution) ----
    perp_candles = acq52.fetch_perp_candles(
        client, underlying, start_ms, end_ms, PERP_RESOLUTION
    )

    # Attach causal per-snapshot spot (perpetual close at the snapshot bar).
    snapshots: List[Dict[str, Any]] = []
    for bar_ms, quotes in built:
        snapshots.append({
            "bar_ms": int(bar_ms),
            "spot": acq52._spot_at(perp_candles, int(bar_ms), SURFACE_BAR_SECONDS),
            "quotes": quotes,
        })
    print(json.dumps({"event": "surface_leg_done", "underlying": underlying,
                      "n_snapshots": len(snapshots), "n_perp_candles": len(perp_candles)}))

    capture: Dict[str, Any] = {
        "schema": SCHEMA,
        "underlying": underlying,
        "venue": "deribit",
        "window_start": acq51._iso_ms(start_ms),
        "window_end": acq51._iso_ms(end_ms),
        "perp_resolution": PERP_RESOLUTION,
        "surface": {
            "bar_seconds": SURFACE_BAR_SECONDS,
            "resolution": SURFACE_RESOLUTION,
            "snapshots": snapshots,
        },
        "option_trades": trades,
        "perp_candles": perp_candles,
        "source": {
            "authenticated": False,
            "public_read_only": True,
            "venue": "deribit",
            "endpoints": [
                "/public/get_instruments",
                "/public/get_index_price",
                "/public/get_last_trades_by_instrument_and_time",
                "/public/get_tradingview_chart_data",
            ],
            "surface_note": (
                "surface mark = measured Deribit 5m option chart close; bid/ask "
                "reconstructed around the mark (constant fallback spread); not venue quotes"
            ),
            "orderflow_note": "signed aggressor direction from real Deribit option trades",
            "underlying_note": f"{underlying}-PERPETUAL {PERP_RESOLUTION}m candles",
            "provenance": "real Deribit public market data; no synthetic data",
        },
        "term_structure_viability": _term_structure_viability({
            "surface": {"snapshots": snapshots},
        }),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"options_surface_{underlying}_{stamp}.json"
    path.write_text(json.dumps(capture, separators=(",", ":")))

    surface_summary = acq52.summarize_surface(capture["surface"])
    of_summary = acq51.summarize(capture)
    summary = {
        "underlying": underlying,
        "path": str(path),
        "surface": surface_summary,
        "orderflow": of_summary,
    }
    print(json.dumps({"event": "capture_written", "underlying": underlying,
                      "path": str(path), "surface": surface_summary,
                      "orderflow": of_summary,
                      "term_structure_viability": capture["term_structure_viability"]}))
    return {"capture": capture, "path": path, "summary": summary}


def seal_manifest(
    results: List[Dict[str, Any]], generated_at: str, task_label: str,
    window_start: str, window_end: str,
) -> Dict[str, str]:
    stamp = acq51._stamp_for_filename(generated_at)
    manifest = {
        "manifest_id": MANIFEST_ID,
        "task_id": f"INIT-{generated_at}-{task_label}",
        "generated_at": generated_at,
        "schema": SCHEMA,
        "venue": "deribit",
        "window_start": window_start,
        "window_end": window_end,
        "underlyings": [r["summary"]["underlying"] for r in results],
        "captures": {
            r["summary"]["underlying"]: {
                "path": str(r["path"]),
                "sha256": acq51._sha256(Path(r["path"])),
                **r["summary"],
            }
            for r in results
        },
        "synthetic": False,
        "term_structure_viability": {
            r["summary"]["underlying"]: r["capture"]["term_structure_viability"]
            for r in results
        },
        "provenance": (
            "real Deribit public options surface (5m candles) + options-venue order "
            "flow (signed trades) + perpetual 1m candles; synchronized window; no synthetic data"
        ),
    }
    out = ROOT / "research_state"
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / f"{MANIFEST_ID}_{stamp}.json"
    json_path.write_text(json.dumps(manifest, indent=2, default=str))

    lines = [
        f"# {MANIFEST_ID} — real Deribit synchronized options surface (+ term-structure viability)",
        "",
        f"- Generated: `{generated_at}`",
        f"- Task: `{manifest['task_id']}`",
        f"- Window: `{window_start}` .. `{window_end}`",
        f"- Underlyings: {', '.join(manifest['underlyings'])}",
        f"- Synthetic: **{manifest['synthetic']}**",
        "",
        "## Per-underlying integrity",
        "",
    ]
    for r in results:
        s = r["summary"]
        sf = s["surface"]
        of = s["orderflow"]
        ts = r["capture"]["term_structure_viability"]
        lines += [
            f"### {s['underlying']} (`{s['path']}`)",
            "",
            f"- surface snapshots: {sf['n_snapshots']} / instruments with data {sf['n_instruments_with_data']} / "
            f"quotes {sf['min_quotes_realized']}–{sf['max_quotes_realized']} / 5m bars {sf['n_bars_5m']} / "
            f"span {sf['span_seconds']} s",
            f"- order-flow trades: {of['n_option_trades']} / instruments with trades {of['n_instruments_with_trades']} / "
            f"buy {of['n_buy']} sell {of['n_sell']} / span {of['span_seconds']} s",
            f"- surface non-degenerate: **{sf['non_degenerate']}**; order-flow non-degenerate: **{of['non_degenerate']}**",
            f"- term-structure viability: viable={ts['viable']} "
            f"(n_viable_expiries={ts['n_viable_expiries']}, viable_expiries={ts['viable_expiries']})",
            "",
        ]
    md_path = json_path.with_suffix(".md")
    md_path.write_text("\n".join(lines) + "\n")
    return {"json": str(json_path), "md": str(md_path)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-57 synchronized real Deribit options surface acquisition (+ term-structure viability)"
    )
    ap.add_argument("--underlying", action="append", default=None,
                    help="underlying (repeatable), e.g. BTC ETH")
    ap.add_argument("--days", type=float, default=DEFAULT_DAYS,
                    help="trailing window length in days (default 1; Deribit serves ~24h of trade history)")
    ap.add_argument("--end", default=None, help="window end ISO-8601 UTC (default now)")
    ap.add_argument("--out-dir", default="data/raw/eval57")
    ap.add_argument("--max-per-expiry", type=int, default=DEFAULT_MAX_PER_EXPIRY)
    ap.add_argument("--max-expiry-days", type=int, default=DEFAULT_MAX_EXPIRY_DAYS)
    ap.add_argument("--max-trades-per-instrument", type=int, default=DEFAULT_MAX_TRADES_PER_INSTRUMENT)
    ap.add_argument("--min-quotes", type=int, default=DEFAULT_MIN_QUOTES)
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    ap.add_argument("--seal", action="store_true",
                    help="write an acquisition manifest into research_state/")
    ap.add_argument("--task-label",
                    default="EVAL-57-REAL-OPTIONS-VOL-RISK-PREMIUM-REALIZED-VS-IMPLIED-NET-OF-COST-BTC-ETH")
    args = ap.parse_args(argv)

    underlyings = [u.upper() for u in (args.underlying or ["BTC", "ETH"])]
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    if args.end:
        end_dt = acq51._parse_iso(args.end)
    else:
        end_dt = datetime.now(timezone.utc)
    end_ms = int(end_dt.timestamp() * 1000)
    start_ms = int((end_dt - acq51.timedelta(days=float(args.days))).timestamp() * 1000)

    client = acq51._session_client()
    generated_at = acq51._utc_now_iso()
    stamp = acq51._stamp_for_filename(generated_at)

    results: List[Dict[str, Any]] = []
    for underlying in underlyings:
        results.append(acquire_underlying(
            client, underlying, start_ms, end_ms, out_dir, stamp,
            max_per_expiry=args.max_per_expiry,
            max_expiry_days=args.max_expiry_days,
            max_trades=args.max_trades_per_instrument,
            min_quotes=args.min_quotes,
            delay=args.delay,
        ))

    if args.seal:
        written = seal_manifest(
            results, generated_at, args.task_label,
            acq51._iso_ms(start_ms), acq51._iso_ms(end_ms),
        )
        print(json.dumps({"artifact_paths": written}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback

        traceback.print_exc()
        raise

#!/usr/bin/env python3
"""EVAL-52 acquisition: capture real Deribit **options SURFACE** *and* **options-venue
ORDER FLOW** over the **same** ~24h window, synchronized by construction.

The repository charter is a **combined options + orderflow** strategy
(``Cryptocurrency-quantitative-options-orderflow-strategy``). Every prior rung
falsified one leg or a cross-venue pairing:

* option *candles / surface / greeks* (EVAL-46..49),
* *spot* order flow (trade tape EVAL-43/45, L2 book OFI EVAL-50),
* *options-venue* order flow standalone (EVAL-51).

The **one combination never measured** is the options market's **own surface fused
with its own order flow** -- a *pure options-side* combined strategy, the most
literal reading of "options orderflow strategy". EVAL-52 acquires both legs from
the same venue (Deribit) over the same window so the surface leg (GEX flip / IV
skew term structure / calibration residual) can be causally fused with the
options-venue signed aggressor flow (per-bar ``imbalance`` / ``notional_imbalance``
/ ``call_minus_put``).

Design (why a *single* combined capture file per underlying):

* Both legs are fetched in one run over one window from one instrument roster, so
  synchronization is guaranteed **by construction** -- there is no second file to
  merge and no risk of the two legs drifting onto different windows.
* Surface leg: real Deribit ``get_tradingview_chart_data`` 5m option candles per
  instrument, assembled into one chain snapshot per 5m bar (mirrors the sealed
  EVAL-48 ``build_snapshots``: ``bid``/``ask`` reconstructed around the measured
  ``mark`` via the ``constant_fallback`` spread; historical candles ARE available,
  so this leg is back-fillable over the full window).
* Order-flow leg: real Deribit option trades via
  ``get_last_trades_by_instrument_and_time`` (signed aggressor ``direction``,
  ``amount`` in underlying units, ``index_price``, ``iv``). Deribit caps signed
  trade history at ~24h per instrument, so the common window must sit inside the
  last ~24h.
* Underlying leg: real ``{BTC,ETH}-PERPETUAL`` ``get_tradingview_chart_data``
  1m candles (Deribit's finest resolution) so the measurement can build genuine
  60s and 300s return grids.

No synthetic data, no relabelling: every field is a measured Deribit public value.
``schema``/``source`` record the real provenance. Paper-only, public read-only
market data. Writes one capture file per underlying under ``--out-dir`` and, with
``--seal``, an acquisition manifest into ``research_state/`` (never a GO/verdict).

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval52_acquire_synchronized_options.py
    # full heavy cross-asset synchronized acquisition (+ manifest):
    python3 scripts/eval52_acquire_synchronized_options.py \
        --underlying BTC --underlying ETH --days 1 \
        --out-dir data/raw/eval52 --seal
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

# Reuse the sealed EVAL-51 order-flow acquisition helpers and the sealed EVAL-48
# surface reconstruction helpers. Do not duplicate them.
import scripts.eval48_acquire_deribit_options as acq48  # noqa: E402
import scripts.eval51_acquire_options_orderflow as acq51  # noqa: E402
from src.ingestion.deribit import DeribitClient  # noqa: E402

SCHEMA = "deribit_options_surface_orderflow_capture_v1"
MANIFEST_ID = "EVAL_52_SYNCHRONIZED_ACQUISITION"

# Surface leg is 5m (sealed EVAL-48 cadence; the heavy-work floor is stated in 5m
# bars). Underlying leg is fetched at Deribit's finest resolution (1m) so the
# measurement can build genuine 60s and 300s return grids.
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


def _iso_ms(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_perp_candles(
    client: DeribitClient,
    underlying: str,
    start_ms: int,
    end_ms: int,
    resolution: str = PERP_RESOLUTION,
) -> List[Dict[str, Any]]:
    """Return ``[{ts, open, high, low, close}]`` for the underlying perpetual."""
    try:
        data = client._get(
            "/public/get_tradingview_chart_data",
            {
                "instrument_name": f"{underlying}-PERPETUAL",
                "start_timestamp": int(start_ms),
                "end_timestamp": int(end_ms),
                "resolution": resolution,
            },
        )
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"event": "perp_candles_failed", "underlying": underlying,
                          "error": str(exc)}))
        return []
    result = data.get("result") if isinstance(data, dict) else None
    if not isinstance(result, dict) or result.get("status") != "ok":
        return []
    ticks = result.get("ticks") or []
    opens = result.get("open") or []
    highs = result.get("high") or []
    lows = result.get("low") or []
    closes = result.get("close") or []
    out: List[Dict[str, Any]] = []
    for i, tick in enumerate(ticks):
        if i >= len(closes):
            break
        try:
            out.append({
                "ts": int(tick),
                "open": float(opens[i]) if i < len(opens) else 0.0,
                "high": float(highs[i]) if i < len(highs) else 0.0,
                "low": float(lows[i]) if i < len(lows) else 0.0,
                "close": float(closes[i]),
            })
        except (TypeError, ValueError):
            continue
    out.sort(key=lambda c: c["ts"])
    return out


def _spot_at(perp_candles: List[Dict[str, Any]], bar_ms: int, bar_seconds: int) -> Optional[float]:
    """Last perpetual close at or before the close of the ``bar_seconds`` bar at ``bar_ms``."""
    cutoff = int(bar_ms) + int(bar_seconds) * 1000
    best: Optional[float] = None
    for c in perp_candles:
        if int(c["ts"]) <= cutoff:
            px = float(c.get("close") or 0.0)
            if px > 0:
                best = px
        else:
            break
    return best


def summarize_surface(surface: Dict[str, Any]) -> Dict[str, Any]:
    snaps = surface.get("snapshots", [])
    quotes_counts = [len(s.get("quotes", [])) for s in snaps]
    bar_ms = [int(s["bar_ms"]) for s in snaps]
    n_inst = len({q.get("symbol") for s in snaps for q in s.get("quotes", [])})
    span = ((max(bar_ms) - min(bar_ms)) / 1000.0) if len(bar_ms) >= 2 else 0.0
    n_bars_5m = (span // SURFACE_BAR_SECONDS) if span > 0 else 0
    return {
        "n_snapshots": len(snaps),
        "n_instruments_with_data": int(n_inst),
        "min_quotes_realized": int(min(quotes_counts)) if quotes_counts else 0,
        "max_quotes_realized": int(max(quotes_counts)) if quotes_counts else 0,
        "span_seconds": round(span, 3),
        "n_bars_5m": int(n_bars_5m),
        "non_degenerate": bool(snaps and n_inst >= 1 and span > 0),
    }


def summarize_orderflow(capture: Dict[str, Any]) -> Dict[str, Any]:
    return acq51.summarize(capture)


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

    # One roster for BOTH legs (synchronization by construction).
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
    bar_grid = list(range(start_ms, end_ms + 1, SURFACE_BAR_SECONDS * 1000))
    built = acq48.build_snapshots(
        candles_by_instrument, instruments, bar_grid, min_quotes, underlying
    )

    # ---- Underlying leg: 1m perpetual candles (finest Deribit resolution) ----
    perp_candles = fetch_perp_candles(client, underlying, start_ms, end_ms, PERP_RESOLUTION)

    # Attach causal per-snapshot spot (perpetual close at the snapshot bar).
    snapshots: List[Dict[str, Any]] = []
    for bar_ms, quotes in built:
        snapshots.append({
            "bar_ms": int(bar_ms),
            "spot": _spot_at(perp_candles, int(bar_ms), SURFACE_BAR_SECONDS),
            "quotes": quotes,
        })
    print(json.dumps({"event": "surface_leg_done", "underlying": underlying,
                      "n_snapshots": len(snapshots), "n_perp_candles": len(perp_candles)}))

    capture: Dict[str, Any] = {
        "schema": SCHEMA,
        "underlying": underlying,
        "venue": "deribit",
        "window_start": _iso_ms(start_ms),
        "window_end": _iso_ms(end_ms),
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
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"options_surface_orderflow_{underlying}_{stamp}.json"
    path.write_text(json.dumps(capture, separators=(",", ":")))

    surface_summary = summarize_surface(capture["surface"])
    of_summary = acq51.summarize(capture)
    summary = {
        "underlying": underlying,
        "path": str(path),
        "surface": surface_summary,
        "orderflow": of_summary,
    }
    print(json.dumps({"event": "capture_written", "underlying": underlying,
                      "path": str(path), "surface": surface_summary,
                      "orderflow": of_summary}))
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
        f"# {MANIFEST_ID} — real Deribit synchronized options surface x options order flow",
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
        lines += [
            f"### {s['underlying']} (`{s['path']}`)",
            "",
            f"- surface snapshots: {sf['n_snapshots']} / instruments with data {sf['n_instruments_with_data']} / "
            f"quotes {sf['min_quotes_realized']}–{sf['max_quotes_realized']} / 5m bars {sf['n_bars_5m']} / "
            f"span {sf['span_seconds']} s",
            f"- order-flow trades: {of['n_option_trades']} / instruments with trades {of['n_instruments_with_trades']} / "
            f"buy {of['n_buy']} sell {of['n_sell']} / span {of['span_seconds']} s",
            f"- surface non-degenerate: **{sf['non_degenerate']}**; order-flow non-degenerate: **{of['non_degenerate']}**",
            "",
        ]
    md_path = json_path.with_suffix(".md")
    md_path.write_text("\n".join(lines) + "\n")
    return {"json": str(json_path), "md": str(md_path)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-52 synchronized real Deribit options surface x options order-flow acquisition"
    )
    ap.add_argument("--underlying", action="append", default=None,
                    help="underlying (repeatable), e.g. BTC ETH")
    ap.add_argument("--days", type=float, default=DEFAULT_DAYS,
                    help="trailing window length in days (default 1; Deribit serves ~24h of trade history)")
    ap.add_argument("--end", default=None, help="window end ISO-8601 UTC (default now)")
    ap.add_argument("--out-dir", default="data/raw/eval52")
    ap.add_argument("--max-per-expiry", type=int, default=DEFAULT_MAX_PER_EXPIRY)
    ap.add_argument("--max-expiry-days", type=int, default=DEFAULT_MAX_EXPIRY_DAYS)
    ap.add_argument("--max-trades-per-instrument", type=int, default=DEFAULT_MAX_TRADES_PER_INSTRUMENT)
    ap.add_argument("--min-quotes", type=int, default=DEFAULT_MIN_QUOTES)
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    ap.add_argument("--seal", action="store_true",
                    help="write an acquisition manifest into research_state/")
    ap.add_argument("--task-label",
                    default="EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION")
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
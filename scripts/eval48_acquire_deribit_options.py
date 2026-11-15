#!/usr/bin/env python3
"""EVAL-48 acquisition: reconstruct real Deribit BTC option-chain snapshots.

This is the venue-specificity acquisition for the combined options+orderflow
campaign. EVAL-46 (BTC) and EVAL-47 (ETH) sealed ``NO-GO CONFIRMED (PASS)`` on
OKX-only data (OKX options + OKX orderflow). EVAL-48 changes the *options*
venue to Deribit (the dominant crypto options venue) while keeping the exact
same real OKX orderflow tapes, isolating the options-venue effect.

The sealed EVAL-46 pipeline (``scripts/eval46_integrated_options_orderflow_audit.py``)
consumes per-snapshot option-chain JSON exports discovered by
``discover_all_real_options_exports`` (filename ``options_<venue>_<UNDERLYING>_<stamp>.json``).
This script fetches **real** Deribit public ``get_tradingview_chart_data`` 5m
candles for every BTC option instrument that was live during the target window,
reconstructs one chain snapshot per 5m bar, and writes them in the exact schema
the pipeline already loads (mark prices, reconstructed bid/ask around the
close — mirroring the OKX ``constant_fallback`` spread — plus strike / expiry /
option_type).  No synthetic data, no relabelling: every price is a measured
Deribit candle close; ``source.derived_from`` records the real provenance.

Paper-only, public read-only market data, polite rate limiting.  Never writes to
``research_state/`` except an acquisition manifest (never a GO/verdict).

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval48_acquire_deribit_options.py
    # tiny smoke (writes to a temp dir):
    python3 scripts/eval48_acquire_deribit_options.py \
        --start 2026-11-14T13:20:00Z --end 2026-11-14T13:40:00Z \
        --out-dir /tmp/eval48_smoke --max-per-expiry 6
    # full acquisition into the git-tracked data dir:
    python3 scripts/eval48_acquire_deribit_options.py \
        --start 2026-11-14T09:00:00Z --end 2026-11-14T20:00:00Z \
        --out-dir data/raw/eval48 --seal
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ingestion.deribit import (  # noqa: E402
    DeribitClient,
    _parse_deribit_instrument,
)

REFERENCE_SPOT = 66825.3  # sealed BTC reference spot (EVAL-23/24/41/46)
SCHEMA = "deribit_public_tradingview_chart_reconstruction_v1"
MANIFEST_ID = "EVAL_48_DERIBIT_ACQUISITION"
BAR_RESOLUTION = "5"
BAR_SECONDS = 300
DEFAULT_MIN_QUOTES = 8
DEFAULT_MAX_PER_EXPIRY = 25
DEFAULT_DELAY = 0.15
# Expiries to reconstruct. Default brackets the OKX BTC option window (which used
# 20NOV26/27NOV26) plus the nearest daily (15NOV26) for term-structure variation.
DEFAULT_EXPIRIES = ("2026-11-15", "2026-11-20", "2026-11-27")

# constant relative half-spread used to reconstruct bid/ask around the mark,
# mirroring the OKX backfill's ``constant_fallback`` spread (bid = 0.99*mark,
# ask = 1.01*mark) so ``_mid_price`` recovers the measured close.
SPREAD_HALF = 0.01


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    # drop microseconds, then strip separators -> e.g. 20261115T081500Z
    base = iso_ts.split(".")[0]
    return base.replace("-", "").replace(":", "").replace("+0000", "Z")


def _parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _floor_bar(dt: datetime) -> datetime:
    epoch = int(dt.timestamp())
    floored = epoch - (epoch % BAR_SECONDS)
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def discover_instruments(
    client: DeribitClient,
    underlying: str,
    window_start: datetime,
    window_end: datetime,
    max_per_expiry: int,
    ref_spot: Optional[float],
    expiries: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Return option instruments live during the window, nearest-to-spot strikes first.

    Combines live (``expired=False``) and expired (``expired=True``) instruments so
    that expiries which rolled off during/just after the window are still covered.
    Selection is capped to ``max_per_expiry`` nearest strikes per expiry (calls and
    puts are both kept so call/put pairs exist for the parity forward fit). When
    ``expiries`` (ISO ``YYYY-MM-DD`` dates) is given, only those expiry dates are kept.
    When ``ref_spot`` is ``None`` the anchor is the **median strike** of all discovered
    instruments, which is the correct near-the-money anchor for any underlying (BTC
    ~66k, ETH ~3.5k) without hard-coding a per-coin spot.
    """
    expiry_filter = set(expiries) if expiries else None
    names: set[str] = set()
    for expired in (False, True):
        try:
            for inst in client.get_instruments(underlying, kind="option", expired=expired):
                nm = inst.get("instrument_name") or inst.get("instrument")
                if nm:
                    names.add(nm)
        except Exception as exc:  # noqa: BLE001 - record and continue
            print(json.dumps({"event": "get_instruments_failed", "expired": expired,
                              "error": str(exc)}))

    parsed: List[Dict[str, Any]] = []
    for nm in names:
        info = _parse_deribit_instrument(nm)
        if not info or info["underlying"] != underlying:
            continue
        expiry: datetime = info["expiry"]
        # keep only options that were live at some point during the window
        if expiry < window_start:
            continue
        if expiry_filter is not None and expiry.date().isoformat() not in expiry_filter:
            continue
        parsed.append({
            "instrument_name": nm,
            "expiry": expiry,
            "strike": float(info["strike"]),
            "option_type": str(info["option_type"]).lower(),
        })

    # group by expiry date (day) and keep nearest strikes to the anchor spot
    if ref_spot is None:
        strikes = [row["strike"] for row in parsed]
        ref_spot = sorted(strikes)[len(strikes) // 2] if strikes else 0.0
    by_expiry: Dict[str, List[Dict[str, Any]]] = {}
    for row in parsed:
        by_expiry.setdefault(row["expiry"].date().isoformat(), []).append(row)

    selected: List[Dict[str, Any]] = []
    for _day, rows in sorted(by_expiry.items()):
        rows.sort(key=lambda r: abs(r["strike"] - ref_spot))
        selected.extend(rows[:max_per_expiry])
    selected.sort(key=lambda r: (r["expiry"], r["strike"], r["option_type"]))
    return selected


def fetch_candles(
    client: DeribitClient,
    instrument_name: str,
    start_ms: int,
    end_ms: int,
) -> Optional[Dict[int, float]]:
    """Return ``{bar_start_ms: close}`` for one instrument, or ``None`` on no data."""
    try:
        data = client._get(
            "/public/get_tradingview_chart_data",
            {
                "instrument_name": instrument_name,
                "start_timestamp": start_ms,
                "end_timestamp": end_ms,
                "resolution": BAR_RESOLUTION,
            },
        )
    except Exception:  # noqa: BLE001 - skip instrument
        return None
    result = data.get("result") if isinstance(data, dict) else None
    if not isinstance(result, dict):
        return None
    if result.get("status") != "ok":
        return None
    ticks = result.get("ticks") or []
    closes = result.get("close") or []
    if not ticks or len(ticks) != len(closes):
        return None
    out: Dict[int, float] = {}
    for tick, close in zip(ticks, closes):
        try:
            out[int(tick)] = float(close)
        except Exception:  # noqa: BLE001
            continue
    return out or None


def build_snapshots(
    candles_by_instrument: Dict[str, Dict[int, float]],
    instruments: List[Dict[str, Any]],
    bar_grid: List[int],
    min_quotes: int,
    underlying: str,
) -> List[Tuple[int, List[Dict[str, Any]]]]:
    """Assemble per-bar snapshots from per-instrument candle maps.

    Each snapshot is the set of instruments that have a candle at that 5m bar.
    Snapshots below ``min_quotes`` are dropped. Quotes carry a reconstructed
    bid/ask around the measured mark (so ``_mid_price`` recovers the close).
    """
    by_name = {row["instrument_name"]: row for row in instruments}
    snapshots: List[Tuple[int, List[Dict[str, Any]]]] = []
    for bar_ms in bar_grid:
        quotes: List[Dict[str, Any]] = []
        for name, candle in candles_by_instrument.items():
            mark = candle.get(bar_ms)
            if mark is None or not math.isfinite(mark) or mark < 0.0:
                continue
            row = by_name.get(name)
            if row is None:
                continue
            bid = mark * (1.0 - SPREAD_HALF)
            ask = mark * (1.0 + SPREAD_HALF)
            expiry_iso = row["expiry"].astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            ts_iso = datetime.fromtimestamp(bar_ms / 1000.0, tz=timezone.utc).isoformat().replace("+00:00", "Z")
            quotes.append({
                "symbol": name,
                "underlying": underlying,
                "strike": float(row["strike"]),
                "expiry": expiry_iso,
                "option_type": row["option_type"],
                "contract_size": 1.0,
                "bid": bid,
                "ask": ask,
                "last": mark,
                "mark": mark,
                "bid_iv": None,
                "ask_iv": None,
                "mark_iv": None,
                "delta": None,
                "gamma": None,
                "theta": None,
                "vega": None,
                "open_interest": 0.0,
                "volume": 0.0,
                "timestamp": ts_iso,
                "candle_bar": "5m",
                "price_unit": "btc_per_1btc",
                "price_mode": "deribit_option_chart_close_reconstructed_spread",
                "spread_source": "constant_fallback",
                "venue": "deribit",
            })
        if len(quotes) >= min_quotes:
            snapshots.append((bar_ms, quotes))
    return snapshots


def write_snapshot(
    out_dir: Path,
    underlying: str,
    bar_ms: int,
    quotes: List[Dict[str, Any]],
    spot: Optional[float] = None,
) -> Path:
    ts = datetime.fromtimestamp(bar_ms / 1000.0, tz=timezone.utc)
    stamp = ts.strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"options_deribit_{underlying}_{stamp}.json"
    payload = {
        "acquired_at": ts.isoformat().replace("+00:00", "Z"),
        "underlying": underlying,
        "venue": "deribit",
        "schema": SCHEMA,
        "quotes": quotes,
        "source": {
            "authenticated": False,
            "public_read_only": True,
            "venue": "deribit",
            "candle_bar": "5m",
            "derived_from": "deribit_tradingview_chart_data",
            "endpoints": ["/public/get_instruments", "/public/get_tradingview_chart_data"],
            "price_mode": "deribit_option_chart_close_reconstructed_spread",
            "spread_source": "constant_fallback",
            "note": "mark = measured 5m chart close; bid/ask reconstructed around the mark (constant fallback spread); not venue quotes",
        },
    }
    if spot is not None and math.isfinite(float(spot)) and float(spot) > 0.0:
        payload["spot"] = float(spot)
        payload["source"]["spot_source"] = f"deribit_{underlying}-PERPETUAL_5m_close"
    with path.open("w") as fh:
        json.dump(payload, fh, sort_keys=True)
    return path


def _sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def seal_manifest(
    out_dir: Path,
    manifest: Dict[str, Any],
    generated_at: str,
    task_label: str,
    manifest_id: str = MANIFEST_ID,
) -> Dict[str, str]:
    stamp = _stamp_for_filename(generated_at)
    json_path = ROOT / "research_state" / f"{manifest_id}_{stamp}.json"
    md_path = json_path.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = dict(manifest)
    manifest["task_id"] = f"INIT-{generated_at}-{task_label}"
    with json_path.open("w") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)

    lines = [
        f"# {manifest_id} — Deribit {manifest.get('underlying', 'BTC')} option-chain reconstruction",
        "",
        f"- **Generated:** {generated_at}",
        f"- **Task:** {manifest['task_id']}",
        f"- **Underlying:** {manifest['underlying']}",
        f"- **Window:** {manifest['window_start']} .. {manifest['window_end']}",
        f"- **Snapshots written:** {manifest['n_snapshots']}",
        f"- **Instruments with data:** {manifest['n_instruments_with_data']} / {manifest['n_instruments_probed']}",
        f"- **Min quotes/snapshot (gate):** {manifest['min_quotes']}  (realized min {manifest['min_quotes_realized']}, max {manifest['max_quotes_realized']})",
        f"- **Per-expiry instruments:** {json.dumps(manifest['per_expiry_counts'])}",
        f"- **Provenance:** real Deribit public `get_tradingview_chart_data` 5m closes; no synthetic data.",
        "",
        "Paper-only, public read-only market data. This is an acquisition manifest, not a verdict.",
    ]
    md_path.write_text("\n".join(lines) + "\n")
    return {"json": str(json_path), "md": str(md_path)}


def acquire(
    underlying: str = "BTC",
    start: str = "2026-11-14T09:00:00Z",
    end: str = "2026-11-14T20:00:00Z",
    out_dir: str = "data/raw/eval48",
    max_per_expiry: int = DEFAULT_MAX_PER_EXPIRY,
    min_quotes: int = DEFAULT_MIN_QUOTES,
    delay: float = DEFAULT_DELAY,
    expiries: Optional[List[str]] = None,
    ref_spot: Optional[float] = None,
    seal: bool = False,
    task_label: str = "EVAL-48-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL",
    manifest_id: str = MANIFEST_ID,
) -> Dict[str, Any]:
    window_start = _floor_bar(_parse_iso(start))
    window_end = _parse_iso(end)
    start_ms = int(window_start.timestamp() * 1000)
    end_ms = int(window_end.timestamp() * 1000)

    out_path = Path(out_dir)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.mkdir(parents=True, exist_ok=True)

    client = DeribitClient()
    instruments = discover_instruments(
        client, underlying, window_start, window_end, max_per_expiry, ref_spot,
        expiries=expiries,
    )
    print(json.dumps({"event": "instruments_selected", "n": len(instruments),
                      "expiries": sorted({i["expiry"].date().isoformat() for i in instruments})}))

    candles_by_instrument: Dict[str, Dict[int, float]] = {}
    probed = 0
    for row in instruments:
        probed += 1
        candle = fetch_candles(client, row["instrument_name"], start_ms, end_ms)
        if candle:
            candles_by_instrument[row["instrument_name"]] = candle
        if delay > 0 and probed < len(instruments):
            time.sleep(delay)

    bar_grid: List[int] = list(range(start_ms, end_ms + 1, BAR_SECONDS * 1000))
    snapshots = build_snapshots(
        candles_by_instrument, instruments, bar_grid, min_quotes, underlying
    )

    # Measured causal spot proxy per 5m bar (underlying perpetual close). The
    # sealed signal loader defaults to a BTC REFERENCE_SPOT unless a spot is
    # supplied, which makes the per-snapshot signal degenerate for non-BTC
    # underlyings; storing the real per-bar spot lets the wrapper pass it through.
    spot_by_bar: Dict[int, float] = (
        fetch_candles(client, f"{underlying}-PERPETUAL", start_ms, end_ms) or {}
    )

    written: List[str] = []
    quotes_realized: List[int] = []
    last_spot: Optional[float] = None
    for bar_ms, quotes in snapshots:
        if bar_ms in spot_by_bar:
            last_spot = spot_by_bar[bar_ms]
        path = write_snapshot(out_path, underlying, bar_ms, quotes, spot=last_spot)
        written.append(str(path))
        quotes_realized.append(len(quotes))

    per_expiry: Dict[str, int] = {}
    for name in candles_by_instrument:
        row = next((r for r in instruments if r["instrument_name"] == name), None)
        if row:
            day = row["expiry"].date().isoformat()
            per_expiry[day] = per_expiry.get(day, 0) + 1

    manifest = {
        "report_id": manifest_id,
        "underlying": underlying,
        "window_start": window_start.isoformat().replace("+00:00", "Z"),
        "window_end": window_end.isoformat().replace("+00:00", "Z"),
        "out_dir": str(out_path),
        "n_snapshots": len(written),
        "n_instruments_probed": probed,
        "n_instruments_with_data": len(candles_by_instrument),
        "min_quotes": min_quotes,
        "min_quotes_realized": min(quotes_realized) if quotes_realized else 0,
        "max_quotes_realized": max(quotes_realized) if quotes_realized else 0,
        "per_expiry_counts": per_expiry,
        "snapshot_files": written,
        "schema": SCHEMA,
        "provenance": "real Deribit public get_tradingview_chart_data 5m closes; no synthetic data",
    }
    if spot_by_bar:
        spots = list(spot_by_bar.values())
        manifest["spot_source"] = f"deribit_{underlying}-PERPETUAL_5m_close"
        manifest["spot_min"] = float(min(spots))
        manifest["spot_max"] = float(max(spots))

    generated_at = _utc_now_iso()
    artifact_paths: Dict[str, str] = {}
    if seal and written:
        manifest["generated_at"] = generated_at
        manifest["sha256"] = {Path(p).name: _sha256(Path(p)) for p in written}
        artifact_paths = seal_manifest(out_path, manifest, generated_at, task_label, manifest_id=manifest_id)
        manifest["artifact_paths"] = artifact_paths

    return manifest


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-48 Deribit BTC option snapshot acquisition")
    ap.add_argument("--underlying", default="BTC")
    ap.add_argument("--start", default="2026-11-14T09:00:00Z")
    ap.add_argument("--end", default="2026-11-14T20:00:00Z")
    ap.add_argument("--out-dir", default="data/raw/eval48")
    ap.add_argument("--max-per-expiry", type=int, default=DEFAULT_MAX_PER_EXPIRY)
    ap.add_argument("--min-quotes", type=int, default=DEFAULT_MIN_QUOTES)
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    ap.add_argument("--expiries", default=",".join(DEFAULT_EXPIRIES),
                    help="comma-separated ISO expiry dates (YYYY-MM-DD) to reconstruct")
    ap.add_argument("--ref-spot", type=float, default=None,
                    help="anchor spot for nearest-strike selection (default: median strike, correct for any underlying)")
    ap.add_argument("--seal", action="store_true", help="write an acquisition manifest to research_state/")
    ap.add_argument("--manifest-id", default=MANIFEST_ID,
                    help="report_id/filename stem for the sealed manifest (default: EVAL_48_DERIBIT_ACQUISITION)")
    args = ap.parse_args(argv)

    expiry_list = [e.strip() for e in args.expiries.split(",") if e.strip()] or None
    manifest = acquire(
        underlying=args.underlying,
        start=args.start,
        end=args.end,
        out_dir=args.out_dir,
        max_per_expiry=args.max_per_expiry,
        min_quotes=args.min_quotes,
        delay=args.delay,
        expiries=expiry_list,
        ref_spot=args.ref_spot,
        seal=args.seal,
        manifest_id=args.manifest_id,
    )
    print(json.dumps({k: manifest[k] for k in (
        "n_snapshots", "n_instruments_probed", "n_instruments_with_data",
        "min_quotes_realized", "max_quotes_realized", "per_expiry_counts",
        "window_start", "window_end", "out_dir",
    )}, sort_keys=True))
    if manifest.get("artifact_paths"):
        print(json.dumps({"artifact_paths": manifest["artifact_paths"]}, sort_keys=True))
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
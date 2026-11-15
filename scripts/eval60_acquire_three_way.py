#!/usr/bin/env python3
"""POST-EVAL / EVAL-60 acquisition: the synchronized **three-way** real-data capture
that fuses the options market's **own surface** + the options market's **own order
flow** + the **underlying perpetual order flow**, all over the same ~24h window.

Repository charter
------------------
``Cryptocurrency-quantitative-options-orderflow-strategy`` is a **combined OPTIONS
+ ORDERFLOW** strategy. Every EVAL-02..59 cell is sealed ``NO-GO CONFIRMED (PASS)``.
The genuinely untested on-charter cell is the **three-way fusion**:

  * Deribit options **SURFACE** (5m option candles -> chain snapshots -> greeks/IV),
  * Deribit options-venue **ORDER FLOW** (signed aggressor option trades), and
  * **OKX perpetual** ORDER FLOW (real ``history-trades`` signed taker flow),

synchronized on one 5m bar grid so the measurement can causally fuse all three legs
net-of-cost. EVAL-48/49 already did Deribit-options x OKX-orderflow; EVAL-52/53
already did Deribit-surface x Deribit-options-venue-orderflow. This script captures
the missing third leg (OKX perp order flow) *inside the same synchronized window* so
the three-way cell can finally be measured.

Reuse (no duplication)
----------------------
* Deribit legs reuse the sealed EVAL-48 surface helpers (``build_snapshots``,
  ``fetch_candles``) and EVAL-51 order-flow helpers (``discover_instruments``,
  ``fetch_trades_paginated``, ``normalize_trade``, ``summarize``) plus the EVAL-52
  perpetual-candle fetcher -- identical to the sealed EVAL-52 acquisition.
* The OKX perp order-flow leg is a **new** real capture: OKX public
  ``GET /api/v5/market/history-trades`` (the correct historical-trades endpoint;
  ``trades-history`` is 404) paginated **backwards** by ``after=<oldest tradeId>``
  until the window start is covered, deduplicated by ``tradeId``.

No synthetic data, no relabelling: every field is a measured public value.
``schema``/``source`` record real provenance. Paper-only, public read-only network.
Writes one capture file per underlying under ``--out-dir`` and, with ``--seal``, an
acquisition manifest into ``research_state/`` (never a GO/verdict).

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval60_acquire_three_way.py
    # short smoke (BTC only, tiny OKX cap; writes to a temp dir, no manifest):
    python3 scripts/eval60_acquire_three_way.py \
        --underlying BTC --days 0.02 --max-okx-pages 5 \
        --out-dir /tmp/eval60_smoke
    # full heavy cross-asset synchronized three-way capture (+ manifest):
    python3 scripts/eval60_acquire_three_way.py \
        --underlying BTC --underlying ETH --days 1 \
        --out-dir data/raw/eval60 --seal
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

# Reuse the sealed EVAL-48 / EVAL-51 / EVAL-52 helpers; do not duplicate them.
import scripts.eval48_acquire_deribit_options as acq48  # noqa: E402
import scripts.eval51_acquire_options_orderflow as acq51  # noqa: E402
import scripts.eval52_acquire_synchronized_options as acq52  # noqa: E402
from src.ingestion.deribit import DeribitClient  # noqa: E402

SCHEMA = "three_way_options_surface_orderflow_okx_perp_capture_v1"
MANIFEST_ID = "POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION"
VENUE = "deribit+okx"

# Surface leg is 5m (sealed EVAL-48 cadence; heavy-work floor is stated in 5m bars).
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

# OKX perpetual swap per underlying (real, public, read-only).
OKX_INST = {"BTC": "BTC-USD-SWAP", "ETH": "ETH-USD-SWAP"}
OKX_HISTORY_URL = "https://www.okx.com/api/v5/market/history-trades"
OKX_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
DEFAULT_MAX_OKX_PAGES = 6000
DEFAULT_OKX_DELAY = 0.12
OKX_PAGE_LIMIT = 100


# ---------------------------------------------------------------------------
# OKX perp order-flow leg (real history-trades, paginated backwards by tradeId)
# ---------------------------------------------------------------------------
def _okx_session():
    import requests  # local import so --help works without deps

    s = requests.Session()
    s.headers.update({"User-Agent": OKX_USER_AGENT, "Accept": "application/json"})
    return s


def fetch_okx_perp_trades(
    session,
    inst_id: str,
    start_ms: int,
    end_ms: int,
    *,
    max_pages: int = DEFAULT_MAX_OKX_PAGES,
    delay: float = DEFAULT_OKX_DELAY,
) -> List[Dict[str, Any]]:
    """Return real OKX perpetual trades in ``[start_ms, end_ms]``.

    OKX ``history-trades`` returns up to 100 rows per page in **reverse** order.
    Pagination walks **backwards in time** by passing ``after=<oldest tradeId>`` of
    the current page; the boundary trade is repeated so we dedupe by ``tradeId``.
    We stop once the oldest observed ts drops below ``start_ms`` (window covered), an
    empty page arrives, or a page yields no *new* tradeIds (retention wall).
    """
    out: Dict[int, Dict[str, Any]] = {}
    cursor: Optional[str] = None
    oldest_ts = end_ms
    for _ in range(max(1, int(max_pages))):
        params: Dict[str, Any] = {"instId": inst_id, "limit": str(OKX_PAGE_LIMIT)}
        if cursor is not None:
            params["after"] = cursor
        try:
            resp = session.get(OKX_HISTORY_URL, params=params, timeout=12)
            if resp.status_code != 200:
                break
            payload = resp.json()
        except Exception as exc:  # noqa: BLE001 - a transient page error ends the walk
            print(json.dumps({"event": "okx_page_error", "inst_id": inst_id, "error": str(exc)}))
            break
        if str(payload.get("code")) != "0":
            break
        rows = payload.get("data") or []
        if not rows:
            break
        new_this_page = 0
        page_oldest_ts = end_ms
        page_oldest_tid: Optional[str] = None
        for r in rows:
            try:
                tid = str(r.get("tradeId"))
                ts = int(r["ts"])
                px = float(r.get("px") or 0.0)
                sz = abs(float(r.get("sz") or 0.0))
            except (KeyError, TypeError, ValueError):
                continue
            try:
                tid_key = int(tid)
            except ValueError:
                tid_key = ts
            if ts < int(start_ms) or ts > int(end_ms):
                # still track the oldest tradeId for pagination even if out of window
                if ts < page_oldest_ts:
                    page_oldest_ts = ts
                    page_oldest_tid = tid
                continue
            if tid_key not in out:
                out[tid_key] = {
                    "ts": ts,
                    "px": px,
                    "sz": sz,
                    "side": str(r.get("side") or "").lower(),
                    "instrument": inst_id,
                    "trade_id": tid,
                }
                new_this_page += 1
            if ts < page_oldest_ts:
                page_oldest_ts = ts
                page_oldest_tid = tid
        if new_this_page == 0:
            break  # retention wall / no forward progress
        oldest_ts = min(oldest_ts, page_oldest_ts)
        if page_oldest_tid is None:
            break
        cursor = page_oldest_tid
        if oldest_ts < int(start_ms):
            break  # window fully covered
        if delay > 0:
            time.sleep(float(delay))

    trades = sorted(out.values(), key=lambda t: (int(t["ts"]), str(t.get("trade_id"))))
    print(json.dumps({
        "event": "okx_perp_orderflow_leg_done",
        "inst_id": inst_id,
        "n_okx_perp_trades": len(trades),
        "oldest_ts_ms": int(trades[0]["ts"]) if trades else None,
        "newest_ts_ms": int(trades[-1]["ts"]) if trades else None,
    }))
    return trades


def summarize_okx_perp(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Integrity / non-degeneracy summary of the OKX perp order-flow leg."""
    n = len(trades)
    if n == 0:
        return {
            "n_okx_perp_trades": 0, "n_buy": 0, "n_sell": 0,
            "span_seconds": 0.0, "n_bars_5m": 0, "non_degenerate": False,
        }
    ts = [int(t["ts"]) for t in trades]
    span = (max(ts) - min(ts)) / 1000.0
    n_buy = sum(1 for t in trades if str(t.get("side")) == "buy")
    n_sell = sum(1 for t in trades if str(t.get("side")) == "sell")
    return {
        "n_okx_perp_trades": int(n),
        "n_buy": int(n_buy),
        "n_sell": int(n_sell),
        "span_seconds": round(span, 3),
        "n_bars_5m": int(span // 300.0) if span > 0 else 0,
        "non_degenerate": bool(n >= 2 and span > 0 and (n_buy > 0 and n_sell > 0)),
    }


# ---------------------------------------------------------------------------
# Per-underlying synchronized capture (Deribit legs + OKX perp leg)
# ---------------------------------------------------------------------------
def acquire_underlying(
    client: DeribitClient,
    okx_session,
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
    max_okx_pages: int,
    okx_delay: float,
) -> Dict[str, Any]:
    window_start = datetime.fromtimestamp(start_ms / 1000.0, tz=timezone.utc)
    window_end = datetime.fromtimestamp(end_ms / 1000.0, tz=timezone.utc)
    ref_spot = acq51._spot(client, underlying)

    # One Deribit roster for BOTH Deribit legs (synchronization by construction).
    instruments = acq51.discover_instruments(
        client, underlying, window_start, window_end,
        max_per_expiry, max_expiry_days, ref_spot,
    )
    print(json.dumps({
        "event": "instruments_selected", "underlying": underlying,
        "n": len(instruments), "ref_spot": ref_spot,
        "expiries": sorted({i["expiry"].date().isoformat() for i in instruments}),
    }))

    # ---- Deribit options-venue order-flow leg: real signed option trades ----
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

    # ---- Deribit surface leg: real 5m option candles -> chain snapshots ----
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

    # ---- Deribit underlying leg: 1m perpetual candles ----
    perp_candles = acq52.fetch_perp_candles(client, underlying, start_ms, end_ms, PERP_RESOLUTION)

    snapshots: List[Dict[str, Any]] = []
    for bar_ms, quotes in built:
        snapshots.append({
            "bar_ms": int(bar_ms),
            "spot": acq52._spot_at(perp_candles, int(bar_ms), SURFACE_BAR_SECONDS),
            "quotes": quotes,
        })
    print(json.dumps({"event": "surface_leg_done", "underlying": underlying,
                      "n_snapshots": len(snapshots), "n_perp_candles": len(perp_candles)}))

    # ---- OKX perpetual order-flow leg: real history-trades (the new third leg) ----
    okx_inst = OKX_INST.get(underlying)
    if not okx_inst:
        raise RuntimeError(f"no OKX perp instrument mapping for {underlying}")
    okx_trades = fetch_okx_perp_trades(
        okx_session, okx_inst, start_ms, end_ms,
        max_pages=max_okx_pages, delay=okx_delay,
    )

    capture: Dict[str, Any] = {
        "schema": SCHEMA,
        "underlying": underlying,
        "venue": VENUE,
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
        "okx_inst_id": okx_inst,
        "okx_perp_trades": okx_trades,
        "source": {
            "authenticated": False,
            "public_read_only": True,
            "venue": VENUE,
            "deribit_endpoints": [
                "/public/get_instruments",
                "/public/get_index_price",
                "/public/get_last_trades_by_instrument_and_time",
                "/public/get_tradingview_chart_data",
            ],
            "okx_endpoint": OKX_HISTORY_URL,
            "surface_note": (
                "surface mark = measured Deribit 5m option chart close; bid/ask "
                "reconstructed around the mark (constant fallback spread); not venue quotes"
            ),
            "deribit_orderflow_note": "signed aggressor direction from real Deribit option trades",
            "okx_orderflow_note": (
                "signed taker side from real OKX perpetual history-trades (buy/sell)"
            ),
            "underlying_note": f"{underlying}-PERPETUAL {PERP_RESOLUTION}m candles (Deribit)",
            "provenance": (
                "real Deribit public options surface + options-venue order flow + "
                "real OKX perpetual history-trades; synchronized window; no synthetic data"
            ),
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"three_way_{underlying}_{stamp}.json"
    path.write_text(json.dumps(capture, separators=(",", ":")))

    surface_summary = acq52.summarize_surface(capture["surface"])
    of_summary = acq51.summarize(capture)
    okx_summary = summarize_okx_perp(capture["okx_perp_trades"])
    summary = {
        "underlying": underlying,
        "path": str(path),
        "surface": surface_summary,
        "orderflow": of_summary,
        "okx_orderflow": okx_summary,
    }
    print(json.dumps({"event": "capture_written", "underlying": underlying,
                      "path": str(path), "surface": surface_summary,
                      "orderflow": of_summary, "okx_orderflow": okx_summary}))
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
        "venue": VENUE,
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
            "real Deribit options surface (5m candles) + Deribit options-venue order "
            "flow (signed trades) + real OKX perpetual history-trades (signed taker "
            "flow) + Deribit perpetual 1m candles; synchronized window; no synthetic data"
        ),
    }
    out = ROOT / "research_state"
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / f"{MANIFEST_ID}_{stamp}.json"
    json_path.write_text(json.dumps(manifest, indent=2, default=str))

    lines = [
        f"# {MANIFEST_ID} — real synchronized three-way options surface x options order flow x OKX perp order flow",
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
        okx = s["okx_orderflow"]
        lines += [
            f"### {s['underlying']} (`{s['path']}`)",
            "",
            f"- surface snapshots: {sf['n_snapshots']} / instruments with data {sf['n_instruments_with_data']} / "
            f"quotes {sf['min_quotes_realized']}–{sf['max_quotes_realized']} / 5m bars {sf['n_bars_5m']} / "
            f"span {sf['span_seconds']} s",
            f"- Deribit options-venue trades: {of['n_option_trades']} / instruments with trades "
            f"{of['n_instruments_with_trades']} / buy {of['n_buy']} sell {of['n_sell']} / span {of['span_seconds']} s",
            f"- OKX perp order-flow trades: {okx['n_okx_perp_trades']} / buy {okx['n_buy']} sell "
            f"{okx['n_sell']} / span {okx['span_seconds']} s / 5m bars {okx['n_bars_5m']}",
            f"- surface non-degenerate: **{sf['non_degenerate']}**; Deribit order-flow non-degenerate: "
            f"**{of['non_degenerate']}**; OKX order-flow non-degenerate: **{okx['non_degenerate']}**",
            "",
        ]
    md_path = json_path.with_suffix(".md")
    md_path.write_text("\n".join(lines) + "\n")
    return {"json": str(json_path), "md": str(md_path)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="POST-EVAL three-way real Deribit options surface x options order flow x OKX perp order flow acquisition"
    )
    ap.add_argument("--underlying", action="append", default=None,
                    help="underlying (repeatable), e.g. BTC ETH")
    ap.add_argument("--days", type=float, default=DEFAULT_DAYS,
                    help="trailing window length in days (default 1; Deribit serves ~24h of trade history)")
    ap.add_argument("--end", default=None, help="window end ISO-8601 UTC (default now)")
    ap.add_argument("--out-dir", default="data/raw/eval60")
    ap.add_argument("--max-per-expiry", type=int, default=DEFAULT_MAX_PER_EXPIRY)
    ap.add_argument("--max-expiry-days", type=int, default=DEFAULT_MAX_EXPIRY_DAYS)
    ap.add_argument("--max-trades-per-instrument", type=int, default=DEFAULT_MAX_TRADES_PER_INSTRUMENT)
    ap.add_argument("--min-quotes", type=int, default=DEFAULT_MIN_QUOTES)
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    ap.add_argument("--max-okx-pages", type=int, default=DEFAULT_MAX_OKX_PAGES,
                    help="safety cap on OKX history-trades pages per underlying")
    ap.add_argument("--okx-delay", type=float, default=DEFAULT_OKX_DELAY,
                    help="polite delay (s) between OKX history-trades pages")
    ap.add_argument("--seal", action="store_true",
                    help="write an acquisition manifest into research_state/")
    ap.add_argument("--task-label",
                    default="POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION")
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
    okx_session = _okx_session()
    generated_at = acq51._utc_now_iso()
    stamp = acq51._stamp_for_filename(generated_at)

    results: List[Dict[str, Any]] = []
    for underlying in underlyings:
        results.append(acquire_underlying(
            client, okx_session, underlying, start_ms, end_ms, out_dir, stamp,
            max_per_expiry=args.max_per_expiry,
            max_expiry_days=args.max_expiry_days,
            max_trades=args.max_trades_per_instrument,
            min_quotes=args.min_quotes,
            delay=args.delay,
            max_okx_pages=args.max_okx_pages,
            okx_delay=args.okx_delay,
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
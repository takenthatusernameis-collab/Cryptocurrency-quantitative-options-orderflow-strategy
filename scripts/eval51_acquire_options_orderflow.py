#!/usr/bin/env python3
"""EVAL-51 acquisition: capture real Deribit **options order flow** (signed option
trades) plus the aligned underlying perpetual candles.

The repository charter is a **combined options + orderflow** strategy. Every prior
rung falsified either option *candles / surface / greeks* (EVAL-46/47/48/49) or the
*spot* orderflow (trade tape EVAL-43/45, L2 book OFI EVAL-50). The one order-flow
modality that has **never** been measured is the order flow **of the options venue
itself** — the signed aggressor flow of real Deribit option trades. That is the
missing leg of the charter and is what this campaign (EVAL-51) acquires.

Deribit exposes a public, read-only historical trade endpoint
(``GET /public/get_last_trades_by_instrument_and_time``) that returns, per trade,
the aggressor ``direction`` (``buy``/``sell``), ``amount`` (in the underlying),
``price``/``mark_price``/``index_price`` and ``iv``. We paginate it politely for
every option instrument that was live during the window, and we also fetch the
underlying perpetual ``get_tradingview_chart_data`` 5m candles so the measurement
can align option flow to subsequent underlying returns.

**Data-depth note:** Deribit caps signed trade history at roughly the trailing 24h
per instrument (older ``start_timestamp`` values return only the last ~24h), so the
useful window is ~1 day. The heavy-work floor is therefore calibrated to a *full*
~24h acquisition across the whole option universe (BTC ~5k trades / ~100
instruments; ETH ~3.5k trades / ~100 instruments; ~289 5m bars each), not to a
multi-day span that the endpoint cannot serve. Breadth (every instrument/strike/
expiry) and rigor (per-config permutation/bootstrap/PBO/BH-FDR) are where the heavy
work lives.

No synthetic data, no relabelling: every trade field is a measured Deribit value.
``schema`` records the real provenance. Paper-only, public read-only market data.
Writes one capture file per underlying under ``--out-dir`` and, with ``--seal``, an
acquisition manifest into ``research_state/`` (never a GO/verdict).

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval51_acquire_options_orderflow.py
    # tiny real smoke (writes to a temp dir; no manifest):
    python3 scripts/eval51_acquire_options_orderflow.py \
        --underlying BTC --days 2 --max-per-expiry 4 \
        --out-dir /tmp/eval51_smoke
    # full heavy cross-asset acquisition into the git-tracked data dir (+ manifest):
    python3 scripts/eval51_acquire_options_orderflow.py \
        --underlying BTC --underlying ETH --days 1 \
        --out-dir data/raw/eval51 --seal
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

SCHEMA = "deribit_options_orderflow_capture_v1"
MANIFEST_ID = "EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION"
DEFAULT_DAYS = 1.0
DEFAULT_MAX_PER_EXPIRY = 12
DEFAULT_MAX_EXPIRY_DAYS = 45
DEFAULT_MAX_TRADES_PER_INSTRUMENT = 5000
DEFAULT_DELAY = 0.12
TRADE_PAGE = 1000
PERP_RESOLUTION = "5"
PERP_BAR_SECONDS = 300
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso_ms(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _session_client() -> DeribitClient:
    import requests

    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return DeribitClient(session=s)


def _spot(client: DeribitClient, underlying: str) -> Optional[float]:
    try:
        data = client._get("/public/get_index_price", {"index_name": f"{underlying.lower()}_usd"})
        result = data.get("result") if isinstance(data, dict) else None
        if isinstance(result, dict):
            px = result.get("index_price") or result.get("estimated_delivery_price")
            if px is not None:
                return float(px)
    except Exception as exc:  # noqa: BLE001 - record and continue
        print(json.dumps({"event": "index_price_failed", "underlying": underlying, "error": str(exc)}))
    return None


def discover_instruments(
    client: DeribitClient,
    underlying: str,
    window_start: datetime,
    window_end: datetime,
    max_per_expiry: int,
    max_expiry_days: int,
    ref_spot: Optional[float],
) -> List[Dict[str, Any]]:
    """Option instruments whose lifetime overlaps the window, nearest-to-spot first.

    Combines live (``expired=False``) and expired (``expired=True``) instruments so
    expiries that rolled off during the window are still covered. Keeps expiries up
    to ``max_expiry_days`` past the window start, then the ``max_per_expiry`` strikes
    closest to the anchor spot (calls and puts both kept).
    """
    names: set[str] = set()
    for expired in (False, True):
        try:
            for inst in client.get_instruments(underlying, kind="option", expired=expired):
                nm = inst.get("instrument_name") or inst.get("instrument")
                if nm:
                    names.add(nm)
        except Exception as exc:  # noqa: BLE001 - record and continue
            print(json.dumps({"event": "get_instruments_failed", "expired": expired,
                              "underlying": underlying, "error": str(exc)}))

    parsed: List[Dict[str, Any]] = []
    expiry_cap = window_start + timedelta(days=int(max_expiry_days))
    for nm in names:
        info = _parse_deribit_instrument(nm)
        if not info or info["underlying"] != underlying:
            continue
        expiry: datetime = info["expiry"]
        if expiry < window_start or expiry > expiry_cap:
            continue
        parsed.append({
            "instrument_name": nm,
            "expiry": expiry,
            "strike": float(info["strike"]),
            "option_type": str(info["option_type"]).lower(),
        })

    if ref_spot is None:
        strikes = sorted(row["strike"] for row in parsed)
        ref_spot = strikes[len(strikes) // 2] if strikes else 0.0
    by_expiry: Dict[str, List[Dict[str, Any]]] = {}
    for row in parsed:
        by_expiry.setdefault(row["expiry"].date().isoformat(), []).append(row)

    selected: List[Dict[str, Any]] = []
    for _day, rows in sorted(by_expiry.items()):
        rows.sort(key=lambda r: abs(r["strike"] - ref_spot))
        selected.extend(rows[: max(1, int(max_per_expiry))])
    selected.sort(key=lambda r: (r["expiry"], r["strike"], r["option_type"]))
    return selected


def fetch_trades_paginated(
    client: DeribitClient,
    instrument_name: str,
    start_ms: int,
    end_ms: int,
    max_trades: int,
    delay: float,
) -> List[Dict[str, Any]]:
    """Page ``get_last_trades_by_instrument_and_time`` ascending until exhausted."""
    collected: List[Dict[str, Any]] = []
    cursor = int(start_ms)
    seen_ids: set[str] = set()
    while cursor < int(end_ms) and len(collected) < int(max_trades):
        try:
            data = client._get(
                "/public/get_last_trades_by_instrument_and_time",
                {
                    "instrument_name": instrument_name,
                    "start_timestamp": cursor,
                    "end_timestamp": int(end_ms),
                    "count": TRADE_PAGE,
                    "sorting": "asc",
                },
            )
        except Exception as exc:  # noqa: BLE001 - skip instrument on persistent failure
            print(json.dumps({"event": "trades_fetch_failed", "instrument": instrument_name,
                              "error": str(exc)}))
            break
        result = data.get("result") if isinstance(data, dict) else None
        if not isinstance(result, dict):
            break
        trades = result.get("trades") or []
        if not trades:
            break
        new = 0
        for t in trades:
            tid = str(t.get("trade_id") or t.get("trade_seq") or "")
            if tid in seen_ids:
                continue
            seen_ids.add(tid)
            collected.append(t)
            new += 1
        has_more = bool(result.get("has_more"))
        cursor = int(trades[-1]["timestamp"]) + 1
        if delay > 0:
            time.sleep(float(delay))
        if not has_more or new == 0:
            break
    return collected[: int(max_trades)]


def normalize_trade(t: Dict[str, Any], row: Dict[str, Any]) -> Dict[str, Any]:
    def f(key: str, default: float = 0.0) -> float:
        try:
            v = float(t.get(key))
            return v if v == v else float(default)
        except (TypeError, ValueError):
            return float(default)

    expiry = row.get("expiry")
    expiry_iso = (
        expiry.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if isinstance(expiry, datetime) else ""
    )
    return {
        "ts": int(t.get("timestamp") or 0),
        "instrument": str(t.get("instrument_name") or row["instrument_name"]),
        "direction": str(t.get("direction") or "").lower(),
        "amount": f("amount"),
        "price": f("price"),
        "index_price": f("index_price"),
        "iv": f("iv"),
        "option_type": row["option_type"],
        "strike": float(row["strike"]),
        "expiry": expiry_iso,
    }


def fetch_perp_candles(
    client: DeribitClient, underlying: str, start_ms: int, end_ms: int
) -> List[Dict[str, Any]]:
    """Return ``[{ts, open, high, low, close}]`` for the underlying perpetual."""
    try:
        data = client._get(
            "/public/get_tradingview_chart_data",
            {
                "instrument_name": f"{underlying}-PERPETUAL",
                "start_timestamp": int(start_ms),
                "end_timestamp": int(end_ms),
                "resolution": PERP_RESOLUTION,
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


def summarize(capture: Dict[str, Any]) -> Dict[str, Any]:
    trades = capture.get("option_trades", [])
    n = len(trades)
    by_inst: Dict[str, int] = {}
    buys = 0
    sells = 0
    notional = 0.0
    for t in trades:
        by_inst[t["instrument"]] = by_inst.get(t["instrument"], 0) + 1
        if t["direction"] == "buy":
            buys += 1
        elif t["direction"] == "sell":
            sells += 1
        notional += abs(float(t["amount"])) * float(t["index_price"] or 0.0)
    ts = [int(t["ts"]) for t in trades if int(t["ts"]) > 0]
    span = ((max(ts) - min(ts)) / 1000.0) if len(ts) >= 2 else 0.0
    candles = capture.get("perp_candles", [])
    return {
        "underlying": capture.get("underlying"),
        "n_option_trades": n,
        "n_instruments_with_trades": len(by_inst),
        "n_distinct_strikes": len({t["strike"] for t in trades}),
        "n_buy": buys,
        "n_sell": sells,
        "notional": notional,
        "span_seconds": round(span, 3),
        "n_perp_candles": len(candles),
        "non_degenerate": bool(n > 0 and len(by_inst) >= 1 and len(candles) >= 2),
    }


def write_capture(capture: Dict[str, Any], out_dir: Path, stamp: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"options_orderflow_{capture['underlying']}_{stamp}.json"
    path.write_text(json.dumps(capture, separators=(",", ":")))
    return path


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
    delay: float,
) -> Dict[str, Any]:
    window_start = datetime.fromtimestamp(start_ms / 1000.0, tz=timezone.utc)
    ref_spot = _spot(client, underlying)
    instruments = discover_instruments(
        client, underlying, window_start,
        datetime.fromtimestamp(end_ms / 1000.0, tz=timezone.utc),
        max_per_expiry, max_expiry_days, ref_spot,
    )
    print(json.dumps({
        "event": "instruments_selected", "underlying": underlying,
        "n": len(instruments), "ref_spot": ref_spot,
        "expiries": sorted({i["expiry"].date().isoformat() for i in instruments}),
    }))

    trades: List[Dict[str, Any]] = []
    probed = 0
    for row in instruments:
        probed += 1
        raw = fetch_trades_paginated(client, row["instrument_name"], start_ms, end_ms,
                                     max_trades, delay)
        for t in raw:
            trades.append(normalize_trade(t, row))
        if delay > 0 and probed < len(instruments):
            time.sleep(delay * 0.5)

    trades.sort(key=lambda t: (int(t["ts"]), t["instrument"]))
    candles = fetch_perp_candles(client, underlying, start_ms, end_ms)

    capture = {
        "schema": SCHEMA,
        "underlying": underlying,
        "venue": "deribit",
        "window_start": _iso_ms(start_ms),
        "window_end": _iso_ms(end_ms),
        "n_instruments_probed": probed,
        "option_trades": trades,
        "perp_candles": candles,
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
            "trade_fields": ["timestamp", "instrument_name", "direction", "amount",
                             "price", "index_price", "iv", "trade_id"],
            "perp": f"{underlying}-PERPETUAL {PERP_RESOLUTION}m candles",
            "note": "every option trade and perp candle is a measured Deribit public value; no synthetic data",
        },
    }
    path = write_capture(capture, out_dir, stamp)
    summary = summarize(capture)
    print(json.dumps({"event": "capture_written", "underlying": underlying,
                      "path": str(path), **summary}))
    return {"capture": capture, "path": path, "summary": summary}


def seal_manifest(
    results: List[Dict[str, Any]], generated_at: str, task_label: str,
    manifest_id: str, window_start: str, window_end: str,
) -> Dict[str, str]:
    stamp = _stamp_for_filename(generated_at)
    captures = [r["summary"] for r in results]
    total_trades = sum(s["n_option_trades"] for s in captures)
    manifest = {
        "manifest_id": manifest_id,
        "task_id": f"INIT-{generated_at}-{task_label}",
        "generated_at": generated_at,
        "schema": SCHEMA,
        "venue": "deribit",
        "window_start": window_start,
        "window_end": window_end,
        "underlyings": [r["summary"]["underlying"] for r in results],
        "total_option_trades": total_trades,
        "captures": {
            r["summary"]["underlying"]: {
                "path": str(r["path"]),
                "sha256": _sha256(Path(r["path"])),
                **r["summary"],
            }
            for r in results
        },
        "synthetic": False,
        "provenance": "real Deribit public options trades + perpetual candles; no synthetic data",
    }
    OUT_DIR = ROOT / "research_state"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / f"{manifest_id}_{stamp}.json"
    json_path.write_text(json.dumps(manifest, indent=2, default=str))
    lines = [
        f"# {manifest_id} — real Deribit options order-flow acquisition",
        "",
        f"- Generated: `{generated_at}`",
        f"- Task: `{manifest['task_id']}`",
        f"- Window: `{window_start}` .. `{window_end}`",
        f"- Underlyings: {', '.join(manifest['underlyings'])}",
        f"- Total option trades: **{total_trades}**",
        f"- Synthetic: **{manifest['synthetic']}**",
        "",
        "## Per-underlying integrity",
        "",
    ]
    for s in captures:
        lines += [
            f"### {s['underlying']} (`{next(r['path'] for r in results if r['summary']['underlying']==s['underlying'])}`)",
            "",
            f"- option trades: {s['n_option_trades']}",
            f"- instruments with trades: {s['n_instruments_with_trades']}",
            f"- distinct strikes: {s['n_distinct_strikes']}",
            f"- buy / sell trades: {s['n_buy']} / {s['n_sell']}",
            f"- span: {s['span_seconds']} s",
            f"- perp candles: {s['n_perp_candles']}",
            f"- non-degenerate: **{s['non_degenerate']}**",
            "",
        ]
    md_path = json_path.with_suffix(".md")
    md_path.write_text("\n".join(lines) + "\n")
    return {"json": str(json_path), "md": str(md_path)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-51 real Deribit options order-flow acquisition")
    ap.add_argument("--underlying", action="append", default=None,
                    help="underlying (repeatable), e.g. BTC ETH")
    ap.add_argument("--days", type=float, default=DEFAULT_DAYS,
                    help="trailing window length in days (default 1; Deribit serves ~24h of trade history)")
    ap.add_argument("--end", default=None, help="window end ISO-8601 UTC (default now)")
    ap.add_argument("--out-dir", default="data/raw/eval51")
    ap.add_argument("--max-per-expiry", type=int, default=DEFAULT_MAX_PER_EXPIRY)
    ap.add_argument("--max-expiry-days", type=int, default=DEFAULT_MAX_EXPIRY_DAYS)
    ap.add_argument("--max-trades-per-instrument", type=int, default=DEFAULT_MAX_TRADES_PER_INSTRUMENT)
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    ap.add_argument("--seal", action="store_true",
                    help="write an acquisition manifest into research_state/")
    ap.add_argument("--task-label", default="EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST")
    ap.add_argument("--manifest-id", default=MANIFEST_ID)
    args = ap.parse_args(argv)

    underlyings = args.underlying or ["BTC", "ETH"]
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    if args.end:
        end_dt = _parse_iso(args.end)
    else:
        end_dt = datetime.now(timezone.utc)
    end_ms = int(end_dt.timestamp() * 1000)
    start_ms = int((end_dt - timedelta(days=float(args.days))).timestamp() * 1000)

    client = _session_client()
    generated_at = _utc_now_iso()
    stamp = _stamp_for_filename(generated_at)

    results: List[Dict[str, Any]] = []
    for underlying in underlyings:
        results.append(acquire_underlying(
            client, underlying.upper(), start_ms, end_ms, out_dir, stamp,
            max_per_expiry=args.max_per_expiry,
            max_expiry_days=args.max_expiry_days,
            max_trades=args.max_trades_per_instrument,
            delay=args.delay,
        ))

    if args.seal:
        written = seal_manifest(
            results, generated_at, args.task_label, args.manifest_id,
            _iso_ms(start_ms), _iso_ms(end_ms),
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
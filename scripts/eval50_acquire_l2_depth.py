#!/usr/bin/env python3
"""EVAL-50 acquisition: capture real OKX L2 order-book depth snapshots.

The repository charter is a **combined options + orderflow** strategy. Every
combined options+orderflow venue/asset cell is now sealed ``NO-GO CONFIRMED
(PASS)`` (EVAL-46 BTC/OKX, EVAL-47 ETH/OKX, EVAL-48 BTC Deribit-cross-venue,
EVAL-49 ETH Deribit-cross-venue). The next orderflow modality is **real L2
order-book depth** (book-imbalance / OFI alpha), which does not yet exist on
disk.

OKX exposes a public, read-only L2 book snapshot endpoint
(``GET /api/v5/market/books?instId=...&sz=400``) but **no historical book
endpoint** (``books-history`` returns 404). Therefore real L2 depth must be
captured **live** by polling the snapshot endpoint at a fixed cadence. This
script does exactly that, politely (fixed cadence + small jitter + retry), and
persists the measured snapshots in the schema the EVAL-50 measurement tool
consumes. No synthetic data, no relabelling: every bid/ask price and size is a
measured OKX book field; ``schema`` records the real provenance.

Paper-only, public read-only market data. Never writes to ``research_state/``
except a capture manifest (never a GO/verdict).

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval50_acquire_l2_depth.py
    # short smoke (writes to a temp dir; no manifest):
    python3 scripts/eval50_acquire_l2_depth.py \
        --inst BTC-USD-SWAP --duration 40 --cadence 2 --out-dir /tmp/eval50_smoke
    # full cross-asset capture into the git-tracked data dir (+ manifest):
    python3 scripts/eval50_acquire_l2_depth.py \
        --inst BTC-USD-SWAP --inst ETH-USD-SWAP \
        --duration 900 --cadence 2 --levels 25 \
        --out-dir data/raw/eval50 --seal
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BOOKS_URL = "https://www.okx.com/api/v5/market/books"
SCHEMA = "okx_l2_books_snapshot_capture_v1"
VENUE = "okx"
MANIFEST_ID = "EVAL_50_L2_DEPTH_ACQUISITION"
OUT_DIR = ROOT / "research_state"
DEFAULT_LEVELS = 25
DEFAULT_CADENCE = 2.0
DEFAULT_DURATION = 900.0
FETCH_SZ = 400  # request the deepest public book, then trim to top-N per side
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp_for_filename(iso_ts: str) -> str:
    return iso_ts.replace("-", "").replace(":", "").replace(".", "").replace("Z", "Z")


def _session():
    """A requests session with a browser User-Agent (OKX rejects bare urllib 403)."""
    import requests  # local import so --help works without deps

    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return s


def _fetch_book(session, inst_id: str, retries: int = 4) -> Dict[str, Any]:
    """Fetch one L2 book snapshot; retry transient failures with backoff."""
    params = {"instId": inst_id, "sz": str(FETCH_SZ)}
    last_err: Optional[BaseException] = None
    for attempt in range(retries):
        try:
            resp = session.get(BOOKS_URL, params=params, timeout=10)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:160]}")
            payload = resp.json()
            if str(payload.get("code")) != "0":
                raise RuntimeError(f"OKX code {payload.get('code')}: {payload.get('msg')}")
            data = payload.get("data") or []
            if not data:
                raise RuntimeError("empty data array")
            return data[0]
        except BaseException as exc:  # noqa: BLE001 - retry any transient error
            last_err = exc
            time.sleep(min(2.0, 0.4 * (2 ** attempt)) + random.uniform(0, 0.2))
    raise RuntimeError(f"failed to fetch book for {inst_id}: {last_err!r}")


def _trim_levels(levels: Sequence[Sequence[Any]], n: int) -> List[List[float]]:
    """Project OKX ``[price, size, n_liq, n_orders]`` rows to top-N ``[price, size]``."""
    out: List[List[float]] = []
    for row in levels[: max(1, int(n))]:
        try:
            out.append([float(row[0]), float(row[1])])
        except (TypeError, ValueError, IndexError):
            continue
    return out


def capture_instrument(
    session,
    inst_id: str,
    duration_s: float,
    cadence_s: float,
    levels: int,
) -> Dict[str, Any]:
    """Poll the L2 book for ``duration_s`` at ``cadence_s``; return a capture record."""
    snapshots: List[Dict[str, Any]] = []
    t_end = time.monotonic() + float(duration_s)
    while True:
        now = time.monotonic()
        if now >= t_end:
            break
        book = _fetch_book(session, inst_id)
        bids = _trim_levels(book.get("bids") or [], levels)
        asks = _trim_levels(book.get("asks") or [], levels)
        if bids and asks:
            snapshots.append(
                {
                    "ts": int(book.get("ts")),
                    "seqId": int(book.get("seqId")),
                    "bids": bids,
                    "asks": asks,
                }
            )
        remaining = t_end - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(float(cadence_s), remaining) + random.uniform(0.0, 0.1))
    return {
        "inst_id": inst_id,
        "count": len(snapshots),
        "snapshots": snapshots,
    }


def _mid(book: Dict[str, Any]) -> float:
    bid = float(book["bids"][0][0])
    ask = float(book["asks"][0][0])
    return 0.5 * (bid + ask)


def _spread_bps(book: Dict[str, Any]) -> float:
    bid = float(book["bids"][0][0])
    ask = float(book["asks"][0][0])
    mid = 0.5 * (bid + ask)
    return (ask - bid) / mid * 1e4 if mid > 0 else 0.0


def summarize_capture(capture: Dict[str, Any]) -> Dict[str, Any]:
    """Integrity / non-degeneracy summary of a captured instrument."""
    snaps = capture["snapshots"]
    n = len(snaps)
    if n == 0:
        return {"count": 0, "degenerate": True, "reason": "no snapshots"}
    mids = [_mid(s) for s in snaps]
    spreads = [_spread_bps(s) for s in snaps]
    ts = [s["ts"] for s in snaps]
    seq = [s["seqId"] for s in snaps]
    seq_non_decreasing = all(b >= a for a, b in zip(seq, seq[1:]))
    mid_min, mid_max = min(mids), max(mids)
    mid_mean = sum(mids) / n
    mid_var = sum((m - mid_mean) ** 2 for m in mids) / n
    mid_std = mid_var ** 0.5
    spread_sorted = sorted(spreads)
    median_spread = spread_sorted[n // 2]
    return {
        "count": int(n),
        "start_ts_ms": int(ts[0]),
        "end_ts_ms": int(ts[-1]),
        "span_seconds": round((ts[-1] - ts[0]) / 1000.0, 3),
        "seq_first": int(seq[0]),
        "seq_last": int(seq[-1]),
        "seq_nondecreasing_fraction": round(
            sum(1 for a, b in zip(seq, seq[1:]) if b >= a) / max(1, n - 1), 4
        ),
        "mid_min": mid_min,
        "mid_max": mid_max,
        "mid_std": mid_std,
        "mid_relative_std": (mid_std / mid_mean) if mid_mean else 0.0,
        "spread_bps_median": median_spread,
        "spread_bps_min": min(spreads),
        "spread_bps_max": max(spreads),
        "bids_levels": len(snaps[0]["bids"]),
        "asks_levels": len(snaps[0]["asks"]),
        "degenerate": bool(n < 2 or mid_std <= 0.0 or median_spread <= 0.0),
        "non_degenerate_ofi_ready": bool(n >= 2 and mid_std > 0.0 and median_spread > 0.0),
    }


def write_capture(capture: Dict[str, Any], out_dir: Path, stamp: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    inst = capture["inst_id"]
    path = out_dir / f"l2_depth_{inst}_{stamp}.json"
    path.write_text(json.dumps(capture, separators=(",", ":")))
    return path


def build_manifest(
    captures: Sequence[Dict[str, Any]],
    paths: Sequence[Path],
    generated_at: str,
    cadence_s: float,
    levels: int,
) -> Dict[str, Any]:
    summaries = {c["inst_id"]: summarize_capture(c) for c in captures}
    total_snaps = sum(s["count"] for s in summaries.values())
    all_ok = all(s["non_degenerate_ofi_ready"] for s in summaries.values()) and total_snaps > 0
    return {
        "manifest_id": MANIFEST_ID,
        "eval": "EVAL-50",
        "generated_at": generated_at,
        "schema": SCHEMA,
        "venue": VENUE,
        "endpoint": BOOKS_URL,
        "cadence_seconds": float(cadence_s),
        "levels_per_side": int(levels),
        "instruments": [c["inst_id"] for c in captures],
        "total_snapshots": int(total_snaps),
        "captures": {
            c["inst_id"]: {
                "path": str(p),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "summary": summaries[c["inst_id"]],
            }
            for c, p in zip(captures, paths)
        },
        "all_non_degenerate": bool(all_ok),
        "synthetic": False,
        "note": (
            "Real OKX L2 book snapshots captured live by polling the public "
            "books endpoint; no historical REST endpoint exists. Levels are a "
            "faithful projection of the measured [price,size] fields."
        ),
    }


def write_manifest(manifest: Dict[str, Any], stamp: str) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: Dict[str, str] = {}
    j = OUT_DIR / f"{MANIFEST_ID}_{stamp}.json"
    j.write_text(json.dumps(manifest, indent=2, default=str))
    written["json"] = str(j)
    md = OUT_DIR / f"{MANIFEST_ID}_{stamp}.md"
    md.write_text(_manifest_md(manifest), encoding="utf-8")
    written["md"] = str(md)
    return written


def _manifest_md(m: Dict[str, Any]) -> str:
    lines = [
        f"# {m['manifest_id']} — EVAL-50 real L2 depth acquisition",
        "",
        f"- Generated: `{m['generated_at']}`",
        f"- Venue/endpoint: `{m['venue']}` `{m['endpoint']}`",
        f"- Cadence: {m['cadence_seconds']} s; levels/side: {m['levels_per_side']}",
        f"- Instruments: {', '.join(m['instruments'])}",
        f"- Total snapshots: **{m['total_snapshots']}**",
        f"- All non-degenerate (OFI-ready): **{m['all_non_degenerate']}**",
        f"- Synthetic: **{m['synthetic']}**",
        "",
        "## Per-instrument integrity",
        "",
    ]
    for inst, info in m["captures"].items():
        s = info["summary"]
        lines.append(f"### {inst} (`{info['path']}`)")
        lines.append("")
        lines.append(f"- snapshots: {s['count']}")
        lines.append(f"- span: {s['span_seconds']} s ({s['start_ts_ms']} → {s['end_ts_ms']})")
        lines.append(f"- seq non-decreasing fraction: {s['seq_nondecreasing_fraction']}")
        lines.append(f"- mid relative std: {s['mid_relative_std']:.6f}")
        lines.append(f"- median spread: {s['spread_bps_median']:.4f} bps")
        lines.append(f"- levels/side: bids={s['bids_levels']} asks={s['asks_levels']}")
        lines.append(f"- OFI-ready: **{s['non_degenerate_ofi_ready']}**")
        lines.append("")
    return "\n".join(lines) + "\n"


def _capture_worker(inst: str, duration_s: float, cadence_s: float, levels: int) -> Dict[str, Any]:
    """Thread worker: each instrument gets its own session (requests is not thread-safe)."""
    cap = capture_instrument(_session(), inst, duration_s, cadence_s, levels)
    cap["schema"] = SCHEMA
    cap["venue"] = VENUE
    cap["levels_per_side"] = int(levels)
    cap["cadence_seconds"] = float(cadence_s)
    cap["start_ts_ms"] = cap["snapshots"][0]["ts"] if cap["snapshots"] else 0
    cap["end_ts_ms"] = cap["snapshots"][-1]["ts"] if cap["snapshots"] else 0
    return cap


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-50 real OKX L2 depth capture")
    ap.add_argument("--inst", action="append", default=None,
                    help="instrument id (repeatable), e.g. BTC-USD-SWAP")
    ap.add_argument("--duration", type=float, default=DEFAULT_DURATION,
                    help="capture duration seconds per instrument (concurrent)")
    ap.add_argument("--cadence", type=float, default=DEFAULT_CADENCE,
                    help="poll cadence seconds")
    ap.add_argument("--levels", type=int, default=DEFAULT_LEVELS,
                    help="levels per side to retain")
    ap.add_argument("--out-dir", default="data/raw/eval50",
                    help="capture output directory")
    ap.add_argument("--seal", action="store_true",
                    help="write an acquisition manifest into research_state/")
    args = ap.parse_args(argv)

    instruments = args.inst or ["BTC-USD-SWAP"]
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir

    captures: List[Dict[str, Any]] = []
    paths: List[Path] = []
    if len(instruments) == 1:
        print(f"[eval50] capturing {instruments[0]} for {args.duration}s @ "
              f"{args.cadence}s ...", flush=True)
        captures = [_capture_worker(instruments[0], args.duration, args.cadence, args.levels)]
    else:
        from concurrent.futures import ThreadPoolExecutor

        print(f"[eval50] capturing {', '.join(instruments)} concurrently for "
              f"{args.duration}s @ {args.cadence}s ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(instruments)) as pool:
            captures = list(pool.map(
                lambda i: _capture_worker(i, args.duration, args.cadence, args.levels),
                instruments,
            ))
    for cap in captures:
        stamp = _stamp_for_filename(_utc_now_iso())
        p = write_capture(cap, out_dir, stamp)
        paths.append(p)
        s = summarize_capture(cap)
        print(f"[eval50] {cap['inst_id']}: {s['count']} snapshots, "
              f"mid_rel_std={s['mid_relative_std']:.6f}, "
              f"median_spread={s['spread_bps_median']:.3f}bps, "
              f"ofi_ready={s['non_degenerate_ofi_ready']} -> {p}", flush=True)

    if args.seal:
        manifest = build_manifest(captures, paths, _utc_now_iso(),
                                  args.cadence, args.levels)
        written = write_manifest(manifest, _stamp_for_filename(_utc_now_iso()))
        print(f"[eval50] manifest sealed: {written}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
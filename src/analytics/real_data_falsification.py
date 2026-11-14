"""Real-data falsification-readiness gate (EVAL-25, paper-only).

EVAL-22/EVAL-23B/EVAL-24A are code-complete: trade, orderflow and option
export adapters parse venue exports into the sealed schemas. The only remaining
blocker to a trustworthy net-of-cost verdict is *data availability*:
``data/raw/`` contains no real tape and no real option chain, so EVAL-23 and
EVAL-24 cannot produce a measured GO.

EVAL-25 is the falsification-readiness gate. It:

  * discovers candidate real exports under ``data/raw/`` (orderflow tapes and
    option chains), excluding any ``*_synthetic*`` file;
  * loads each candidate through the sealed ``DataLoader`` (cache disabled,
    offline, no network calls) and re-validates provenance;
  * re-checks EVAL-22 trade adequacy (``n_returns >= 1000``,
    ``n_windows >= 20`` at ``bar_duration_seconds=15.0``) and EVAL-24 option
    adequacy (``min_contracts=8``, ``min_quotes=8``, ``min_expiries=2``);
  * emits a per-candidate measured verdict and an overall GO/NO-GO that is GO
    only when at least one real trade tape and one real option chain clear
    their adequacy floors;
  * never relabels synthetic as real, never substitutes synthetic provenance,
    records ``authenticity_verified=false`` and honest ``data_provenance`` per
    candidate, and never emits ``{"valid": true}``.

If no real export exists, this session ships the gate + fixtures/tests/CLI and
seals an artifact documenting readiness and that ``data/raw`` yields 0 real
candidates. That is a measured NO-GO, not a failure of the gate.

No network calls, no exchange access, no ``.env``, no live trading.

CLI::

    python -m src.analytics.real_data_falsification --repo . \
        --out research_state/ [--data-dir data/raw] [--no-write] [--timestamp ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.analytics.measurement_validity_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_MIN_RETURNS,
    DEFAULT_MIN_WINDOWS,
    DEFAULT_STEP_SIZE,
    DEFAULT_TEST_WINDOW,
    DEFAULT_TRAIN_WINDOW,
    _stamp_for_filename,
    _utc_now_iso as _now_iso,
)
from src.analytics.sample_adequacy_acquisition import _tape_adequacy
from src.data.loader import DataLoader
from src.data.options_exports import (
    DEFAULT_MIN_CONTRACTS,
    DEFAULT_MIN_EXPIRIES,
    DEFAULT_MIN_QUOTES,
    _adequacy_counts,
)
from src.data.schemas import OptionsChain, OrderflowSnapshot
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "REAL_DATA_FALSIFICATION_25"
OUT_DIR = Path("research_state")
DEFAULT_DATA_DIR = Path("data/raw")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# Substrings that mark a file as synthetic rather than a venue export.
_SYNTHETIC_MARKERS: Tuple[str, ...] = ("synthetic",)


class RealDataRejected(ValueError):
    """A candidate real-data export failed provenance or schema validation."""


def _utc_now_iso() -> str:
    return _now_iso()


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _parse_ts(value: Any) -> datetime:
    """Strictly parse a raw timestamp; raise instead of substituting ``now``."""
    try:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(float(value), tz=timezone.utc)
        elif isinstance(value, str) and value.strip():
            dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        else:
            raise RealDataRejected(f"unparseable timestamp: {value!r}")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if not math.isfinite(dt.timestamp()):
            raise RealDataRejected(f"non-finite timestamp: {value!r}")
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError, OSError) as exc:
        raise RealDataRejected(f"unparseable timestamp: {value!r}") from exc


def _content_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _discover_candidates(data_raw_dir: Path) -> List[Path]:
    """Return candidate real-data exports, sorted, excluding ``*_synthetic*``.

    Candidates are orderflow tapes (``orderflow_<venue>_<symbol>.json``) and
    option chains (``options_<venue>_<underlying>_<utc>.json``).
    """
    root = Path(data_raw_dir)
    if not root.exists():
        return []
    out: List[Path] = []
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if not (lowered.startswith("orderflow_") or lowered.startswith("options_")):
            continue
        if not lowered.endswith(".json"):
            continue
        if any(marker in lowered for marker in _SYNTHETIC_MARKERS):
            continue
        out.append(path)
    return out


def _parse_orderflow_name(path: Path) -> Tuple[str, str]:
    stem = path.stem
    parts = stem.split("_")
    if len(parts) < 3 or parts[0] != "orderflow":
        raise RealDataRejected(
            f"filename does not match orderflow_<venue>_<symbol>.json: {path.name}"
        )
    venue = parts[1].strip()
    symbol = "_".join(parts[2:]).strip()
    if not venue or not symbol:
        raise RealDataRejected(f"empty venue/symbol in filename: {path.name}")
    return venue, symbol


def _parse_options_name(path: Path) -> Tuple[str, str]:
    stem = path.stem
    parts = stem.split("_")
    if len(parts) < 4 or parts[0] != "options":
        raise RealDataRejected(
            f"filename does not match options_<venue>_<underlying>_<utc>.json: {path.name}"
        )
    venue = parts[1].strip()
    underlying = parts[2].strip()
    if not venue or not underlying:
        raise RealDataRejected(f"empty venue/underlying in filename: {path.name}")
    return venue, underlying


def _canonical_fingerprint(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, allow_nan=False).encode("utf-8")
    ).hexdigest()


def _base_candidate_result(path: Path, kind: str) -> Dict[str, Any]:
    return {
        "path": str(path),
        "kind": kind,
        "loaded": False,
        "rejection_reason": None,
        "content_sha256": None,
        "provenance": None,
        "trade_adequacy": None,
        "option_adequacy": None,
        "verdict": "NO-GO",
        "verdict_reason": "not evaluated",
    }


def _evaluate_orderflow_candidate(
    path: Path,
    *,
    bar_duration_seconds: float,
    train_window: int,
    test_window: int,
    step_size: int,
    min_returns: int,
    min_windows: int,
    timestamp: str,
) -> Dict[str, Any]:
    result = _base_candidate_result(path, "orderflow")
    try:
        venue, symbol = _parse_orderflow_name(path)
        content_sha = _content_sha256(path)
        loader = DataLoader(cache=False)
        snapshot = loader.load_orderflow(path, venue=venue, symbol=symbol)
        if not snapshot.trades:
            raise RealDataRejected(f"{path.name}: empty tape")
        venue_str = str(snapshot.venue).strip()
        if not venue_str or venue_str.lower() in _SYNTHETIC_MARKERS:
            raise RealDataRejected(f"{path.name}: synthetic venue {snapshot.venue!r}")
        if not str(snapshot.symbol).strip():
            raise RealDataRejected(f"{path.name}: empty symbol")
        ts_list = [t.timestamp for t in snapshot.trades]
        start, end = min(ts_list), max(ts_list)
        adequacy = _tape_adequacy(
            snapshot,
            bar_duration_seconds,
            train_window,
            test_window,
            step_size,
            min_returns,
            min_windows,
        )
        adequate = bool(adequacy["sample_adequate"])
        result.update(
            {
                "venue": venue_str,
                "symbol": str(snapshot.symbol),
                "loaded": True,
                "content_sha256": content_sha,
                "provenance": {
                    "kind": "real",
                    "path": str(path),
                    "venue": venue_str,
                    "symbol": str(snapshot.symbol),
                    "content_sha256": content_sha,
                    "n_trades": int(len(snapshot.trades)),
                    "start_timestamp": _iso(start),
                    "end_timestamp": _iso(end),
                    "span_seconds": float((end - start).total_seconds()),
                },
                "trade_adequacy": {
                    "n_bars": adequacy["n_bars"],
                    "n_returns": adequacy["n_returns"],
                    "n_windows": adequacy["n_windows"],
                    "n_trades": adequacy["n_trades"],
                    "min_returns": int(min_returns),
                    "min_windows": int(min_windows),
                    "sample_adequate": adequate,
                    "shortfall_returns": max(0, int(min_returns) - adequacy["n_returns"]),
                    "shortfall_windows": max(0, int(min_windows) - adequacy["n_windows"]),
                },
                "verdict": "GO" if adequate else "NO-GO",
                "verdict_reason": (
                    "orderflow tape clears EVAL-22 adequacy floors"
                    if adequate
                    else "orderflow tape below EVAL-22 adequacy floors"
                ),
            }
        )
    except RealDataRejected as exc:
        result["rejection_reason"] = str(exc)
        result["verdict_reason"] = f"rejected candidate: {exc}"
    except Exception as exc:  # noqa: BLE001  (per-candidate isolation)
        result["rejection_reason"] = f"{type(exc).__name__}: {exc}"
        result["verdict_reason"] = f"rejected candidate: {result['rejection_reason']}"
    return result


def _evaluate_options_candidate(
    path: Path,
    *,
    min_contracts: int,
    min_quotes: int,
    min_expiries: int,
    timestamp: str,
) -> Dict[str, Any]:
    result = _base_candidate_result(path, "options")
    try:
        venue, underlying = _parse_options_name(path)
        content_sha = _content_sha256(path)
        loader = DataLoader(cache=False)
        chain = loader.load_options_chain(path, venue=venue, underlying=underlying)
        if not chain.quotes:
            raise RealDataRejected(f"{path.name}: empty chain")
        if not str(chain.underlying).strip():
            raise RealDataRejected(f"{path.name}: empty underlying")
        adequacy = _adequacy_counts(chain, min_contracts, min_quotes, min_expiries)
        adequate = bool(adequacy["sample_adequate"])
        ts_list = [q.timestamp for q in chain.quotes]
        start, end = min(ts_list), max(ts_list)
        result.update(
            {
                "venue": str(chain.venue),
                "underlying": str(chain.underlying),
                "loaded": True,
                "content_sha256": content_sha,
                "provenance": {
                    "kind": "real",
                    "path": str(path),
                    "venue": str(chain.venue),
                    "underlying": str(chain.underlying),
                    "content_sha256": content_sha,
                    "n_quotes": int(len(chain.quotes)),
                    "n_contracts": adequacy["n_contracts"],
                    "n_expiries": adequacy["n_expiries"],
                    "start_timestamp": _iso(start),
                    "end_timestamp": _iso(end),
                    "span_seconds": float((end - start).total_seconds()),
                },
                "option_adequacy": {
                    "n_quotes": adequacy["n_quotes"],
                    "n_contracts": adequacy["n_contracts"],
                    "n_strikes": adequacy["n_strikes"],
                    "n_expiries": adequacy["n_expiries"],
                    "min_contracts": int(min_contracts),
                    "min_quotes": int(min_quotes),
                    "min_expiries": int(min_expiries),
                    "sample_adequate": adequate,
                    "shortfall_contracts": adequacy["shortfall_contracts"],
                    "shortfall_quotes": adequacy["shortfall_quotes"],
                    "shortfall_expiries": adequacy["shortfall_expiries"],
                },
                "verdict": "GO" if adequate else "NO-GO",
                "verdict_reason": (
                    "option chain clears EVAL-24 adequacy floors"
                    if adequate
                    else "option chain below EVAL-24 adequacy floors"
                ),
            }
        )
    except RealDataRejected as exc:
        result["rejection_reason"] = str(exc)
        result["verdict_reason"] = f"rejected candidate: {exc}"
    except Exception as exc:  # noqa: BLE001  (per-candidate isolation)
        result["rejection_reason"] = f"{type(exc).__name__}: {exc}"
        result["verdict_reason"] = f"rejected candidate: {result['rejection_reason']}"
    return result


def evaluate_real_data_falsification(
    *,
    repo_root: str | Path = ".",
    write: bool = True,
    out_dir: Path = OUT_DIR,
    data_dir: Path | None = None,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    train_window: int = DEFAULT_TRAIN_WINDOW,
    test_window: int = DEFAULT_TEST_WINDOW,
    step_size: int = DEFAULT_STEP_SIZE,
    min_returns: int = DEFAULT_MIN_RETURNS,
    min_windows: int = DEFAULT_MIN_WINDOWS,
    min_contracts: int = DEFAULT_MIN_CONTRACTS,
    min_quotes: int = DEFAULT_MIN_QUOTES,
    min_expiries: int = DEFAULT_MIN_EXPIRIES,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Discover, validate and gate every candidate real-data export.

    Returns a sealed verdict dict (never raises). Overall GO only when at least
    one real orderflow tape clears EVAL-22 adequacy AND at least one real
    option chain clears EVAL-24 adequacy; otherwise an explicit, sealable
    NO-GO documenting the shortfall or the absence of real candidates.
    """
    stamp = timestamp or _utc_now_iso()
    repo_root = Path(repo_root)
    data_dir = Path(data_dir) if data_dir is not None else repo_root / DEFAULT_DATA_DIR
    candidates = _discover_candidates(data_dir)

    evaluated: List[Dict[str, Any]] = []
    for path in candidates:
        lowered = path.name.lower()
        if lowered.startswith("orderflow_"):
            result = _evaluate_orderflow_candidate(
                path,
                bar_duration_seconds=bar_duration_seconds,
                train_window=train_window,
                test_window=test_window,
                step_size=step_size,
                min_returns=min_returns,
                min_windows=min_windows,
                timestamp=stamp,
            )
        else:
            result = _evaluate_options_candidate(
                path,
                min_contracts=min_contracts,
                min_quotes=min_quotes,
                min_expiries=min_expiries,
                timestamp=stamp,
            )
        evaluated.append(result)

    n_orderflow = sum(1 for c in evaluated if c["kind"] == "orderflow")
    n_options = sum(1 for c in evaluated if c["kind"] == "options")
    n_adequate_orderflow = sum(
        1 for c in evaluated if c["kind"] == "orderflow" and c["verdict"] == "GO"
    )
    n_adequate_options = sum(
        1 for c in evaluated if c["kind"] == "options" and c["verdict"] == "GO"
    )

    if n_adequate_orderflow >= 1 and n_adequate_options >= 1:
        overall = "GO"
        overall_reason = (
            "adequate real orderflow tape(s) and option chain(s) passed the "
            "EVAL-22 / EVAL-24 adequacy floors"
        )
    elif len(candidates) == 0:
        overall = "NO-GO"
        overall_reason = (
            "no real-data candidates under data/raw/ (all exports are "
            "synthetic or absent); synthetic never substituted"
        )
    else:
        overall = "NO-GO"
        reasons = "; ".join(
            f"{c['kind']}:{Path(c['path']).name} -> {c['verdict_reason']}"
            for c in evaluated
        )
        overall_reason = f"no adequate real tape and/or option chain; candidates: {reasons}"

    fingerprint_payload = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "n_candidates": len(evaluated),
        "n_orderflow_candidates": n_orderflow,
        "n_options_candidates": n_options,
        "n_adequate_orderflow": n_adequate_orderflow,
        "n_adequate_options": n_adequate_options,
        "overall_verdict": overall,
                "candidates": [
            {
                "path": c["path"],
                "kind": c["kind"],
                "venue": c.get("venue"),
                "symbol_or_underlying": c.get("symbol") or c.get("underlying"),
                "loaded": c["loaded"],
                "verdict": c["verdict"],
                "content_sha256": c["content_sha256"],
            }
            for c in evaluated
        ],
    }

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "data_provenance": "real",
        "authenticity_verified": False,
        "repo_root": str(repo_root),
        "data_dir": str(data_dir),
        "floors": {
            "min_returns": int(min_returns),
            "min_windows": int(min_windows),
            "bar_duration_seconds": float(bar_duration_seconds),
            "min_contracts": int(min_contracts),
            "min_quotes": int(min_quotes),
            "min_expiries": int(min_expiries),
        },
        "n_candidates": len(evaluated),
        "n_orderflow_candidates": n_orderflow,
        "n_options_candidates": n_options,
        "n_adequate_orderflow": n_adequate_orderflow,
        "n_adequate_options": n_adequate_options,
        "candidates": evaluated,
        "overall_verdict": overall,
        "overall_reason": overall_reason,
        "canonical_fingerprint": _canonical_fingerprint(fingerprint_payload),
    }

    serialized = serialize_metrics_strict(report)
    assert_json_valid(serialized)

    artifact_paths: Dict[str, str] = {}
    if write:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        filename_stamp = _stamp_for_filename(stamp)
        json_path = out / f"REAL_DATA_FALSIFICATION_{filename_stamp}.json"
        md_path = out / f"REAL_DATA_FALSIFICATION_{filename_stamp}.md"
        artifact_paths = {"json": str(json_path), "md": str(md_path)}
        serialized["artifact_paths"] = artifact_paths
        json_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")

    result = dict(serialized)
    result["artifact_paths"] = artifact_paths
    return result


def _write_markdown(report: Dict[str, Any]) -> str:
    lines = [
        f"# {report['report_id']} — REAL_DATA_FALSIFICATION (EVAL-25)",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- overall_verdict: **{report['overall_verdict']}**",
        f"- reason: {report['overall_reason']}",
        f"- trading_mode: {report['trading_mode']}",
        f"- data_provenance: {report['data_provenance']} "
        f"(authenticity_verified={str(report['authenticity_verified']).lower()})",
        f"- repo_root: `{report['repo_root']}`",
        f"- data_dir: `{report['data_dir']}`",
        f"- candidates discovered: {report['n_candidates']} "
        f"(orderflow {report['n_orderflow_candidates']}, options {report['n_options_candidates']})",
        f"- adequate real: orderflow {report['n_adequate_orderflow']}, "
        f"options {report['n_adequate_options']}",
        f"- floors: {report['floors']}",
        f"- canonical_fingerprint: `{report['canonical_fingerprint']}`",
        "",
        "## Candidates",
    ]
    for c in report["candidates"]:
        lines.append("")
        lines.append(f"### `{Path(c['path']).name}` ({c['kind']})")
        if not c.get("loaded", False):
            lines.append(f"- NOT LOADED: {c.get('rejection_reason') or c.get('verdict_reason')}")
            continue
        p = c.get("provenance") or {}
        lines.extend(
            [
                f"- venue/symbol: `{p.get('venue')}` / `{p.get('symbol') or p.get('underlying')}`",
                f"- content_sha256: `{str(p.get('content_sha256'))[:16]}…`",
                f"- verdict: **{c['verdict']}** — {c['verdict_reason']}",
            ]
        )
        ta = c.get("trade_adequacy") or {}
        oa = c.get("option_adequacy") or {}
        if ta:
            lines.append(
                "- trade adequacy (EVAL-22): "
                f"{ta['n_returns']}/{ta['min_returns']} returns, "
                f"{ta['n_windows']}/{ta['min_windows']} windows, "
                f"adequate={str(ta['sample_adequate']).lower()}"
            )
        if oa:
            lines.append(
                "- option adequacy (EVAL-24): "
                f"{oa['n_contracts']}/{oa['min_contracts']} contracts, "
                f"{oa['n_quotes']}/{oa['min_quotes']} quotes, "
                f"{oa['n_expiries']}/{oa['min_expiries']} expiries, "
                f"adequate={str(oa['sample_adequate']).lower()}"
            )
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "Offline deterministic gate; no network, no ``.env``, no live trading. "
            "Synthetic is never relabeled as real and the artifact never contains "
            "``{\"valid\": true}``. A GO requires at least one adequate real orderflow "
            "tape AND at least one adequate real option chain; otherwise NO-GO stands "
            "and EVAL-23 / EVAL-24 remain data-blocked.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Real-data falsification-readiness gate (EVAL-25, paper-only)"
    )
    parser.add_argument("--repo", type=str, default=".", help="repository root")
    parser.add_argument("--out", type=str, default=str(OUT_DIR), help="artifact directory")
    parser.add_argument(
        "--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="raw data directory"
    )
    parser.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    parser.add_argument("--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS)
    parser.add_argument("--min-returns", type=int, default=DEFAULT_MIN_RETURNS)
    parser.add_argument("--min-windows", type=int, default=DEFAULT_MIN_WINDOWS)
    parser.add_argument("--min-contracts", type=int, default=DEFAULT_MIN_CONTRACTS)
    parser.add_argument("--min-quotes", type=int, default=DEFAULT_MIN_QUOTES)
    parser.add_argument("--min-expiries", type=int, default=DEFAULT_MIN_EXPIRIES)
    args = parser.parse_args(argv)

    # Offline guarantee for the CLI run: refuse any network access.
    _original_create_connection = socket.create_connection

    def _guard_create_connection(*a, **k):  # type: ignore[no-untyped-def]
        raise AssertionError("EVAL-25 gate attempted a network call; offline only")

    socket.create_connection = _guard_create_connection  # type: ignore[method-assign]
    try:
        report = evaluate_real_data_falsification(
            repo_root=args.repo,
            write=not args.no_write,
            out_dir=Path(args.out),
            data_dir=Path(args.data_dir),
            bar_duration_seconds=args.bar_duration_seconds,
            min_returns=args.min_returns,
            min_windows=args.min_windows,
            min_contracts=args.min_contracts,
            min_quotes=args.min_quotes,
            min_expiries=args.min_expiries,
            timestamp=args.timestamp,
        )
    finally:
        socket.create_connection = _original_create_connection  # type: ignore[assignment]

    print(
        json.dumps(
            {
                "overall_verdict": report["overall_verdict"],
                "n_candidates": report["n_candidates"],
                "n_adequate_orderflow": report["n_adequate_orderflow"],
                "n_adequate_options": report["n_adequate_options"],
                "artifact_paths": report["artifact_paths"],
                "canonical_fingerprint": report["canonical_fingerprint"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

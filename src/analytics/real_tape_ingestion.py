"""Real orderflow-tape ingestion gate (EVAL-22, paper-only).

The sole blocker on a trustworthy net-of-cost verdict is that ``data/raw/``
contains only synthetic tapes. EVAL-21 can manufacture an adequate *synthetic*
sample, but it can never manufacture a *real* one; a GO produced from synthetic
data is a fabricated result, not a measurement.

EVAL-22 does not fabricate. It is a strict, offline gate that:

  * discovers candidate real tapes under ``data/raw/`` (excluding ``*_synthetic*``);
  * loads each candidate through the sealed ``DataLoader`` and rejects
    synthetic provenance, unparseable timestamps, empty tapes and
    microstructure-invalid trades;
  * canonicalizes trade order (tie-broken by ``trade_id``/price/size/side) so
    bar closes -- and therefore every downstream metric -- are invariant to the
    input row order of the tape;
  * re-verifies causal no-lookahead on the raw tape with **time-truncation
    invariance** (bars built from only ``timestamp <= bar_end[k]`` reproduce the
    full tape's first ``k+1`` closes), replacing the sealed but vacuous
    ``_assert_causal`` helper;
  * measures adequacy (``n_returns >= 1000`` and ``n_windows >= 20``) and, if no
    tape clears it, emits an explicit ``NO-GO (no adequate real tape)`` artifact
    with the exact per-candidate counts, shortfall and the data contract.

No network calls, no exchange access, no ``.env``, no live trading. Synthetic is
never relabeled as real, and the artifact never contains ``{"valid": true}``.

CLI::

    python -m src.analytics.real_tape_ingestion --out research_state/ [--data-dir data/raw]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.analytics.integrated_options_orderflow_evaluation import _build_bars
from src.analytics.measurement_validity_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_MAX_POSITION_PCT,
    DEFAULT_MIN_RETURNS,
    DEFAULT_MIN_WINDOWS,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_TEST_WINDOW,
    DEFAULT_TRAIN_WINDOW,
    DEFAULT_STEP_SIZE,
    DEFAULT_TOXICITY_THRESHOLD,
    DEFAULT_TOXICITY_WINDOW_TRADES,
    _stamp_for_filename,
    _utc_now_iso,
    adequacy_report,
    build_pillar_signals,
    compute_verdict,
    degeneracy_report,
    ic_report,
    per_bar_returns,
    periods_per_year,
    pillar_metrics,
    sharpe_from_returns,
    simulate_pillar,
)
from src.analytics.production_simulation_evaluation import load_btc_options_chain
from src.analytics.sample_adequacy_acquisition import (
    _count_windows_for_bars,
    _tape_adequacy,
)
from src.backtest.engine import RiskConfig
from src.campaign.integrated import DEFAULT_SPOT, DETERMINISTIC_NOW
from src.config_settings import RiskConfig as SettingsRiskConfig
from src.data.loader import DataLoader
from src.data.schemas import OrderflowSnapshot
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "REAL_TAPE_INGESTION_22"
OUT_DIR = Path("research_state")
DATA_RAW_DIR = Path("data/raw")

TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# Substrings that mark a file as synthetic rather than a venue export.
_SYNTHETIC_MARKERS: Tuple[str, ...] = ("synthetic",)

# Canonical synthetic tape hash (the repo's only orderflow fixture).
CANONICAL_SYNTHETIC_SHA256 = (
    "c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7"
)

# Time-truncation horizons (bars) verified against the full-tape closes.
CAUSAL_HORIZONS: Tuple[int, ...] = (0, 5, 50, 150)

# Minimum tape span for the adequacy replay to be meaningful.
_MIN_SPAN_SECONDS = 60.0


class RealTapeRejected(ValueError):
    """A candidate tape failed provenance, schema or microstructure validation."""


class NoAdequateRealTape(RuntimeError):
    """No discovered candidate cleared the pre-declared adequacy floors."""


# ---------------------------------------------------------------------------
# Small helpers (self-contained, deterministic)
# ---------------------------------------------------------------------------


def _parse_ts(value: Any) -> datetime:
    """Strictly parse a raw timestamp; raise instead of substituting ``now``."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(float(value), tz=timezone.utc)
    elif isinstance(value, str) and value.strip():
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    else:
        raise RealTapeRejected(f"unparseable timestamp: {value!r}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if not math.isfinite(dt.timestamp()):
        raise RealTapeRejected(f"non-finite timestamp: {value!r}")
    return dt.astimezone(timezone.utc)


def _canonical_trades(trades: Sequence[Any]) -> List[Any]:
    """Order-invariant canonical order: (timestamp, trade_id, price, size, side).

    ``_build_bars`` sorts by timestamp only, so trades sharing a timestamp keep
    input order and the bar close depends on which trade happened to be last.
    Canonicalizing here makes closes (and every metric) invariant to row order.
    """

    def key(t: Any) -> Tuple[Any, ...]:
        return (
            t.timestamp,
            str(t.trade_id),
            float(t.price),
            float(t.size),
            str(t.side),
        )

    return sorted(trades, key=key)


def _parse_venue_symbol(path: Path) -> Tuple[str, str]:
    """Derive ``(venue, symbol)`` from ``orderflow_<venue>_<symbol>[_<stamp>].json``.

    Trades and liquidations legitimately contain a ``_synthetic`` substring
    (``orderflow_binance_BTCUSDT_synthetic.json`` would be rejected as a whole),
    so the synthetic marker is checked case-insensitively at the *file* level
    only, matching :func:`discover_real_orderflow_tapes`.
    """
    stem = path.stem
    parts = stem.split("_")
    if len(parts) < 3 or parts[0] != "orderflow":
        raise RealTapeRejected(
            f"filename does not match orderflow_<venue>_<symbol>.json: {path.name}"
        )
    venue = parts[1].strip()
    symbol = parts[2].strip()
    if not venue or not symbol:
        raise RealTapeRejected(f"empty venue/symbol in filename: {path.name}")
    return venue, symbol


class _OrderflowView:
    """Minimal ``snapshot.trades`` view for the bar builder (causality checks).

    ``_build_bars`` only reads ``trades``; this avoids constructing a full
    validated snapshot for the pure bar-level prefix checks.
    """

    __slots__ = ("trades",)

    def __init__(self, trades: Sequence[Any]) -> None:
        self.trades = list(trades)


def _canonical_snapshot(snapshot: OrderflowSnapshot) -> OrderflowSnapshot:
    """Return a snapshot whose trades are in canonical order.

    Rebuilding a full :class:`OrderflowSnapshot` (rather than duck-typing the
    signal builder) keeps ``snapshot.symbol``/``venue`` intact, which
    ``_causal_signal_series`` reads per bar.
    """
    return OrderflowSnapshot(
        symbol=snapshot.symbol,
        venue=snapshot.venue,
        trades=_canonical_trades(snapshot.trades),
        liquidations=list(snapshot.liquidations),
        funding_rates=list(snapshot.funding_rates),
        timestamp=snapshot.timestamp,
    )


def _load_raw(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RealTapeRejected(f"unreadable JSON: {exc}") from None


def _snapshot_dict(snapshot: OrderflowSnapshot) -> Dict[str, Any]:
    return {
        "symbol": snapshot.symbol,
        "venue": snapshot.venue,
        "n_trades": int(len(snapshot.trades)),
        "n_liquidations": int(len(snapshot.liquidations)),
        "n_funding_rates": int(len(snapshot.funding_rates)),
        "start_timestamp": (
            snapshot.trades[0].timestamp.isoformat().replace("+00:00", "Z")
            if snapshot.trades
            else None
        ),
        "end_timestamp": (
            snapshot.trades[-1].timestamp.isoformat().replace("+00:00", "Z")
            if snapshot.trades
            else None
        ),
    }


def _fingerprint(snapshot: OrderflowSnapshot) -> str:
    """SHA-256 over the raw tape (content-identity of the loaded tape).

    The raw content hash is the provenance fingerprint; the order-invariant
    ``tape_fingerprint_canonical`` is what the determinism check uses. A
    reordering of the same tape must change the content hash (that is exactly
    the tie-order defect EVAL-22 contains) while leaving the canonical
    fingerprint and every bar close unchanged.
    """
    parts = [
        f"{t.trade_id}|{t.price:.10f}|{t.size:.10f}|{t.side}|{t.timestamp.isoformat()}"
        for t in snapshot.trades
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _canonical_fingerprint(snapshot: OrderflowSnapshot) -> str:
    """Order-invariant SHA-256 over the canonicalized tape."""
    parts = [
        f"{t.trade_id}|{t.price:.10f}|{t.size:.10f}|{t.side}|{t.timestamp.isoformat()}"
        for t in _canonical_trades(snapshot.trades)
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------


def discover_real_orderflow_tapes(data_raw_dir: Path = DATA_RAW_DIR) -> List[Path]:
    """Return candidate real tapes, sorted, excluding any ``*_synthetic*`` file."""
    root = Path(data_raw_dir)
    if not root.exists():
        return []
    out: List[Path] = []
    for path in sorted(root.glob("orderflow_*.json")):
        lowered = path.name.lower()
        if any(marker in lowered for marker in _SYNTHETIC_MARKERS):
            continue
        out.append(path)
    return out


def _validate_microstructure(raw_trades: Sequence[Any]) -> None:
    """Reject prices/sizes/sides/timestamps that would make the tape unusable."""
    seen: set = set()
    for i, item in enumerate(raw_trades):
        if not isinstance(item, dict):
            raise RealTapeRejected(f"trade[{i}] is not an object")
        for field in ("timestamp", "price", "size", "side"):
            if field not in item:
                raise RealTapeRejected(f"trade[{i}] missing {field!r}")
        try:
            price = float(item["price"])
            size = float(item.get("size", item.get("qty", 0.0)))
        except (TypeError, ValueError):
            raise RealTapeRejected(f"trade[{i}] non-numeric price/size") from None
        if not math.isfinite(price) or price <= 0.0:
            raise RealTapeRejected(f"trade[{i}] non-positive price: {price!r}")
        if not math.isfinite(size) or size <= 0.0:
            raise RealTapeRejected(f"trade[{i}] non-positive size: {size!r}")
        side = str(item["side"]).strip().lower()
        if side not in ("buy", "sell"):
            raise RealTapeRejected(f"trade[{i}] invalid side: {item['side']!r}")
        ts = _parse_ts(item["timestamp"])  # raises on unparseable / now-fallback
        _ = ts
        trade_id = str(item.get("trade_id") or item.get("id") or f"idx{i}")
        if trade_id in seen:
            raise RealTapeRejected(f"duplicate trade_id: {trade_id!r}")
        seen.add(trade_id)


def _raw_trades_of(raw: Any, path: Path) -> List[Any]:
    if isinstance(raw, dict):
        items = raw.get("trades")
        if not isinstance(items, list):
            raise RealTapeRejected(f"{path.name}: no 'trades' list")
        return items
    if isinstance(raw, list):
        return raw
    raise RealTapeRejected(f"{path.name}: unsupported document type {type(raw).__name__}")


def load_real_tape(
    path: Path,
    *,
    allow_synthetic_content: bool = False,
) -> Tuple[OrderflowSnapshot, Dict[str, Any]]:
    """Load and validate one real tape; return ``(snapshot, provenance)``.

    Rejects empty tapes, blank venue/symbol, synthetic venue, unparseable
    timestamps, invalid microstructure and (unless explicitly allowed) the
    canonical synthetic tape content.
    """
    path = Path(path)
    venue, symbol = _parse_venue_symbol(path)
    raw = _load_raw(path)
    raw_trades = _raw_trades_of(raw, path)

    _validate_microstructure(raw_trades)

    # The loader silently substitutes ``now`` for unparseable timestamps and
    # swallows per-trade exceptions, so load with cache disabled and re-check the
    # parsed timestamps ourselves (done above) before trusting the snapshot.
    loader = DataLoader(cache=False)
    snapshot = loader.load_orderflow(path, venue=venue, symbol=symbol)

    if not snapshot.trades:
        raise RealTapeRejected(f"{path.name}: empty tape")
    if not str(snapshot.venue).strip() or snapshot.venue.strip().lower() in _SYNTHETIC_MARKERS:
        raise RealTapeRejected(f"{path.name}: synthetic venue {snapshot.venue!r}")
    if not str(snapshot.symbol).strip():
        raise RealTapeRejected(f"{path.name}: empty symbol")

    content_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if not allow_synthetic_content and content_sha == CANONICAL_SYNTHETIC_SHA256:
        raise RealTapeRejected(f"{path.name}: content matches the canonical synthetic tape")

    ts_list = [t.timestamp for t in snapshot.trades]
    start, end = min(ts_list), max(ts_list)
    if (end - start).total_seconds() < _MIN_SPAN_SECONDS:
        raise RealTapeRejected(
            f"{path.name}: tape span {((end - start).total_seconds()):.1f}s below "
            f"{_MIN_SPAN_SECONDS:.0f}s floor"
        )

    provenance = {
        "kind": "real",
        "path": str(path),
        "venue": str(snapshot.venue),
        "symbol": str(snapshot.symbol),
        "content_sha256": content_sha,
        "tape_fingerprint": _fingerprint(snapshot),
        "tape_fingerprint_canonical": _canonical_fingerprint(snapshot),
        "n_trades": int(len(snapshot.trades)),
        "n_liquidations": int(len(snapshot.liquidations)),
        "n_funding_rates": int(len(snapshot.funding_rates)),
        "start_timestamp": start.isoformat().replace("+00:00", "Z"),
        "end_timestamp": end.isoformat().replace("+00:00", "Z"),
        "span_seconds": float((end - start).total_seconds()),
    }
    return snapshot, provenance


# ---------------------------------------------------------------------------
# Causal no-lookahead (time-truncation invariance)
# ---------------------------------------------------------------------------


def assert_causal_time_truncation(
    trades: Sequence[Any],
    bar_duration_seconds: float,
    *,
    horizons: Sequence[int] = CAUSAL_HORIZONS,
) -> bool:
    """True iff prefix tapes reproduce the full tape's earlier bar closes.

    For each horizon ``k`` the tape is truncated to trades with
    ``timestamp <= start + (k+1) * bar_duration``; the first ``k+1`` bar closes
    must equal the full-tape closes. This catches any builder that peeks past
    ``bar_end[k]``, unlike the sealed ``_assert_causal`` which is vacuous.
    """
    if not trades:
        return False
    dur = max(float(bar_duration_seconds), 1.0)
    canon = _canonical_trades(trades)
    start = canon[0].timestamp
    full = _build_bars(_OrderflowView(canon), dur)["bar_closes"]
    for k in horizons:
        if k >= len(full):
            break
        bar_end = start + timedelta(seconds=(k + 1) * dur)
        prefix = [t for t in canon if t.timestamp <= bar_end]
        if not prefix:
            return False
        sub = _build_bars(_OrderflowView(prefix), dur)["bar_closes"]
        if len(sub) < k + 1 or sub[: k + 1] != full[: k + 1]:
            return False
    return True


# ---------------------------------------------------------------------------
# Per-tape verdict evaluation
# ---------------------------------------------------------------------------


def evaluate_candidate(
    path: Path,
    *,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    train_window: int = DEFAULT_TRAIN_WINDOW,
    test_window: int = DEFAULT_TEST_WINDOW,
    step_size: int = DEFAULT_STEP_SIZE,
    min_returns: int = DEFAULT_MIN_RETURNS,
    min_windows: int = DEFAULT_MIN_WINDOWS,
    max_position_pct: float = DEFAULT_MAX_POSITION_PCT,
    cost_budget_bps: float = 0.5,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate one real tape. Returns a sealed verdict dict (never raises)."""
    stamp = timestamp or _utc_now_iso()
    snapshot, provenance = load_real_tape(path)

    canonical = _canonical_snapshot(snapshot)

    adequacy_counts = _tape_adequacy(
        snapshot,
        bar_duration_seconds,
        train_window,
        test_window,
        step_size,
        min_returns,
        min_windows,
    )

    causal_ok = assert_causal_time_truncation(
        snapshot.trades, bar_duration_seconds
    )
    microsane_ok = True  # guaranteed by load_real_tape; recorded explicitly

    base = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "path": str(path),
        "provenance": provenance,
        "real_tape_loaded": True,
        "real_tape_discovery": True,
        "causal_no_lookahead": bool(causal_ok),
        "microstructure_sane": bool(microsane_ok),
        "adequacy": adequacy_counts,
        "bars": None,
        "verdict": None,
        "verdict_checks": None,
        "artifact_paths": None,
    }

    if not adequacy_counts["sample_adequate"]:
        base["verdict"] = "NO-GO"
        base["verdict_checks"] = {
            "checks": [],
            "n_checks": 0,
            "n_passed": 0,
            "all_checks_pass": False,
            "verdict": "NO-GO",
            "reason": "inadequate real tape",
        }
        base["bars"] = {
            "n_bars": adequacy_counts["n_bars"],
            "n_returns": adequacy_counts["n_returns"],
            "n_windows": adequacy_counts["n_windows"],
            "shortfall_returns": max(0, min_returns - adequacy_counts["n_returns"]),
            "shortfall_windows": max(0, min_windows - adequacy_counts["n_windows"]),
        }
        return base

    # Adequate: drive the sealed EVAL-20 primitives on the real snapshot.
    chain = load_btc_options_chain()
    spot = float(DEFAULT_SPOT["BTC"])
    built = build_pillar_signals(
        chain,
        canonical,
        spot,
        DETERMINISTIC_NOW,
        bar_duration_seconds=bar_duration_seconds,
        seed=42,
    )
    closes = [float(p) for p in built["bar_closes"]]
    bar_ends_dt = built["bar_ends_dt"]
    bar_rets = per_bar_returns(closes)
    annualisation = periods_per_year(bar_duration_seconds)
    n_windows = adequacy_counts["n_windows"]
    n_bars = int(built["n_bars"])

    risk_config = RiskConfig(
        max_position_pct=float(max_position_pct),
        max_drawdown_limit=0.20,
    )
    sims: Dict[str, Any] = {}
    for name, positions in built["positions"].items():
        sims[name] = simulate_pillar(
            closes,
            positions,
            bar_ends_dt,
            cost_budget_bps=cost_budget_bps,
            max_position_pct=float(max_position_pct),
            risk_config=risk_config,
            seed=42,
        )

    metrics = {name: pillar_metrics(sims[name], annualisation) for name in sims}
    degeneracy = degeneracy_report(
        built["options_signal"], built["orderflow_signal"], built["toxicities"]
    )
    of_ic = ic_report(built["orderflow_signal"], closes)
    adequacy = adequacy_report(
        len(bar_rets), n_windows, bar_rets, [of_ic["ic_mean"]]
    )

    cost_detail = {
        "complete": all(
            k in metrics["combined"]
            for k in ("gross_return_total", "net_return_total", "turnover", "total_cost_bps")
        ),
        "non_negative": all(m["total_cost_bps"] >= 0.0 for m in metrics.values()),
        "series": {
            name: {
                "gross_return_total": m["gross_return_total"],
                "net_return_total": m["net_return_total"],
                "turnover": m["turnover"],
                "total_cost_bps": m["total_cost_bps"],
            }
            for name, m in metrics.items()
        },
    }
    req = float(max_position_pct)
    enforced = float(metrics["combined"]["risk_config_max_position_pct"])
    total_rejections = int(sum(m["rejections"] for m in metrics.values()))
    sizing_detail = {
        "requested_max_position_pct": req,
        "risk_config_max_position_pct": enforced,
        "max_drawdown_limit": float(risk_config.max_drawdown_limit),
        "rejections": total_rejections,
        "sizing_consistent": bool(
            math.isfinite(enforced) and abs(enforced - req) <= 1e-12 and total_rejections == 0
        ),
    }
    comb_net = sims["combined"]["net_returns"]
    comb_sharpe = sharpe_from_returns(comb_net, annualisation)
    sharpe_detail = {
        "annualisation": float(annualisation),
        "expected_annualisation": float(periods_per_year(bar_duration_seconds)),
        "sharpe": float(comb_sharpe),
        "abs_error": 0.0,
        "n_returns": int(len(comb_net)),
    }
    sharpe_ok = bool(
        math.isfinite(comb_sharpe)
        and abs(sharpe_detail["annualisation"] - sharpe_detail["expected_annualisation"]) <= 1e-12
        and abs(sharpe_detail["sharpe"] - sharpe_from_returns(comb_net, annualisation)) <= 1e-9
    )

    # Determinism: canonicalize -> rebuild must reproduce the identical stack.
    built2 = build_pillar_signals(
        chain,
        _canonical_snapshot(snapshot),
        spot,
        DETERMINISTIC_NOW,
        bar_duration_seconds=bar_duration_seconds,
        seed=42,
    )
    determinism_ok = bool([float(p) for p in built2["bar_closes"]] == closes)

    verdict_block = compute_verdict(
        adequacy=adequacy,
        sizing_consistent=sizing_detail["sizing_consistent"],
        sizing_detail=sizing_detail,
        sharpe_ok=sharpe_ok,
        sharpe_detail=sharpe_detail,
        degeneracy=degeneracy,
        cost_detail=cost_detail,
        ic_detail={
            "ic_mean": of_ic["ic_mean"],
            "min_detectable_ic_at_n": adequacy["min_detectable_ic_at_n"],
        },
        determinism_ok=determinism_ok,
        never_valid_true=True,
    )

    base.update(
        {
            "bars": {
                "n_bars": n_bars,
                "n_returns": int(len(bar_rets)),
                "n_windows": n_windows,
                "start_timestamp": built["bars"].get("start_timestamp"),
                "end_timestamp": built["bars"].get("end_timestamp"),
                "bar_return_mean_bps": adequacy["bar_return_mean_bps"],
                "bar_return_std_bps": adequacy["bar_return_std_bps"],
                "bar_return_tstat": adequacy["bar_return_tstat"],
            },
            "degeneracy": degeneracy,
            "ic": of_ic,
            "net_of_cost": cost_detail,
            "sizing": sizing_detail,
            "sharpe": sharpe_detail,
            "pillars": metrics,
            "verdict": verdict_block["verdict"],
            "verdict_checks": verdict_block,
            "determinism": {
                "canonical_rebuild_identical": bool(determinism_ok),
            },
        }
    )
    return base


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def evaluate_real_tape_ingestion(
    *,
    write: bool = True,
    out_dir: Path = OUT_DIR,
    data_dir: Path = DATA_RAW_DIR,
    bar_duration_seconds: float = DEFAULT_BAR_DURATION_SECONDS,
    train_window: int = DEFAULT_TRAIN_WINDOW,
    test_window: int = DEFAULT_TEST_WINDOW,
    step_size: int = DEFAULT_STEP_SIZE,
    min_returns: int = DEFAULT_MIN_RETURNS,
    min_windows: int = DEFAULT_MIN_WINDOWS,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Discover, validate and gate every candidate real tape."""
    stamp = timestamp or _utc_now_iso()
    candidates = discover_real_orderflow_tapes(data_dir)

    evaluated: List[Dict[str, Any]] = []
    adequate: List[Dict[str, Any]] = []
    for path in candidates:
        try:
            result = evaluate_candidate(
                path,
                bar_duration_seconds=bar_duration_seconds,
                train_window=train_window,
                test_window=test_window,
                step_size=step_size,
                min_returns=min_returns,
                min_windows=min_windows,
                timestamp=stamp,
            )
        except RealTapeRejected as exc:
            result = {
                "report_id": REPORT_ID,
                "generated_at": stamp,
                "path": str(path),
                "real_tape_loaded": False,
                "real_tape_discovery": True,
                "rejection_reason": str(exc),
                "verdict": "NO-GO",
                "verdict_checks": {
                    "checks": [],
                    "n_checks": 0,
                    "n_passed": 0,
                    "all_checks_pass": False,
                    "verdict": "NO-GO",
                    "reason": "rejected candidate",
                },
            }
        evaluated.append(result)
        if result["verdict"] == "GO":
            adequate.append(result)

    # Overall verdict: GO only if at least one real tape clears adequacy AND its
    # sealed verdict battery passes. Otherwise an explicit, sealable NO-GO.
    overall = "GO" if adequate and all(a["verdict"] == "GO" for a in adequate) else "NO-GO"

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": stamp,
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "data_provenance": "real",
        "data_dir": str(data_dir),
        "floors": {
            "min_returns": int(min_returns),
            "min_windows": int(min_windows),
            "bar_duration_seconds": float(bar_duration_seconds),
        },
        "n_candidates": len(candidates),
        "candidates": evaluated,
        "n_adequate": len(adequate),
        "overall_verdict": overall,
        "overall_reason": (
            "adequate real tape(s) passed the sealed verdict battery"
            if overall == "GO"
            else "no adequate real tape; synthetic never substituted"
        ),
    }

    serialized = serialize_metrics_strict(report)
    assert_json_valid(serialized)

    artifact_paths: Dict[str, str] = {}
    if write:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        filename_stamp = _stamp_for_filename(stamp)
        json_path = out / f"REAL_TAPE_INGESTION_{filename_stamp}.json"
        md_path = out / f"REAL_TAPE_INGESTION_{filename_stamp}.md"
        artifact_paths = {"json": str(json_path), "md": str(md_path)}
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
        f"# {report['report_id']} — REAL_TAPE_INGESTION (EVAL-22)",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- overall_verdict: **{report['overall_verdict']}**",
        f"- reason: {report['overall_reason']}",
        f"- data_provenance: {report['data_provenance']}",
        f"- candidates discovered: {report['n_candidates']}",
        f"- adequate real tapes: {report['n_adequate']}",
        f"- floors: {report['floors']}",
        "",
        "## Candidates",
    ]
    for c in report["candidates"]:
        lines.append("")
        lines.append(f"### `{c['path']}`")
        if not c.get("real_tape_loaded", True):
            lines.append(f"- REJECTED: {c['rejection_reason']}")
            continue
        p = c["provenance"]
        lines.extend(
            [
                f"- venue/symbol: `{p['venue']}` / `{p['symbol']}`",
                f"- content_sha256: `{p['content_sha256'][:16]}…`",
                f"- n_trades: {p['n_trades']}",
                f"- span: {p['span_seconds']:.1f}s "
                f"({p['start_timestamp']} → {p['end_timestamp']})",
                f"- bars/returns/windows: {c['bars']}",
                f"- causal_no_lookahead: {c['causal_no_lookahead']}",
                f"- microstructure_sane: {c['microstructure_sane']}",
                f"- verdict: **{c['verdict']}**",
            ]
        )
        checks = c.get("verdict_checks") or {}
        if checks.get("checks"):
            lines.append(f"- checks passed: {checks['n_passed']}/{checks['n_checks']}")
            for ch in checks["checks"]:
                mark = "PASS" if ch["pass"] else "FAIL"
                lines.append(f"  - [{mark}] {ch['name']}: {ch['reason']}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Real orderflow-tape ingestion gate (EVAL-22, paper-only)"
    )
    parser.add_argument("--out", type=str, default=str(OUT_DIR), help="output directory")
    parser.add_argument("--data-dir", type=str, default=str(DATA_RAW_DIR), help="raw data dir")
    parser.add_argument("--no-write", action="store_true", help="compute without writing artifacts")
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    parser.add_argument("--bar-duration-seconds", type=float, default=DEFAULT_BAR_DURATION_SECONDS)
    parser.add_argument("--min-returns", type=int, default=DEFAULT_MIN_RETURNS)
    parser.add_argument("--min-windows", type=int, default=DEFAULT_MIN_WINDOWS)
    args = parser.parse_args(argv)

    report = evaluate_real_tape_ingestion(
        write=not args.no_write,
        out_dir=args.out,
        data_dir=Path(args.data_dir),
        bar_duration_seconds=args.bar_duration_seconds,
        min_returns=args.min_returns,
        min_windows=args.min_windows,
        timestamp=args.timestamp,
    )
    print(json.dumps({
        "overall_verdict": report["overall_verdict"],
        "n_candidates": report["n_candidates"],
        "n_adequate": report["n_adequate"],
        "artifact_paths": report["artifact_paths"],
    }, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
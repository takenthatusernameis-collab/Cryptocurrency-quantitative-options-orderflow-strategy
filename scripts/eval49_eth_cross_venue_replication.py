#!/usr/bin/env python3
"""EVAL-49: ETH cross-venue combined (fused) options+orderflow net-of-cost falsification.

Thin wrapper around the sealed EVAL-46 integrated options+orderflow audit
(``scripts/eval46_integrated_options_orderflow_audit.py``).  EVAL-46 (BTC) and
EVAL-47 (ETH) sealed ``NO-GO CONFIRMED (PASS)`` on **OKX-only** data (OKX options
+ OKX orderflow).  EVAL-48 tested BTC venue-specificity (Deribit options + OKX BTC
orderflow) and sealed ``NO-GO CONFIRMED (PASS)``.

EVAL-49 fills the **final cross-venue cell**: the same real OKX **ETH** orderflow
tapes used by EVAL-47, with the options leg switched from OKX to **Deribit ETH**.
Only the options venue changes, so any difference is attributable to the options
venue, not to data or orderflow.  This closes venue-specificity for both assets.

The wrapper does **not** edit the sealed eval46 script, the sealed eval47 script,
or any ``src/`` module.  It imports eval46 as a module, overrides the module-level
constants (``OPTIONS_DIR``, ``TAPES``, ``REPORT_ID``, ``PREREG_ID``, ``BLOCKED_ID``,
``CODE_PATHS``, ``COMMANDS``), and monkeypatches ``_build_report`` / ``build_prereg``
to relabel ETH/OKX-specific fields (``verdict_scope``, ``campaign_state``, hypothesis
text) to the ETH cross-venue scope.

Data: real Deribit ETH option snapshots in ``data/raw/eval49/`` (reconstructed from
public ``get_tradingview_chart_data`` 5m closes via
``scripts/eval48_acquire_deribit_options.py --underlying ETH``), aligned to the same
5 real OKX ETH orderflow tapes used by EVAL-47.

Pipeline (identical to EVAL-46/47/48):
  * load N Deribit ETH option snapshots (load_snapshot_signals("ETH", OPTIONS_DIR))
  * load 5 real OKX ETH orderflow tapes (load_real_orderflow("ETH", path))
  * 15 s causal bars + bisect fast signal/toxicity (bit-identical to sealed)
  * align options signal to bars, fuse under 3 pre-registered rules
    (sign_agreement / regime_filter / continuous_zscore) with VPIN toxicity gate
  * walk-forward combined + options-only + orderflow-only + flat per tape
  * 1000-perm paired permutation, 1000-resample block bootstrap (block 2),
    CSCV PBO (k=4), BH-FDR (alpha 0.1), DSR, seed 42
  * seal EVAL_49_PREREGISTRATION_* BEFORE measurement, then
    EVAL_49_ETH_CROSS_VENUE_COMBINED_* (or EVAL_49_BLOCKED_* on error)

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval49_eth_cross_venue_replication.py tests/test_eval49_eth_cross_venue_replication.py
    python3 -m pytest -q tests/test_eval49_eth_cross_venue_replication.py
    # acquire real Deribit ETH options first (writes data/raw/eval49 + manifest):
    python3 scripts/eval48_acquire_deribit_options.py --underlying ETH \
        --start 2026-11-14T20:20:00Z --end 2026-11-15T05:20:00Z \
        --out-dir data/raw/eval49 --manifest-id EVAL_49_DERIBIT_ACQUISITION --seal
    python3 scripts/eval49_eth_cross_venue_replication.py --no-write --max-trades 5000   # smoke
    python3 scripts/eval49_eth_cross_venue_replication.py                               # full seal
    python3 scripts/check_session_sealed.py \
        --task-id "INIT-2026-11-15T08:20:09Z-EVAL-49-ETH-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL" \
        --glob "EVAL_49_*"
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure the project root is importable (mirror eval46's sys.path setup).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the sealed, tested eval46 pipeline as a module (no edits to it).
import scripts.eval46_integrated_options_orderflow_audit as e46  # noqa: E402

# ---------------------------------------------------------------------------
# ETH cross-venue parametrization — override module-level constants on eval46.
# ---------------------------------------------------------------------------
CROSS_VENUE_OPTIONS_DIR = "data/raw/eval49"
ETH_TAPES: Dict[str, str] = {
    "eth_w05": "data/raw/eval45/orderflow_okx_ETH_w05_507849899.json",
    "eth_w04": "data/raw/eval45/orderflow_okx_ETH_w04_507921099.json",
    "eth_w03": "data/raw/eval45/orderflow_okx_ETH_w03_507948099.json",
    "eth_w02": "data/raw/eval45/orderflow_okx_ETH_w02_507990299.json",
    "eth_w01": "data/raw/eval45/orderflow_okx_ETH_w01_508045199.json",
}

REPORT_ID = "EVAL_49_ETH_CROSS_VENUE_COMBINED"
PREREG_ID = "EVAL_49_PREREGISTRATION"
BLOCKED_ID = "EVAL_49_BLOCKED"

TASK_LABEL = "EVAL-49-ETH-CROSS-VENUE-REPLICATION-FALSIFY-AND-SEAL"

CODE_PATHS = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/options_time_varying_signal.py",
    "src/analytics/capacity_aware_tca.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "src/campaign/integrated.py",
    "src/telemetry/serialization.py",
    "src/ingestion/deribit.py",
    "scripts/eval46_integrated_options_orderflow_audit.py",
    "scripts/eval48_acquire_deribit_options.py",
    "scripts/eval49_eth_cross_venue_replication.py",
    "tests/test_eval49_eth_cross_venue_replication.py",
)

COMMANDS = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval48_acquire_deribit_options.py "
    "scripts/eval49_eth_cross_venue_replication.py "
    "tests/test_eval49_eth_cross_venue_replication.py",
    "python3 -m pytest -q tests/test_eval49_eth_cross_venue_replication.py",
    "python3 scripts/eval48_acquire_deribit_options.py --underlying ETH "
    "--start 2026-11-14T20:20:00Z --end 2026-11-15T05:20:00Z "
    "--out-dir data/raw/eval49 --manifest-id EVAL_49_DERIBIT_ACQUISITION --seal",
    "python3 scripts/eval49_eth_cross_venue_replication.py --no-write --max-trades 5000",
    "python3 scripts/eval49_eth_cross_venue_replication.py",
)

# Apply constant overrides on the eval46 module (no edits to eval46 source).
e46.OPTIONS_DIR = CROSS_VENUE_OPTIONS_DIR
e46.TAPES = dict(ETH_TAPES)
e46.REPORT_ID = REPORT_ID
e46.PREREG_ID = PREREG_ID
e46.BLOCKED_ID = BLOCKED_ID
e46.CODE_PATHS = CODE_PATHS
e46.COMMANDS = COMMANDS

# ---------------------------------------------------------------------------
# Monkeypatch _build_report / build_prereg to relabel ETH/OKX -> ETH cross-venue.
# ---------------------------------------------------------------------------
_orig_build_report = e46._build_report
_orig_build_prereg = e46.build_prereg


_CROSS_VENUE_LABELS = [
    ("the available real BTC data", "the available real ETH orderflow + Deribit ETH options data"),
    ("the available real ETH data", "the available real ETH orderflow + Deribit ETH options data"),
    ("both real BTC tapes", "all 5 real ETH orderflow tapes"),
    ("both real ETH tapes", "all 5 real ETH orderflow tapes"),
    ("both real BTC orderflow tapes", "all 5 real ETH orderflow tapes"),
    ("both real ETH orderflow tapes", "all 5 real ETH orderflow tapes"),
    ("across both real BTC tapes", "across all 5 real ETH orderflow tapes"),
    ("across both real ETH tapes", "across all 5 real ETH orderflow tapes"),
    ("on both real BTC tapes", "on all 5 real ETH orderflow tapes"),
    ("on both real ETH tapes", "on all 5 real ETH orderflow tapes"),
    ("options-only", "Deribit-ETH-options-only"),
]


def _relabel(d: Dict[str, Any]) -> Dict[str, Any]:
    """Relabel ETH/OKX-specific prose to the ETH cross-venue scope (recurses dicts)."""
    for key, val in d.items():
        if isinstance(val, str):
            for old, new in _CROSS_VENUE_LABELS:
                val = val.replace(old, new)
            d[key] = val
        elif isinstance(val, dict):
            _relabel(val)
    return d


def _patched_build_report(**kwargs: Any) -> Dict[str, Any]:
    rep = _orig_build_report(**kwargs)
    rep["verdict_scope"] = "FULL_DENSE_ETH_CROSS_VENUE"
    rep["options_venue"] = "deribit"
    rep["orderflow_venue"] = "okx"
    rep["cross_venue_contrast"] = (
        "same real OKX ETH orderflow as EVAL-47; options venue OKX -> Deribit ETH"
    )
    rep["campaign_state"] = (
        "TERMINATED (EVAL-36 TERMINATE_NO_GO); EVAL-37 PASS 9/9; "
        "EVAL-46 BTC combined (OKX) NO-GO CONFIRMED (PASS); "
        "EVAL-47 ETH combined (OKX) NO-GO CONFIRMED (PASS); "
        "EVAL-48 BTC cross-venue (Deribit options + OKX orderflow) NO-GO CONFIRMED (PASS); "
        "EVAL-49 ETH cross-venue (Deribit ETH options + OKX orderflow) in progress"
    )
    _relabel(rep)
    return rep


def _patched_build_prereg(**kwargs: Any) -> Dict[str, Any]:
    p = _orig_build_prereg(**kwargs)
    p["hypothesis"] = (
        "The fused options+orderflow strategy is net-of-cost tradable when the options "
        "leg is sourced from Deribit ETH (a different venue) while orderflow is the same "
        "real OKX ETH tape: at least one pre-declared fusion rule yields combined Sharpe > 0 "
        "with no kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on all "
        "real ETH orderflow tapes."
    )
    p["options_venue"] = "deribit"
    p["orderflow_venue"] = "okx"
    p["verdict_scope"] = "FULL_DENSE_ETH_CROSS_VENUE"
    _relabel(p)
    return p


e46._build_report = _patched_build_report
e46.build_prereg = _patched_build_prereg

# ---------------------------------------------------------------------------
# Per-snapshot spot loader (Deribit ETH).
#
# The sealed signal loader defaults every symbol to the BTC ``REFERENCE_SPOT``
# unless ``spot`` is supplied.  Applied to ETH that saturates the forward/IV
# components and collapses ``options_signal_raw`` to a single value (degenerate
# options leg).  The Deribit ETH acquisition stores a measured per-snapshot spot
# (``spot`` = ETH-PERPETUAL 5m close) in each export; this loader passes it
# through so the ETH cross-venue options signal is non-degenerate.  It reuses the
# sealed ``snapshot_options_signal``/loaders unchanged.
# ---------------------------------------------------------------------------
_orig_load_snapshot_signals = e46.load_snapshot_signals


def _read_snapshot_spot(path: Path) -> Optional[float]:
    try:
        payload = json.loads(Path(path).read_text())
    except Exception:  # noqa: BLE001
        return None
    val = payload.get("spot")
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) and f > 0.0 else None


def _load_snapshot_signals_with_spot(
    symbol: str = "ETH",
    data_raw: Path | str = Path("data/raw"),
    *,
    spot: Optional[float] = None,
    weights: Optional[Dict[str, float]] = None,
) -> list:
    from src.analytics.options_time_varying_signal import (  # noqa: WPS433
        _parse_ts,
        _snapshot_timestamp,
        snapshot_options_signal,
    )
    from src.campaign.integrated import RealDataUnavailable
    from src.data.loader import DataLoader
    from src.data.options_timeseries import discover_all_real_options_exports

    candidates = discover_all_real_options_exports(str(symbol), data_raw)
    if not candidates:
        raise RealDataUnavailable(f"no real option export for {symbol!r} under {data_raw}")
    loader = DataLoader(cache=False)
    out = []
    for path, venue, _underlying in candidates:
        try:
            chain = loader.load_options_chain(str(path), venue=venue, underlying=str(symbol))
            stamp = _snapshot_timestamp(Path(path))
            if not stamp:
                continue
            ts = _parse_ts(stamp)
            snap_spot = _read_snapshot_spot(Path(path))
            use_spot = float(snap_spot if snap_spot is not None else (spot or 0.0)) or None
            if use_spot is None:
                # No measured spot anywhere: fall back to the sealed default path.
                return _orig_load_snapshot_signals(symbol, data_raw, spot=spot, weights=weights)
            sig = snapshot_options_signal(
                chain, use_spot, ts, weights=weights, source_path=path
            )
            out.append(sig)
        except Exception:  # noqa: BLE001 - skip per-snapshot failures, never fake
            continue
    if not out:
        raise RealDataUnavailable(
            f"no real option export for {symbol!r} produced a usable signal"
        )
    out.sort(key=lambda s: s.snapshot_timestamp)
    return out


e46.load_snapshot_signals = _load_snapshot_signals_with_spot


def _build_blocked_report(generated_at: str, exc: BaseException, task_label: str) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-{task_label}",
        "status": "BLOCKED",
        "verdict": "BLOCKED",
        "verdict_reason": "EVAL-49 could not complete; see error.",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "commands": list(COMMANDS),
    }


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(
        description="EVAL-49 ETH cross-venue (Deribit ETH options + OKX ETH orderflow) combined audit"
    )
    ap.add_argument("--no-write", action="store_true",
                    help="run measurement without sealing (smoke test)")
    ap.add_argument("--max-trades", type=int, default=None,
                    help="truncate each tape to the last N trades (smoke test only)")
    ap.add_argument("--options-dir", default=None,
                    help="override the Deribit ETH option snapshot dir (default: data/raw/eval49)")
    ap.add_argument("--tape", action="append", default=[], metavar="NAME=PATH",
                    help="override a roster tape path (repeatable)")
    for key in ETH_TAPES:
        ap.add_argument(f"--{key}-tape", dest=f"tape_{key}", default=None,
                        help=f"override the {key} tape path")
    args = ap.parse_args(argv)

    if args.options_dir:
        e46.OPTIONS_DIR = args.options_dir

    overrides: Dict[str, str] = {}
    for item in args.tape:
        if "=" not in item:
            raise SystemExit(f"--tape expects NAME=PATH, got {item!r}")
        name, path = item.split("=", 1)
        overrides[name.strip()] = path.strip()
    for key in ETH_TAPES:
        val = getattr(args, f"tape_{key}")
        if val:
            overrides[key] = val

    generated_at = e46._utc_now_iso()
    try:
        report = e46.run_eval46(
            write=not args.no_write,
            tape_overrides=overrides or None,
            max_trades=args.max_trades,
            symbol="ETH",
            task_label=TASK_LABEL,
        )
    except Exception as exc:  # noqa: BLE001 - seal a BLOCKED artifact, never silent
        traceback.print_exc()
        paths: Dict[str, str] = {}
        if not args.no_write:
            paths = e46._seal(BLOCKED_ID, _build_blocked_report(generated_at, exc, TASK_LABEL))
        print(json.dumps({
            "report_id": BLOCKED_ID,
            "verdict": "BLOCKED",
            "error": str(exc),
            "blocked_artifact_paths": paths,
        }, sort_keys=True))
        return 1

    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "verdict_scope": report["verdict_scope"],
        "n_tapes": report["pooled"]["n_tapes"],
        "go_rule": report["pooled"]["go_rule"],
        "passed": report["pooled"]["passed"],
        "tape_errors": report.get("tape_errors", []),
        "artifact_paths": report.get("artifact_paths", {}),
        "preregistration_artifact": report.get("preregistration_artifact"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
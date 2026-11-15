#!/usr/bin/env python3
"""EVAL-47: ETH combined (fused) options+orderflow net-of-cost falsification.

Thin wrapper around the sealed EVAL-46 integrated options+orderflow audit
(``scripts/eval46_integrated_options_orderflow_audit.py``).  Parametrizes the
reusable eval46 pipeline for ``symbol="ETH"`` against the git-tracked ETH data
in ``data/raw/eval45/`` (5 orderflow tapes / 207,600 trades + 201 option
snapshots).

This wrapper does **not** edit the sealed eval46 script or any ``src/`` module.
It imports eval46 as a module, overrides the module-level constants
(``OPTIONS_DIR``, ``TAPES``, ``REPORT_ID``, ``PREREG_ID``, ``BLOCKED_ID``,
``CODE_PATHS``, ``COMMANDS``), and monkeypatches ``_build_report`` /
``build_prereg`` to relabel BTC-specific fields (``verdict_scope``,
``campaign_state``, hypothesis text) to ETH.

Pipeline (identical to EVAL-46):
  * load 201 ETH option snapshots  (load_snapshot_signals("ETH", OPTIONS_DIR))
  * load 5 ETH orderflow tapes     (load_real_orderflow("ETH", path))
  * 15 s causal bars + bisect fast signal/toxicity (bit-identical to sealed)
  * align options signal to bars, fuse under 3 pre-registered rules
    (sign_agreement / regime_filter / continuous_zscore) with VPIN toxicity gate
  * walk-forward combined + options-only + orderflow-only + flat per tape
  * 1000-perm paired permutation, 1000-resample block bootstrap (block 2),
    CSCV PBO (k=4), BH-FDR (alpha 0.1), DSR, seed 42
  * seal EVAL_47_PREREGISTRATION_* BEFORE measurement, then EVAL_47_ETH_COMBINED_*
    (or EVAL_47_BLOCKED_* on error)

Usage::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 -m py_compile scripts/eval47_eth_combined_audit.py tests/test_eval47_eth_combined_audit.py
    python3 -m pytest -q tests/test_eval47_eth_combined_audit.py
    python3 scripts/eval47_eth_combined_audit.py --no-write --max-trades 5000   # smoke
    python3 scripts/eval47_eth_combined_audit.py                               # full seal
    python3 scripts/check_session_sealed.py \
        --task-id "INIT-2026-11-15T06:22:20Z-EVAL-47-ETH-COMBINED-CROSS-ASSET-REPLICATION-FALSIFY-AND-SEAL" \
        --glob "EVAL_47_*"
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure the project root is importable (mirror eval46's sys.path setup).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the sealed, tested eval46 pipeline as a module (no edits to it).
import scripts.eval46_integrated_options_orderflow_audit as e46

# ---------------------------------------------------------------------------
# ETH parametrization — override module-level constants on the eval46 module.
# ---------------------------------------------------------------------------
ETH_OPTIONS_DIR = "data/raw/eval45"
ETH_TAPES: Dict[str, str] = {
    "eth_w05": "data/raw/eval45/orderflow_okx_ETH_w05_507849899.json",
    "eth_w04": "data/raw/eval45/orderflow_okx_ETH_w04_507921099.json",
    "eth_w03": "data/raw/eval45/orderflow_okx_ETH_w03_507948099.json",
    "eth_w02": "data/raw/eval45/orderflow_okx_ETH_w02_507990299.json",
    "eth_w01": "data/raw/eval45/orderflow_okx_ETH_w01_508045199.json",
}

REPORT_ID = "EVAL_47_ETH_COMBINED"
PREREG_ID = "EVAL_47_PREREGISTRATION"
BLOCKED_ID = "EVAL_47_BLOCKED"

TASK_LABEL = "EVAL-47-ETH-COMBINED-CROSS-ASSET-REPLICATION-FALSIFY-AND-SEAL"

CODE_PATHS = (
    "src/analytics/integrated_options_orderflow_evaluation.py",
    "src/analytics/options_time_varying_signal.py",
    "src/analytics/capacity_aware_tca.py",
    "src/analytics/real_walkforward_certification.py",
    "src/analytics/strategy_evaluation.py",
    "src/campaign/integrated.py",
    "src/telemetry/serialization.py",
    "scripts/eval46_integrated_options_orderflow_audit.py",
    "scripts/eval47_eth_combined_audit.py",
    "tests/test_eval47_eth_combined_audit.py",
)

COMMANDS = (
    'export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"',
    "python3 -m py_compile scripts/eval47_eth_combined_audit.py "
    "tests/test_eval47_eth_combined_audit.py",
    "python3 -m pytest -q tests/test_eval47_eth_combined_audit.py",
    "python3 scripts/eval47_eth_combined_audit.py --no-write --max-trades 5000",
    "python3 scripts/eval47_eth_combined_audit.py",
)

# Apply constant overrides on the eval46 module (no edits to eval46 source).
e46.OPTIONS_DIR = ETH_OPTIONS_DIR
e46.TAPES = dict(ETH_TAPES)
e46.REPORT_ID = REPORT_ID
e46.PREREG_ID = PREREG_ID
e46.BLOCKED_ID = BLOCKED_ID
e46.CODE_PATHS = CODE_PATHS
e46.COMMANDS = COMMANDS

# ---------------------------------------------------------------------------
# Monkeypatch _build_report / build_prereg to relabel BTC -> ETH.
# ---------------------------------------------------------------------------
_orig_build_report = e46._build_report
_orig_build_prereg = e46.build_prereg


_BTC2ETH = [
    ("both real BTC tapes", "all 5 real ETH tapes"),
    ("both real BTC tapes", "all real ETH tapes"),
    ("the available real BTC data", "the available real ETH data"),
    ("across both real BTC tapes", "across all real ETH tapes"),
]


def _relabel_eth(d: Dict[str, Any]) -> Dict[str, Any]:
    """Reline BTC-specific prose in verdict_reason / go_bar / hypothesis to ETH (EVAL-47 scope).

    Recurses into nested dicts (e.g. ``protocol``) so the pre-registered ``go_bar``
    string is relabeled as well as the top-level report fields.
    """
    for key, val in d.items():
        if isinstance(val, str):
            for old, new in _BTC2ETH:
                val = val.replace(old, new)
            d[key] = val
        elif isinstance(val, dict):
            _relabel_eth(val)
    return d


def _patched_build_report(**kwargs: Any) -> Dict[str, Any]:
    rep = _orig_build_report(**kwargs)
    rep["verdict_scope"] = "FULL_DENSE_ETH"
    rep["campaign_state"] = (
        "TERMINATED (EVAL-36 TERMINATE_NO_GO); EVAL-37 PASS 9/9; "
        "EVAL-46 BTC combined NO-GO CONFIRMED (PASS); EVAL-47 ETH combined in progress"
    )
    _relabel_eth(rep)
    return rep


def _patched_build_prereg(**kwargs: Any) -> Dict[str, Any]:
    p = _orig_build_prereg(**kwargs)
    p["hypothesis"] = (
        "The fused options+orderflow strategy is net-of-cost tradable on dense real ETH "
        "data: at least one pre-declared fusion rule yields combined Sharpe > 0 with no "
        "kill-switch breach, permutation p < 0.05 and bootstrap CI lower > 0 on the ETH tapes."
    )
    _relabel_eth(p)
    return p


e46._build_report = _patched_build_report
e46.build_prereg = _patched_build_prereg


def _build_blocked_report(generated_at: str, exc: BaseException, task_label: str) -> Dict[str, Any]:
    return {
        "report_id": BLOCKED_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-{task_label}",
        "status": "BLOCKED",
        "verdict": "BLOCKED",
        "verdict_reason": "EVAL-47 could not complete; see error.",
        "error_type": type(exc).__name__,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "commands": list(COMMANDS),
    }


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="EVAL-47 ETH combined options+orderflow audit")
    ap.add_argument("--no-write", action="store_true",
                    help="run measurement without sealing (smoke test)")
    ap.add_argument("--max-trades", type=int, default=None,
                    help="truncate each tape to the last N trades (smoke test only)")
    ap.add_argument("--tape", action="append", default=[], metavar="NAME=PATH",
                    help="override a roster tape path (repeatable)")
    for key in ETH_TAPES:
        ap.add_argument(f"--{key}-tape", dest=f"tape_{key}", default=None,
                        help=f"override the {key} tape path")
    args = ap.parse_args(argv)

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
        raise
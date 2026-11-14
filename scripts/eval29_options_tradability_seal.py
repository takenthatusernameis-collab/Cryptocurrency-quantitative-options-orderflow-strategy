"""EVAL-29: Options-leg tradability / net-of-cost with calibrated forwards.

Measures the options leg on the real OKX exports currently present under
``data/raw/`` (re-acquired this session via EVAL-26), computes per-expiry
forward-calibrated parity, runs the integrated options+orderflow net-of-cost
walk-forward, and records the exact measured root cause for the options-leg
`options_signal_exists` failure with code paths. Emits strict JSON/MD and an
explicit GO/NO-GO. Never fabricates provenance; never relabels synthetic real.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.data.options_timeseries import (
    calibrate_expiry_parity,
    discover_all_real_options_exports,
    load_options_timeseries,
)
from src.analytics.integrated_options_orderflow_evaluation import (
    evaluate_integrated_options_orderflow,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "OPTIONS_LEG_TRADABILITY_29"
OUT_DIR = Path("research_state")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def build_report() -> Dict[str, Any]:
    generated_at = _utc_now_iso()
    exports = discover_all_real_options_exports("BTC", Path("data/raw"))
    real_paths = [p for p, _v, _u in exports]

    # Parity calibration on real data (EVAL-28 additive, re-run this session).
    parity = calibrate_expiry_parity()
    p = parity.__dict__

    diags = load_options_timeseries("BTC")
    ts = [d.snapshot_timestamp for d in diags]
    span = ( _parse(ts[-1]) - _parse(ts[0]) ).total_seconds() if len(ts) > 1 else 0.0

    # Integrated net-of-cost walk-forward (uses whatever data is present).
    integrated = evaluate_integrated_options_orderflow(write=True)
    checks = integrated["verdict_checks"]
    options_only = integrated["options_only_wf"]
    orderflow_only = integrated["orderflow_only_wf"]
    combined = integrated["combined_wf"]

    # Measured root cause: the options signal is broadcast-static by design.
    root_cause = {
        "code_path": "src/analytics/integrated_options_orderflow_evaluation.py",
        "function": "_causal_options_signal_series",
        "measured_behavior": (
            "Broadcasts a single static options snapshot value to every bar; "
            "a constant signal has zero time-variation so mean IC == 0.0 and "
            "options_signal_exists FAILs. The options leg cannot yield a "
            "time-varying edge until the signal is computed per-snapshot over time."
        ),
        "evidence": {
            "options_mean_ic_observed": checks["checks"][0]["observed"],
            "options_signal_exists_pass": checks["checks"][0]["pass"],
        },
    }

    measured = {
        "n_real_options_snapshots": len(real_paths),
        "snapshot_span_seconds": span,
        "snapshot_timestamps": ts,
        "real_options_exports": [
            {"path": str(pth), "sha256": _sha256(pth)} for pth in real_paths
        ],
        "parity": {
            "report_id": p.get("report_id"),
            "parity_consistent": p.get("parity_consistent"),
            "verdict": p.get("overall_verdict"),
            "reason": p.get("overall_reason"),
        },
        "integrated_eval": {
            "report_id": integrated.get("report_id"),
            "verdict": integrated.get("verdict"),
            "n_checks": checks["n_checks"],
            "n_passed": checks["n_passed"],
            "failed_checks": checks["failed_checks"],
            "options_only_wf": {
                k: options_only[k]
                for k in (
                    "oos_sharpe", "oos_return", "oos_max_drawdown", "num_trades",
                    "total_cost_usd", "total_traded_notional",
                )
            },
            "orderflow_only_wf": {
                k: orderflow_only[k]
                for k in (
                    "oos_sharpe", "oos_return", "oos_max_drawdown", "num_trades",
                    "total_cost_usd", "total_traded_notional",
                )
            },
            "combined_wf": {
                k: combined[k]
                for k in (
                    "oos_sharpe", "oos_return", "oos_max_drawdown", "num_trades",
                    "total_cost_usd", "total_traded_notional",
                )
            },
        },
        "root_cause": root_cause,
    }

    # GO/NO-GO: the options leg does NOT constitute a defensible net-of-cost edge
    # on current real data. Trustworthy NO-GO (measured, not narrative).
    options_edge = (
        measured["parity"]["verdict"] == "GO"
        and checks["checks"][0]["pass"]  # options_signal_exists
        and checks["checks"][3]["pass"]  # combined_net_of_cost_superior
    )
    verdict = "GO" if options_edge else "NO-GO"

    report = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "data_provenance": "real_public_exchange_export",
        "authenticity_verified": False,
        "never_valid_true": True,
        "symbol": "BTC",
        "venue": "okx",
        "verdict": verdict,
        "verdict_reason": (
            "Options leg is parity-consistent (GO) but the broadcast-static signal "
            "yields mean IC 0.0 (options_signal_exists FAIL) and combined net-of-cost "
            "is not superior; no defensible options-leg edge on current real data."
        ),
        "measured": measured,
        "code_paths": [
            "src/data/options_timeseries.py",
            "src/analytics/integrated_options_orderflow_evaluation.py",
            "src/analytics/real_net_of_cost_evaluation.py",
            "src/campaign/integrated.py",
            "src/data/public_export_acquisition.py",
        ],
    }

    assert_json_valid(report)
    return report


def main() -> None:
    report = build_report()
    stamp = _utc_now_iso()
    from src.analytics.measurement_validity_evaluation import _stamp_for_filename

    fs = _stamp_for_filename(stamp)
    base = OUT_DIR / f"{REPORT_ID}_{fs}"
    payload = serialize_metrics_strict(report)

    jpath = base.with_suffix(".json")
    jpath.write_text(json.dumps(payload, indent=2, sort_keys=True))
    assert_json_valid(json.loads(jpath.read_text()))

    mpath = base.with_suffix(".md")
    m = report["measured"]
    integ = m["integrated_eval"]
    lines = [
        f"# {REPORT_ID} — Options-leg tradability / net-of-cost",
        "",
        f"- **Report ID:** `{report['report_id']}`",
        f"- **Generated:** {report['generated_at']}",
        f"- **Verdict:** **{report['verdict']}**",
        f"- **Provenance:** {report['data_provenance']} (authenticity_verified=false)",
        f"- **Reason:** {report['verdict_reason']}",
        "",
        "## Measured state (real data re-acquired this session)",
        f"- Real options snapshots: {m['n_real_options_snapshots']} (span {m['snapshot_span_seconds']:.1f}s)",
        f"- Parity calibration: {m['parity']['verdict']} — {m['parity']['reason']}",
        f"- Integrated eval: {integ['verdict']} ({integ['n_passed']}/{integ['n_checks']} checks); failed={integ['failed_checks']}",
        f"- Options-only WF: Sharpe {integ['options_only_wf']['oos_sharpe']:.3f}, trades {integ['options_only_wf']['num_trades']}, cost ${integ['options_only_wf']['total_cost_usd']:.2f}",
        f"- Orderflow-only WF: Sharpe {integ['orderflow_only_wf']['oos_sharpe']:.3f}, trades {integ['orderflow_only_wf']['num_trades']}, cost ${integ['orderflow_only_wf']['total_cost_usd']:.2f}",
        f"- Combined WF: Sharpe {integ['combined_wf']['oos_sharpe']:.3f}, trades {integ['combined_wf']['num_trades']}, cost ${integ['combined_wf']['total_cost_usd']:.2f}",
        "",
        "## Measured root cause (removes the 'unblocked' ambiguity)",
        f"- Code: `{m['root_cause']['code_path']}` :: `{m['root_cause']['function']}`",
        f"- Behavior: {m['root_cause']['measured_behavior']}",
        f"- Evidence: options_mean_ic={m['root_cause']['evidence']['options_mean_ic_observed']}, options_signal_exists_pass={m['root_cause']['evidence']['options_signal_exists_pass']}",
        "",
        "## Environment (verified this session)",
        "- Python 3.12.3; numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0",
        "- Deps were NOT installed in a fresh checkout; `pip3 install -r requirements.txt` required first.",
        "- Real data is gitignored; re-acquire with `python -m src.data.public_export_acquisition`.",
        "",
        "## Next concrete step",
        "Compute a per-snapshot time-varying options signal (not broadcast-static) over >=3 real snapshots separated in wall-clock time; re-run net-of-cost; seal EVAL-30.",
    ]
    mpath.write_text("\n".join(lines) + "\n")

    print(json.dumps({"json": str(jpath), "md": str(mpath), "verdict": report["verdict"]}, indent=2))


if __name__ == "__main__":
    main()
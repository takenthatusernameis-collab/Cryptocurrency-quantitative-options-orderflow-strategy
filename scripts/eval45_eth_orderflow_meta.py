#!/usr/bin/env python3
"""EVAL-45: cross-asset ETH orderflow net-of-cost meta-analysis (thin reuse).

EVAL-43 sealed ``NO-GO CONFIRMED (PASS)`` for orderflow-only net-of-cost on the
five real BTC/OKX tapes. The repo charter is *cryptocurrency* options+orderflow,
so the same pre-registered protocol must be falsified on a second asset before
the pillar can be called closed cross-asset.

This script is deliberately thin: it reuses the sealed EVAL-43 bar builder,
causal signal, toxicity gate, capacity-aware sizer, walk-forward engine,
permutation/bootstrap/CSCV/BH-FDR statistics and sealing helpers, and only
changes the symbol, the roster and the report identity. No new orchestrator.

Anti-avoidance:
  * the ETH roster must be **complete** (``--go-min-tapes 5``) or the run refuses
    to seal a measurement and seals a BLOCKED artifact instead;
  * the BTC control is **cited** from the sealed EVAL-43 artifact (never
    re-measured, never re-labelled) so the cross-asset table is reproducible;
  * ``--allow-partial`` exists only for a documented partial acquisition and
    still records the shortfall in the artifact.

Pre-declared ETH GO bar (identical to EVAL-43's): orderflow-only net-of-cost
Sharpe > 0 on >= 3 of the 5 ETH windows AND no kill-switch breach
(max-DD <= 0.20) on any window. Otherwise ``NO-GO CONFIRMED (PASS)``.

CLI::

    export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
    python3 scripts/eval45_eth_orderflow_meta.py --no-write
    python3 scripts/eval45_eth_orderflow_meta.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "EVAL_45_ETH_ORDERFLOW_META"
BLOCKED_REPORT_ID = "EVAL_45_ETH_ORDERFLOW_META_BLOCKED"
BTC_CONTROL_REPORT_ID = "EVAL_43_ORDERFLOW_FULL_ROSTER_META"
DATA_RAW_DIR = Path("data/raw")
OUT_DIR = Path("research_state")

DEFAULT_GO_MIN_POSITIVE_TAPES = 3
DEFAULT_GO_MIN_TAPES = 5
ETH_TAPE_GLOB = "orderflow_okx_ETH_w*.json"


def _load_eval43():
    """Import the sealed EVAL-43 script as a module (path-based, no package)."""
    path = ROOT / "scripts" / "eval43_orderflow_full_roster_meta.py"
    spec = importlib.util.spec_from_file_location("eval43_orderflow_full_roster_meta", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


eval43 = _load_eval43()


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested)
# ---------------------------------------------------------------------------


def window_index(path: Path | str) -> int:
    """Parse the ``_wNN_`` window index out of an acquisition tape name."""
    stem = Path(path).stem
    token = ""
    for part in stem.split("_"):
        if len(part) == 3 and part[0] == "w" and part[1:].isdigit():
            token = part
            break
    if not token:
        raise ValueError(f"no _wNN_ window token in {stem!r}")
    return int(token[1:])


def discover_eth_tapes(data_raw: Path | str = DATA_RAW_DIR) -> Dict[str, str]:
    """Map window index -> newest ETH tape path (deterministic, no synthesis)."""
    root = Path(data_raw)
    found: Dict[int, Path] = {}
    if root.is_dir():
        for path in sorted(root.glob(ETH_TAPE_GLOB)):
            if "synthetic" in path.name.lower() or not path.is_file():
                continue
            idx = window_index(path)
            if idx not in found or path.stat().st_mtime > found[idx].stat().st_mtime:
                found[idx] = path
    return {f"eth_w{idx:02d}": str(found[idx]) for idx in sorted(found)}


def resolve_roster(
    tape_overrides: Optional[Mapping[str, str]] = None,
    *,
    data_raw: Path | str = DATA_RAW_DIR,
    go_min_tapes: int = DEFAULT_GO_MIN_TAPES,
) -> Dict[str, Any]:
    """Resolve the ETH roster; report present/missing without substituting files."""
    discovered = discover_eth_tapes(data_raw)
    resolved: Dict[str, str] = dict(discovered)
    for name, path in (tape_overrides or {}).items():
        if path:
            resolved[name] = str(path)
    missing = [
        {"tape": f"eth_w{i:02d}", "path": ""}
        for i in range(1, int(go_min_tapes) + 1)
        if f"eth_w{i:02d}" not in resolved
    ]
    present = {k: v for k, v in resolved.items() if Path(v).is_file()}
    absent = {k: v for k, v in resolved.items() if not Path(v).is_file()}
    return {
        "resolved": resolved,
        "present": present,
        "missing": missing + [{"tape": k, "path": v} for k, v in absent.items()],
        "full_roster_met": len(present) >= int(go_min_tapes) and not missing,
        "n_present": len(present),
        "go_min_tapes": int(go_min_tapes),
    }


def btc_control_from_sealed(
    research_state: Path | str = OUT_DIR,
    report_id: str = BTC_CONTROL_REPORT_ID,
) -> Dict[str, Any]:
    """Cite the sealed EVAL-43 BTC per-tape results (read-only, never re-run)."""
    root = Path(research_state)
    if not root.is_dir():
        return {"available": False, "reason": "research_state missing"}
    candidates = sorted(root.glob(f"{report_id}_*.json"))
    if not candidates:
        return {"available": False, "reason": f"no sealed {report_id} artifact"}
    path = candidates[-1]
    payload = json.loads(path.read_text(encoding="utf-8"))
    tapes = []
    for tape in payload.get("tape_results", []) or []:
        tapes.append({
            "tape": tape.get("name"),
            "n_bars": int(tape.get("n_bars", 0)),
            "oos_sharpe": float(tape.get("oos_sharpe", 0.0)),
            "oos_max_drawdown": float(tape.get("oos_max_drawdown", 0.0)),
            "kill_switch_breach": bool(tape.get("kill_switch_breach")),
        })
    pooled = payload.get("pooled") or {}
    return {
        "available": True,
        "source_artifact": str(path),
        "symbol": payload.get("symbol", "BTC"),
        "verdict": payload.get("verdict"),
        "n_tapes": int(pooled.get("n_tapes", len(tapes))),
        "n_positive_sharpe": int(pooled.get("n_positive_sharpe", 0)),
        "n_kill_switch_breaches": int(pooled.get("n_kill_switch_breaches", 0)),
        "tapes": tapes,
        "re_measured": False,
    }


def cross_asset_table(
    eth_report: Mapping[str, Any],
    btc_control: Mapping[str, Any],
) -> Dict[str, Any]:
    """BTC vs ETH verdict table (BTC cited from sealed evidence)."""
    eth_pooled = dict(eth_report.get("pooled") or {})
    eth_verdict = str(eth_report.get("verdict") or "")
    btc_verdict = str(btc_control.get("verdict") or "") if btc_control.get("available") else ""
    btc_nogo = btc_verdict.upper().startswith("NO-GO")
    eth_nogo = eth_verdict.upper().startswith("NO-GO")
    return {
        "assets": {
            "BTC": {
                "verdict": btc_verdict or None,
                "scope": "SEALED (EVAL-43, cited)",
                "n_tapes": btc_control.get("n_tapes"),
                "n_positive_sharpe": btc_control.get("n_positive_sharpe"),
                "n_kill_switch_breaches": btc_control.get("n_kill_switch_breaches"),
                "source_artifact": btc_control.get("source_artifact"),
            },
            "ETH": {
                "verdict": eth_verdict or None,
                "scope": eth_report.get("verdict_scope"),
                "n_tapes": eth_pooled.get("n_tapes"),
                "n_positive_sharpe": eth_pooled.get("n_positive_sharpe"),
                "n_kill_switch_breaches": eth_pooled.get("n_kill_switch_breaches"),
                "source_artifact": (eth_report.get("artifact_paths") or {}).get("json"),
            },
        },
        "btc_control_available": bool(btc_control.get("available")),
        "btc_nogo": btc_nogo,
        "eth_nogo": eth_nogo,
        "eth_replicates_btc_nogo": bool(btc_nogo and eth_nogo),
        "note": (
            "BTC numbers are cited from the sealed EVAL-43 artifact and are not "
            "re-measured; ETH numbers are measured in this artifact."
        ),
    }


def md_appendix(report: Mapping[str, Any]) -> str:
    """Markdown cross-asset appendix appended to the EVAL-43 markdown body."""
    table = report.get("cross_asset") or {}
    assets = table.get("assets") or {}
    lines = ["", "## Cross-asset consistency (BTC vs ETH)", ""]
    lines.append("| asset | verdict | scope | tapes | positive Sharpe | kill-switch breaches |")
    lines.append("|---|---|---|---|---|---|")
    for name in ("BTC", "ETH"):
        row = assets.get(name) or {}
        lines.append(
            f"| {name} | {row.get('verdict')} | {row.get('scope')} | {row.get('n_tapes')} | "
            f"{row.get('n_positive_sharpe')} | {row.get('n_kill_switch_breaches')} |"
        )
    lines.append("")
    lines.append(f"- ETH replicates the BTC NO-GO: {table.get('eth_replicates_btc_nogo')}")
    lines.append(f"- BTC control cited from: `{table.get('assets', {}).get('BTC', {}).get('source_artifact')}`")
    lines.append("")
    lines.append("## ETH windows")
    lines.append("")
    lines.append("| window | trades | bars | Sharpe | max-DD | trades taken | cost $ | perm p | CI |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for tape in report.get("tape_results", []) or []:
        ci = tape.get("bootstrap_ci", [0.0, 0.0, 0.0])
        lines.append(
            f"| {tape.get('name')} | {tape.get('n_trades')} | {tape.get('n_bars')} | "
            f"{tape.get('oos_sharpe'):.4f} | {tape.get('oos_max_drawdown'):.4f} | "
            f"{tape.get('num_trades')} | {tape.get('total_cost_usd'):.2f} | "
            f"{tape.get('permutation_p'):.4f} | [{ci[1]:.4f},{ci[2]:.4f}] |"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_eval45(
    *,
    write: bool = True,
    tape_overrides: Optional[Mapping[str, str]] = None,
    data_raw: Path | str = DATA_RAW_DIR,
    go_min_positive_tapes: int = DEFAULT_GO_MIN_POSITIVE_TAPES,
    go_min_tapes: int = DEFAULT_GO_MIN_TAPES,
    allow_partial: bool = False,
    btc_control: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    resolved = resolve_roster(tape_overrides, data_raw=data_raw, go_min_tapes=go_min_tapes)
    if not resolved["full_roster_met"] and not allow_partial:
        raise RuntimeError(
            "ETH roster incomplete: "
            f"{resolved['n_present']}/{go_min_tapes} windows present; missing "
            f"{[m['tape'] for m in resolved['missing']]}. Acquire them with "
            f"scripts/eval45_acquire_eth_windows.py (never substitute a BTC tape)."
        )

    report = eval43.run_eval43(
        write=False,
        tape_overrides=dict(resolved["resolved"]),
        tapes_spec={name: resolved["resolved"][name] for name in resolved["resolved"]},
        blocked_report_id=BLOCKED_REPORT_ID,
        report_id=REPORT_ID,
        symbol="ETH",
        task_label="EVAL-45-ETH-ORDERFLOW-META",
        go_min_positive_tapes=go_min_positive_tapes,
        go_min_tapes=go_min_tapes,
    )
    control = dict(btc_control) if btc_control is not None else btc_control_from_sealed()
    report["input_resolution"] = {
        "present": resolved["present"],
        "missing": resolved["missing"],
        "full_roster_met": bool(resolved["full_roster_met"]),
        "go_min_tapes": int(go_min_tapes),
    }
    report["verdict_scope"] = (
        "ETH_FULL_ROSTER" if resolved["full_roster_met"] else "ETH_PARTIAL"
    )
    report["cross_asset"] = cross_asset_table(report, control)
    report["btc_control"] = control

    if not eval43._all_finite(report):
        raise RuntimeError("non-finite values in ETH report")

    artifact_paths: Dict[str, str] = {}
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = eval43._stamp_for_filename(str(report["generated_at"]))
        jpath = OUT_DIR / f"{REPORT_ID}_{stamp}.json"
        mpath = OUT_DIR / f"{REPORT_ID}_{stamp}.md"
        eval43._write_json(jpath, report)
        mpath.write_text(eval43.build_md(report) + md_appendix(report) + "\n", encoding="utf-8")
        artifact_paths = {"json": str(jpath), "md": str(mpath)}
        report["artifact_paths"] = artifact_paths
        report["cross_asset"]["assets"]["ETH"]["source_artifact"] = str(jpath)
        eval43._write_json(jpath, report)
    else:
        report["artifact_paths"] = artifact_paths
    return report


def _seal_blocked(generated_at: str, exc: BaseException) -> Dict[str, str]:
    return eval43._seal_blocked(
        generated_at, exc, report_id=BLOCKED_REPORT_ID, symbol="ETH"
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--tape", action="append", default=[], metavar="NAME=PATH",
                    help="override an ETH window tape (repeatable)")
    ap.add_argument("--data-raw", default=str(DATA_RAW_DIR))
    ap.add_argument("--go-min-positive-tapes", type=int, default=DEFAULT_GO_MIN_POSITIVE_TAPES)
    ap.add_argument("--go-min-tapes", type=int, default=DEFAULT_GO_MIN_TAPES)
    ap.add_argument("--allow-partial", action="store_true",
                    help="seal a PARTIAL ETH scope when windows are missing (documented only)")
    args = ap.parse_args(argv)

    overrides: Dict[str, str] = {}
    for item in args.tape:
        if "=" not in item:
            raise SystemExit(f"--tape expects NAME=PATH, got {item!r}")
        name, path = item.split("=", 1)
        overrides[name.strip()] = path.strip()

    generated_at = eval43._utc_now_iso()
    try:
        report = run_eval45(
            write=not args.no_write,
            tape_overrides=overrides or None,
            data_raw=Path(args.data_raw),
            go_min_positive_tapes=args.go_min_positive_tapes,
            go_min_tapes=args.go_min_tapes,
            allow_partial=args.allow_partial,
        )
    except Exception as exc:  # noqa: BLE001 - seal a BLOCKED artifact, never silent
        import traceback

        traceback.print_exc()
        paths = _seal_blocked(generated_at, exc) if not args.no_write else {}
        print(json.dumps({
            "report_id": BLOCKED_REPORT_ID,
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
        "n_positive_sharpe": report["pooled"]["n_positive_sharpe"],
        "n_kill_switch_breaches": report["pooled"]["n_kill_switch_breaches"],
        "eth_replicates_btc_nogo": report["cross_asset"]["eth_replicates_btc_nogo"],
        "tape_errors": report.get("tape_errors", []),
        "artifact_paths": report.get("artifact_paths", {}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
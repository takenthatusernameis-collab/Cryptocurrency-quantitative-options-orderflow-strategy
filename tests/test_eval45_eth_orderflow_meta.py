"""Focused unit tests for the EVAL-45 ETH orderflow meta-analysis helpers.

Only pure helpers are covered: ETH tape discovery/roster resolution, sealed BTC
control citation and the cross-asset table. The walk-forward meta-analysis is
exercised by the script itself (it reuses the sealed EVAL-43 engine).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_MODULE_PATH = ROOT / "scripts" / "eval45_eth_orderflow_meta.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("eval45_eth_orderflow_meta", _MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def test_window_index_parses_acquisition_names() -> None:
    assert mod.window_index("data/raw/orderflow_okx_ETH_w03_507848531.json") == 3
    assert mod.window_index(Path("x/orderflow_okx_ETH_w12_1.json")) == 12
    try:
        mod.window_index("orderflow_okx_BTC-USD-SWAP.json")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for a non-window tape")


def test_discover_eth_tapes_is_sorted_and_ignores_btc(tmp_path: Path) -> None:
    (tmp_path / "orderflow_okx_ETH_w02_200.json").write_text("{}")
    (tmp_path / "orderflow_okx_ETH_w01_100.json").write_text("{}")
    (tmp_path / "orderflow_okx_ETH_synthetic_w09_1.json").write_text("{}")
    (tmp_path / "orderflow_okx_BTC-USD-SWAP.json").write_text("{}")
    found = mod.discover_eth_tapes(tmp_path)
    assert list(found) == ["eth_w01", "eth_w02"]
    assert found["eth_w01"].endswith("orderflow_okx_ETH_w01_100.json")


def test_resolve_roster_reports_missing_without_substituting(tmp_path: Path) -> None:
    (tmp_path / "orderflow_okx_ETH_w01_100.json").write_text("{}")
    resolved = mod.resolve_roster(data_raw=tmp_path, go_min_tapes=3)
    assert resolved["n_present"] == 1
    assert resolved["full_roster_met"] is False
    assert [m["tape"] for m in resolved["missing"]] == ["eth_w02", "eth_w03"]


def test_resolve_roster_full_and_override(tmp_path: Path) -> None:
    paths = {}
    for i in range(1, 6):
        path = tmp_path / f"orderflow_okx_ETH_w{i:02d}_{i}.json"
        path.write_text("{}")
        paths[f"eth_w{i:02d}"] = str(path)
    resolved = mod.resolve_roster(paths, data_raw=tmp_path, go_min_tapes=5)
    assert resolved["full_roster_met"] is True
    assert resolved["missing"] == []

    overridden = mod.resolve_roster(
        {"eth_w01": str(tmp_path / "missing.json")}, data_raw=tmp_path, go_min_tapes=5
    )
    assert overridden["full_roster_met"] is False
    assert overridden["missing"][0]["tape"] == "eth_w01"


def _sealed_btc_artifact(tmp_path: Path) -> Path:
    payload = {
        "verdict": "NO-GO CONFIRMED (PASS)",
        "symbol": "BTC",
        "pooled": {"n_tapes": 5, "n_positive_sharpe": 1, "n_kill_switch_breaches": 5},
        "tape_results": [
            {"name": "41a", "n_bars": 1553, "oos_sharpe": 0.2387,
             "oos_max_drawdown": 0.4414, "kill_switch_breach": True},
            {"name": "41b", "n_bars": 1555, "oos_sharpe": -8.7851,
             "oos_max_drawdown": 0.9492, "kill_switch_breach": True},
        ],
    }
    path = tmp_path / "EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z.json"
    path.write_text(json.dumps(payload))
    return path


def test_btc_control_cites_sealed_artifact_without_rerun(tmp_path: Path) -> None:
    path = _sealed_btc_artifact(tmp_path)
    control = mod.btc_control_from_sealed(tmp_path)
    assert control["available"] is True
    assert control["source_artifact"] == str(path)
    assert control["verdict"] == "NO-GO CONFIRMED (PASS)"
    assert control["n_kill_switch_breaches"] == 5
    assert control["re_measured"] is False
    assert control["tapes"][0]["tape"] == "41a"


def test_btc_control_reports_unavailable(tmp_path: Path) -> None:
    control = mod.btc_control_from_sealed(tmp_path)
    assert control["available"] is False
    table = mod.cross_asset_table({"verdict": "NO-GO CONFIRMED (PASS)", "pooled": {}}, control)
    assert table["eth_replicates_btc_nogo"] is False
    assert table["assets"]["BTC"]["verdict"] is None


def test_cross_asset_table_flags_replication() -> None:
    eth = {
        "verdict": "NO-GO CONFIRMED (PASS)",
        "verdict_scope": "ETH_FULL_ROSTER",
        "pooled": {"n_tapes": 5, "n_positive_sharpe": 1, "n_kill_switch_breaches": 5},
        "artifact_paths": {"json": "research_state/EVAL_45_ETH_ORDERFLOW_META_x.json"},
    }
    control = {"available": True, "verdict": "NO-GO CONFIRMED (PASS)",
               "n_tapes": 5, "n_positive_sharpe": 1, "n_kill_switch_breaches": 5,
               "source_artifact": "research_state/EVAL_43_ORDERFLOW_FULL_ROSTER_META_x.json"}
    table = mod.cross_asset_table(eth, control)
    assert table["eth_replicates_btc_nogo"] is True
    assert table["assets"]["ETH"]["scope"] == "ETH_FULL_ROSTER"
    assert table["assets"]["ETH"]["source_artifact"].endswith(".json")
    assert "BTC" in mod.md_appendix({"cross_asset": table, "tape_results": []})


def test_cross_asset_table_detects_divergence() -> None:
    eth = {"verdict": "FALSIFIED", "pooled": {"n_tapes": 5, "n_positive_sharpe": 4,
                                              "n_kill_switch_breaches": 0}}
    control = {"available": True, "verdict": "NO-GO CONFIRMED (PASS)",
               "n_tapes": 5, "n_positive_sharpe": 1, "n_kill_switch_breaches": 5}
    table = mod.cross_asset_table(eth, control)
    assert table["eth_nogo"] is False
    assert table["eth_replicates_btc_nogo"] is False
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import scripts.generate_phase126_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence as gen


def test_generate_phase126_valid_advisory_shape() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=12, seed=126126, write=False)
    ok, issues = gen.validate_artifact(d)
    assert ok, issues
    assert d["artifact_type"].endswith("_PAPER_EVIDENCE")
    assert d["paper_only"] is True
    assert d["advisory"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["no_external_venue_mutation"] is True


def test_generate_phase126_rejects_live_true() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=8, seed=126126, write=False)
    bad = dict(d)
    bad["live_trading_enabled"] = True
    ok, issues = gen.validate_artifact(bad)
    assert ok is False
    assert "must_not_enable_live_trading" in issues


def test_generate_phase126_rejects_next9_true() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=8, seed=126126, write=False)
    bad = dict(d)
    bad["next9_unblocked"] = True
    ok, issues = gen.validate_artifact(bad)
    assert ok is False
    assert "must_not_unblock_next9" in issues


def test_generate_phase126_rejects_paper_false() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=8, seed=126126, write=False)
    bad = dict(d)
    bad["paper_only"] = False
    ok, issues = gen.validate_artifact(bad)
    assert ok is False


def test_generate_phase126_rejects_advisory_false() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=8, seed=126126, write=False)
    bad = dict(d)
    bad["advisory"] = False
    ok, issues = gen.validate_artifact(bad)
    assert ok is False


def test_generate_phase126_rejects_external_mutation_false_required() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=8, seed=126126, write=False)
    bad = dict(d)
    bad["no_external_venue_mutation"] = False
    ok, issues = gen.validate_artifact(bad)
    assert ok is False
    assert "no_external_venue_mutation_required" in issues


def test_generate_phase126_deterministic_seed_reproducibility() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d1 = gen.generate(cycles=16, seed=126126, write=False)
    d2 = gen.generate(cycles=16, seed=126126, write=False)
    assert d1["determinism"]["same_seed_cycles_reproduce_surface"] is True
    assert d1["determinism"]["bounds_ok"] is True

    def strip(obj):
        if isinstance(obj, dict):
            return {k: strip(v) for k, v in obj.items() if k not in ("timestamp_utc", "timestamp")}
        if isinstance(obj, list):
            return [strip(v) for v in obj]
        return obj

    assert strip(d1) == strip(d2)


def test_generate_phase126_12_coverage_and_bounds_and_composes() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    d = gen.generate(cycles=20, seed=126126, write=False)
    assert len(d["venue_symbol_coverage"]) == 4 * 3  # 12
    assert all(r["paper_only"] for r in d["venue_symbol_coverage"])
    assert all(r["probe_gates_ok"] for r in d["venue_symbol_coverage"])
    assert all(r["probe_finite"] for r in d["venue_symbol_coverage"])
    assert all(r["probe_bounds_within_limits"] for r in d["venue_symbol_coverage"])
    assert d["seal_surface"]["bounds_ok"] is True
    assert d["seal_surface"]["deterministic_replay_equal"] is True
    assert d["campaign"]["gates_ok"] is True
    assert "PHASE125" in d["campaign"]["composes"]
    assert "PHASE32" in d["campaign"]["composes"]
    assert d["risk_posture"]["paper_only"] is True
    assert d["risk_posture"]["next9_unblocked"] is False
    assert d["risk_posture"]["live_trading_enabled"] is False


def test_generate_phase126_cli_no_write_deterministic() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    repo = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        "scripts/generate_phase126_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py",
        "--cycles",
        "4",
        "--seed",
        "126126",
        "--no-write",
    ]
    res = subprocess.run(cmd, cwd=repo, env=os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    assert res.returncode == 0
    out = json.loads(res.stdout)
    assert out["valid"] is True
    assert out["issues"] == []
    assert out["paper_only"] is True
    assert out["live_trading_enabled"] is False
    assert out["next9_unblocked"] is False
    assert out["deterministic"] is True
    assert out["gates_ok"] is True
    assert out["artifact_path"] is None

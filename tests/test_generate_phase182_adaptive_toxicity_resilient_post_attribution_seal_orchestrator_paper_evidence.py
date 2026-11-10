from __future__ import annotations

import json
import os
import sys

import scripts.generate_phase182_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence as gen
from scripts.generate_phase182_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence import (
    generate,
    validate_artifact,
)


def test_generate_phase182_valid_advisory_shape() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        ok, issues = validate_artifact(d)
        assert ok, issues
        assert d["paper_only"] is True
        assert d["advisory"] is True
        assert d["next9_unblocked"] is False
        assert d["live_trading_enabled"] is False
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_rejects_live_true() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        d["live_trading_enabled"] = True
        ok, issues = validate_artifact(d)
        assert not ok and "must_not_enable_live_trading" in issues
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_rejects_next9_true() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        d["next9_unblocked"] = True
        ok, issues = validate_artifact(d)
        assert not ok and "must_not_unblock_next9" in issues
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_rejects_paper_false() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        d["paper_only"] = False
        ok, _ = validate_artifact(d)
        assert not ok
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_rejects_advisory_false() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        d["advisory"] = False
        ok, _ = validate_artifact(d)
        assert not ok
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_rejects_external_mutation_false_required() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        d["no_external_venue_mutation"] = False
        ok, issues = validate_artifact(d)
        assert not ok and "no_external_venue_mutation_required" in issues
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_deterministic_seed_reproducibility() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        a = generate(cycles=30, seed=182182, write=False)
        b = generate(cycles=30, seed=182182, write=False)
        for k in ("campaign", "seal_surface", "venue_symbol_coverage", "determinism"):
            assert a[k] == b[k]
        for r in a["venue_symbol_coverage"]:
            assert r["probe_gates_ok"] is True
            assert r["probe_finite"] is True
            assert r["probe_bounds_within_limits"] is True
        assert a["seal_surface"]["deterministic_replay_equal"] is True
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_12_coverage_and_bounds_and_composes() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        assert len(d["venue_symbol_coverage"]) == 12
        venues = {r["venue"] for r in d["venue_symbol_coverage"]}
        symbols = {r["symbol"] for r in d["venue_symbol_coverage"]}
        assert venues == {"deribit", "okx", "bybit", "binance"}
        assert symbols == {"BTC-USD", "ETH-USD", "SOL-USD"}
        assert all(r["probe_gates_ok"] for r in d["venue_symbol_coverage"])
        assert d["seal_surface"]["bounds_ok"] is True
        assert d["campaign"]["composes"] == ["PHASE181", "PHASE32"]
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_cli_no_write_deterministic() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        argv_bak = sys.argv[:]
        try:
            sys.argv = ["gen", "--cycles", "30", "--seed", "182182", "--no-write"]
            from io import StringIO
            buf = StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                gen.main()
            finally:
                sys.stdout = old
            j = json.loads(buf.getvalue())
            assert j["valid"] is True and j["deterministic"] is True and j["gates_ok"] is True
            assert j["artifact_path"] is None
        finally:
            sys.argv = argv_bak
    finally:
        gen.ORCH_CACHE.clear()


def test_generate_phase182_cross_refs_and_composes() -> None:
    os.environ["PHASE_QUICK_VERIFY"] = "1"
    try:
        d = generate(cycles=30, seed=182182, write=False)
        refs = d["cross_refs"]
        assert "Phase182AdaptiveToxicityResilientPostAttributionSealOrchestrator" in refs
        assert "Phase181AdaptiveToxicityResilientPostAttributionSealOrchestrator" in refs
        assert "Phase180AdaptiveToxicityResilientPostAttributionSealOrchestrator" in refs
        assert "Phase179AdaptiveToxicityResilientPostAttributionSealOrchestrator" in refs
        assert "Phase32OrderflowAlphaIntegration" in refs
        assert "composes=PHASE181,PHASE32" in refs
        ev = " ".join(d["evidence_refs"])
        assert "PAPER_OPS_SESSION_GATE" in ev
        assert "CONTINUOUS_VALIDATION" in ev
        assert "PHASE181_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261110T133711Z.json" in ev
    finally:
        gen.ORCH_CACHE.clear()

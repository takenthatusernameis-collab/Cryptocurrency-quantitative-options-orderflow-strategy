import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_no_write():
    r = subprocess.run([sys.executable, str(REPO / "scripts/generate_phase60_adaptive_execution_intelligence_engine_paper_evidence.py"), "--no-write"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["valid"] is True
    assert out["deterministic"] is True
    assert out["paper_only"] is True


def test_write():
    r = subprocess.run([sys.executable, str(REPO / "scripts/generate_phase60_adaptive_execution_intelligence_engine_paper_evidence.py"), "--write"],
                       cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    p = Path(out["path"])
    assert p.exists()
    d = json.loads(p.read_text())
    assert d["paper_only"] is True
    assert d["live_trading_enabled"] is False
    assert d["next9_unblocked"] is False
    assert d["no_external_venue_mutation"] is True
    assert d["advisory"] is True
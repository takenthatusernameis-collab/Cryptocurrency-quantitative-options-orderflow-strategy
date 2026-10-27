"""Tests for scripts/controller_progress.py change-detection accounting."""

import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = PROJECT_ROOT / "scripts" / "controller_progress.py"


def _init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, capture_output=True, check=True)


def _commit_file(repo: Path, name: str, content: str, message: str) -> str:
    target = repo / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    subprocess.run(["git", "add", name], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, capture_output=True, check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def _run_controller(repo: Path, base: str, head: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(CONTROLLER), "--base-sha", base, "--head-sha", head],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def test_detects_project_changes_returns_zero(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    _commit_file(repo, "a.txt", "1\n", "init")
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    _commit_file(repo, "src/strategy.py", "print('x')\n", "add strategy")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    result = _run_controller(repo, base, head)
    assert result.returncode == 0


def test_no_project_changes_returns_nonzero(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    _commit_file(repo, "a.txt", "1\n", "init")
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    (repo / ".github" / "workflows").mkdir(parents=True)
    _commit_file(repo, ".github/workflows/main.yml", "name: ci\n", "workflow only")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    result = _run_controller(repo, base, head)
    assert result.returncode == 1


def test_identical_shas_returns_nonzero(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    _commit_file(repo, "a.txt", "1\n", "init")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    result = _run_controller(repo, sha, sha)
    assert result.returncode == 1

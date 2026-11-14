#!/usr/bin/env bash
# verify_env.sh — reproducible verification runtime for this repository.
#
# The checkout ships no third-party packages (no pandas/numpy/scipy/pytest), so a
# fresh agent session cannot run the sealed EVAL checks or the test suite until
# the runtime is bootstrapped. This script does that deterministically into a
# local, git-ignored directory and then runs the checks that matter.
#
# Usage:
#   ./scripts/verify_env.sh            # bootstrap deps (if needed) + run checks
#   ./scripts/verify_env.sh --check    # use existing deps; fail if missing
#
# It never installs into the system Python, never writes .env, and never enables
# live trading.

set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DEPS_DIR="${DEPS_DIR:-$ROOT/.venv-deps}"
CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

PY="${PYTHON:-python3}"

bootstrap() {
  if [ "$CHECK_ONLY" -eq 1 ]; then
    echo "[verify_env] --check set and deps missing; aborting" >&2
    exit 2
  fi
  echo "[verify_env] bootstrapping runtime deps into $DEPS_DIR" >&2
  "$PY" -m pip install --disable-pip-version-check --no-input \
    --target "$DEPS_DIR" -r requirements.txt >/dev/null
}

if [ ! -d "$DEPS_DIR" ] || [ -z "$(ls -A "$DEPS_DIR" 2>/dev/null)" ]; then
  bootstrap
else
  echo "[verify_env] reusing deps in $DEPS_DIR" >&2
fi

export PYTHONPATH="$DEPS_DIR${PYTHONPATH:+:$PYTHONPATH}"

echo "[verify_env] python: $("$PY" --version 2>&1)"
"$PY" - <<'PY'
import importlib
for m in ("pytest", "numpy", "pandas", "scipy", "pydantic", "yaml", "requests"):
    try:
        importlib.import_module(m)
        print(f"[verify_env]   {m}: ok")
    except Exception as e:  # noqa: BLE001
        print(f"[verify_env]   {m}: MISSING ({e})")
        raise SystemExit(1)
PY

echo "[verify_env] py_compile sealed EVAL scripts/tests"
"$PY" -m py_compile \
  scripts/eval37_final_termination_audit.py \
  tests/test_eval37_final_termination_audit.py

echo "[verify_env] pytest: EVAL-37 termination audit"
"$PY" -m pytest -q tests/test_eval37_final_termination_audit.py

echo "[verify_env] pytest: EVAL-36 termination memo"
"$PY" -m pytest -q tests/test_eval36_final_termination_memo.py

echo "[verify_env] OK"
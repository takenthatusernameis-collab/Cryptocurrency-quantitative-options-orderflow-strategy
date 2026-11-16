#!/usr/bin/env bash
# EVAL-67 disjoint BTC capture launcher (paper-only, real public read-only network).
#
# Enforces the pre-registered disjointness rule BEFORE acquiring:
#   window = [now - 3.7d, now]; start must be >= sealed end 2026-11-16T06:48:16Z
#   and span (319680 s) must be >= the EVAL-64 perp-span floor (300000 s).
# That requires real UTC now >= 2026-11-20T00:00:00Z (the pre-registered threshold).
# A naive trailing --days 7 capture before the sealed window has cleared is refused.
#
# Usage (persistent background process, only at/after the threshold):
#   chmod +x scripts/eval67_launch_capture.sh
#   PYTHONUNBUFFERED=1 scripts/eval67_launch_capture.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THRESHOLD_ISO="2026-11-20T00:00:00Z"
THRESHOLD_EPOCH="$(date -u -d "$THRESHOLD_ISO" +%s 2>/dev/null || date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$THRESHOLD_ISO" +%s)"
NOW_EPOCH="$(date -u +%s)"
NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [ "${NOW_EPOCH}" -lt "${THRESHOLD_EPOCH}" ]; then
    echo "ERROR: now ${NOW_ISO} is before the disjointness threshold ${THRESHOLD_ISO};" >&2
    echo "       do NOT run the EVAL-67 capture yet (it would overlap the sealed BTC window" >&2
    echo "       2026-11-09T06:48:16Z..2026-11-16T06:48:16Z and must seal BLOCKED)." >&2
    exit 1
fi

echo "EVAL-67 capture: now=${NOW_ISO} >= threshold=${THRESHOLD_ISO} (disjoint OK)"
echo "window = [now-3.7d, now] = [$(date -u -d "@$((NOW_EPOCH - 319680))" +%Y-%m-%dT%H:%M:%SZ), ${NOW_ISO}]"

mkdir -p "${ROOT}/data/raw/eval67"
cd "${ROOT}"
export PYTHONPATH="${ROOT}/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"

exec python3 scripts/eval60_acquire_three_way.py \
    --underlying BTC \
    --days 3.7 \
    --end "${NOW_ISO}" \
    --out-dir data/raw/eval67 \
    --seal
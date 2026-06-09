#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${APP_ROOT}"

python3 scripts/check_config.py --skip-runtime-deps

python3 - <<'PY'
import sys
if sys.version_info < (3, 9):
    raise SystemExit("Python >= 3.9 is required for the local annotation app")
PY

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

cd frontend
npm install
npm run build

cd "${APP_ROOT}"
python scripts/check_config.py --require-runtime-deps

echo
echo "Local setup complete."
echo "Run: ./scripts/run_local.sh"

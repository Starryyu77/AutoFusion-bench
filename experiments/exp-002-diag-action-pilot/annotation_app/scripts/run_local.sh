#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${APP_ROOT}"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export AUTOFUSION_REPO_ROOT="${AUTOFUSION_REPO_ROOT:-$(cd ../../.. && pwd)}"
export ANNOTATION_DB_PATH="${ANNOTATION_DB_PATH:-${APP_ROOT}/state/annotations.sqlite}"
export PYTHONPATH="${APP_ROOT}/backend${PYTHONPATH:+:${PYTHONPATH}}"

HOST="${ANNOTATION_HOST:-127.0.0.1}"
PORT="${ANNOTATION_PORT:-8000}"

if [[ ! -x .venv/bin/uvicorn ]]; then
  echo "Missing .venv/bin/uvicorn. Run ./scripts/bootstrap_local.sh first." >&2
  exit 1
fi

exec .venv/bin/uvicorn app.main:app \
  --host "${HOST}" \
  --port "${PORT}" \
  --app-dir "${APP_ROOT}/backend"


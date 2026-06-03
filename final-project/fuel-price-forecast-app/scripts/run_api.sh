#!/usr/bin/env bash
# macOS: avoid gunicorn worker crash after numpy/xgboost (objc fork safety)
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)"

exec .venv/bin/gunicorn \
  --workers 1 \
  --threads 2 \
  --timeout 300 \
  -b 127.0.0.1:8080 \
  api.app:app

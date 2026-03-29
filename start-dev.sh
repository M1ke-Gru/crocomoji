#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/crocomoji-backend"
FRONTEND_DIR="$ROOT_DIR/crocomoji-frontend"

if [[ ! -d "$BACKEND_DIR" ]]; then
  echo "Backend directory not found: $BACKEND_DIR" >&2
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR" ]]; then
  echo "Frontend directory not found: $FRONTEND_DIR" >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but not found in PATH." >&2
  exit 1
fi

if [[ ! -x "$FRONTEND_DIR/node_modules/.bin/vite" ]]; then
  echo "Frontend dependencies not found. Installing with npm install ..."
  (
    cd "$FRONTEND_DIR"
    npm install
  )
fi

if command -v uv >/dev/null 2>&1; then
  BACKEND_CMD=(uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000)
elif [[ -x "$BACKEND_DIR/.venv/bin/uvicorn" ]]; then
  BACKEND_CMD=("$BACKEND_DIR/.venv/bin/uvicorn" main:app --reload --host 0.0.0.0 --port 8000)
else
  echo "Could not find backend runner. Install 'uv' or create backend .venv with uvicorn." >&2
  exit 1
fi

cleanup() {
  local exit_code=$?

  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi

  if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi

  wait 2>/dev/null || true
  exit "$exit_code"
}

trap cleanup EXIT INT TERM

echo "Starting backend on http://localhost:8000 ..."
(
  cd "$BACKEND_DIR"
  "${BACKEND_CMD[@]}"
) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
(
  cd "$FRONTEND_DIR"
  npm run dev -- --host 0.0.0.0 --port 5173
) &
FRONTEND_PID=$!

echo
echo "Crocomoji dev stack is running."
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "Press Ctrl+C to stop both."

wait -n "$BACKEND_PID" "$FRONTEND_PID"

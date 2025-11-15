#!/bin/bash
set -e

PORT=${PORT:-8000}

echo "Starting FastAPI application on port $PORT..."

exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

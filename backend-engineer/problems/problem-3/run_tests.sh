#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- Installing/updating test dependencies ---"
pip install -U --quiet \
  pytest \
  pytest-cov \
  pytest-asyncio \
  httpx \
  fakeredis \
  aiosqlite \
  "pydantic-settings" \
  "redis>=4.2.0" \
  "fastapi"

echo ""
echo "--- Running tests with coverage ---"

python -m pytest tests/ \
  --cov=app \
  --cov-report=term-missing \
  -s \
  -v

echo ""
echo "--- Test run complete ---"
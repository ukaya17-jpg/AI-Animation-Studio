#!/usr/bin/env bash
# Runs ruff, mypy --strict, and pytest with the same effective Settings that
# CI sees (a fresh checkout with no .env file), even though a real .env
# usually sits at the repo root during local development.
#
# Why this exists: `Settings.model_config` (app/core/config.py) always reads
# `../.env` if present. That's correct for a real local `uvicorn` run, but it
# means running `pytest` directly picks up whatever's in the local .env
# (typically a rotated DATABASE_URL/APP_SECRET_KEY, DEBUG=true, and a
# TRUSTED_HOSTS without "testserver") instead of the class defaults CI uses.
# That mismatch used to fail most of the suite locally (host-header
# rejection from TrustedHostMiddleware) with no obvious cause. Environment
# variables always take precedence over the .env file, so exporting the
# same values as Settings' class defaults here reproduces CI exactly,
# without touching or renaming your local .env.
#
# Usage: backend/scripts/test-like-ci.sh [pytest args...]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

export TRUSTED_HOSTS="localhost,127.0.0.1,testserver,backend"
export DEBUG=false
export DATABASE_URL="postgresql+asyncpg://app_user:change-me@localhost:5432/ai_animation_studio"
export APP_SECRET_KEY="development-only-secret-change-me"

.venv/bin/python -m ruff check .
.venv/bin/python -m mypy --strict app
.venv/bin/python -m pytest "$@"

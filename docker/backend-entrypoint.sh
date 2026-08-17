#!/bin/sh
# Apply pending Alembic migrations, then start the API. `set -e` means a
# failed migration stops the script (and the container exits non-zero)
# instead of silently starting an API against a stale/broken schema.
set -eu

echo "Applying database migrations..."
python -m alembic upgrade head

echo "Migrations applied. Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

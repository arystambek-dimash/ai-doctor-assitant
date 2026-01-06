#!/bin/sh
set -e

alembic upgrade head

echo "Starting: $@"
exec "$@"

uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
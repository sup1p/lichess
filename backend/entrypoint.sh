#!/bin/sh
set -e

# Wait for Postgres to be ready using project environment
uv run python - <<'PY'
import asyncio
import os
import sys
import time

import asyncpg

url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://lichess:lichess@db:5432/lichess")
url = url.replace("postgresql+asyncpg", "postgresql")

async def check():
    for i in range(30):
        try:
            conn = await asyncpg.connect(url)
            await conn.close()
            print("Database is ready")
            return
        except Exception as exc:  # noqa: BLE001
            print(f"Waiting for database... ({i+1}/30) {exc}")
            await asyncio.sleep(1)
    sys.exit("Database not ready after 30s")

asyncio.run(check())
PY

# Apply migrations
uv run alembic upgrade head

# Start server
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

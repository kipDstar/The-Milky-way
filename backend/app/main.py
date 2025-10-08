import os
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .api.v1.router import api_router


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def apply_schema_if_needed() -> None:
    schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"
    if not schema_path.exists():
        # In dev, schema lives under /app/sql mounted by Dockerfile copy step
        schema_path = Path(__file__).parent.parent.parent / "sql" / "schema.sql"
    sql_text = schema_path.read_text(encoding="utf-8")
    with psycopg.connect(get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("ENV", "development") == "development":
        try:
            apply_schema_if_needed()
        except Exception as exc:  # pragma: no cover
            # On dev start, schema application should not crash the app; logs suffice.
            print(f"[WARN] Failed to apply schema: {exc}")
    yield


app = FastAPI(title="DDCPTS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true":
    Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/health", tags=["system"])  # simple health check
def health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")


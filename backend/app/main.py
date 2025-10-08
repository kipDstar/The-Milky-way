from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from .core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers placeholders
from .api import router as api_router  # type: ignore
app.include_router(api_router, prefix="/api/v1")

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

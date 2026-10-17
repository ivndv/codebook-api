from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import health, summarize

app = FastAPI(title="codebook-api", version="0.1.0")

# CORS: solo los orígenes de confianza.
# El front llama desde el servidor (Server Action), así que esto es defensivo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origen.strip() for origen in settings.allowed_origins.split(",") if origen.strip()
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

app.include_router(health.router)
app.include_router(summarize.router)

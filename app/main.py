from fastapi import FastAPI

app = FastAPI(title="codebook-api", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Chequeo de salud (lo usan el monitoreo y el anti-pausa)."""
    return {"status": "ok"}

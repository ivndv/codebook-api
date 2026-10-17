from fastapi import APIRouter

router = APIRouter(tags=["salud"])


@router.get("/health")
def health() -> dict[str, str]:
    """Chequeo de salud (lo usan el monitoreo y el anti-pausa)."""
    return {"status": "ok"}

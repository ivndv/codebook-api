# Fixtures compartidas: aíslan los tests de la configuración local (.env)
import pytest

from app.core.config import settings
from app.dependencies.security import limitador


@pytest.fixture(autouse=True)
def _entorno_limpio(monkeypatch):
    """Sin API key y con límites por defecto en cada test."""
    monkeypatch.setattr(settings, "codebook_api_key", "")
    monkeypatch.setattr(settings, "rate_limit_per_min", 10)
    monkeypatch.setattr(settings, "rate_limit_per_day", 100)
    limitador.limpiar()

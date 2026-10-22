# Fixtures compartidas: aíslan los tests de la configuración local (.env)
import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def _entorno_limpio(monkeypatch):
    """Sin API key en cada test."""
    monkeypatch.setattr(settings, "codebook_api_key", "")

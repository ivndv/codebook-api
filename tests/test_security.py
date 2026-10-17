from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.routers import summarize as router_summarize

client = TestClient(app)


def test_sin_api_key(monkeypatch) -> None:
    """Sin X-API-Key se rechaza con 401."""
    monkeypatch.setattr(settings, "codebook_api_key", "secreto")

    res = client.post("/summarize", json={"code": "print(1)"})

    assert res.status_code == 401


def test_api_key_incorrecta(monkeypatch) -> None:
    """Con una X-API-Key que no coincide se rechaza con 401."""
    monkeypatch.setattr(settings, "codebook_api_key", "secreto")

    res = client.post("/summarize", json={"code": "print(1)"}, headers={"X-API-Key": "otra-cosa"})

    assert res.status_code == 401


def test_api_key_correcta(monkeypatch) -> None:
    """Con la X-API-Key correcta pasa."""
    monkeypatch.setattr(settings, "codebook_api_key", "secreto")
    monkeypatch.setattr(
        router_summarize, "resumir_codigo", lambda code: ("Imprime un uno.", "python")
    )

    res = client.post("/summarize", json={"code": "print(1)"}, headers={"X-API-Key": "secreto"})

    assert res.status_code == 200


def test_rate_limit(monkeypatch) -> None:
    """Al pasarse del límite por minuto devuelve 429 con Retry-After."""
    monkeypatch.setattr(settings, "rate_limit_per_min", 2)
    monkeypatch.setattr(
        router_summarize, "resumir_codigo", lambda code: ("Imprime un uno.", "python")
    )

    assert client.post("/summarize", json={"code": "print(1)"}).status_code == 200
    assert client.post("/summarize", json={"code": "print(1)"}).status_code == 200

    res = client.post("/summarize", json={"code": "print(1)"})

    assert res.status_code == 429
    assert "Retry-After" in res.headers

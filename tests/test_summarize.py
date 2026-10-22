from fastapi.testclient import TestClient
from httpx import Request, Response
from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.main import app
from app.routers import summarize as router_summarize

client = TestClient(app)


def _error_rate_limit() -> RateLimitError:
    """Construye el error 429 que lanzaría el SDK de OpenAI."""
    request = Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = Response(429, request=request)
    return RateLimitError("Límite de Groq", response=response, body=None)


def test_summarize_ok(monkeypatch) -> None:
    """Devuelve la explicación y el lenguaje que dio la IA (mockeada)."""

    async def resumen_falso(code: str) -> tuple[str, str | None]:
        return "Suma dos números.", "python"

    monkeypatch.setattr(router_summarize, "resumir_codigo", resumen_falso)

    res = client.post("/summarize", json={"code": "def suma(a, b):\n    return a + b"})

    assert res.status_code == 200
    assert res.json() == {"explanation": "Suma dos números.", "language": "python"}


def test_summarize_codigo_largo() -> None:
    """Un código demasiado largo se rechaza sin llamar a la IA."""
    res = client.post("/summarize", json={"code": "x" * 10_001})

    assert res.status_code == 400


def test_summarize_codigo_vacio() -> None:
    """Un código vacío lo rechaza la validación."""
    res = client.post("/summarize", json={"code": ""})

    assert res.status_code == 422


def test_summarize_error_de_ia(monkeypatch) -> None:
    """Si la IA falla, se devuelve 502."""

    async def explota(code: str) -> tuple[str, str | None]:
        raise RuntimeError("boom")

    monkeypatch.setattr(router_summarize, "resumir_codigo", explota)

    res = client.post("/summarize", json={"code": "print(1)"})

    assert res.status_code == 502


def test_summarize_error_rate_limit(monkeypatch) -> None:
    """Si Groq limita, se devuelve 429."""

    async def falla(code: str) -> tuple[str, str | None]:
        raise _error_rate_limit()

    monkeypatch.setattr(router_summarize, "resumir_codigo", falla)

    res = client.post("/summarize", json={"code": "print(1)"})

    assert res.status_code == 429


def test_summarize_error_timeout(monkeypatch) -> None:
    """Si Groq tarda demasiado, se devuelve 504."""

    async def falla(code: str) -> tuple[str, str | None]:
        request = Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        raise APITimeoutError(request=request)

    monkeypatch.setattr(router_summarize, "resumir_codigo", falla)

    res = client.post("/summarize", json={"code": "print(1)"})

    assert res.status_code == 504


def test_summarize_error_conexion(monkeypatch) -> None:
    """Si no hay conexión con Groq, se devuelve 503."""

    async def falla(code: str) -> tuple[str, str | None]:
        request = Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        raise APIConnectionError(request=request)

    monkeypatch.setattr(router_summarize, "resumir_codigo", falla)

    res = client.post("/summarize", json={"code": "print(1)"})

    assert res.status_code == 503

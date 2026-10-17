from fastapi.testclient import TestClient

from app.main import app
from app.routers import summarize as router_summarize

client = TestClient(app)


def test_summarize_ok(monkeypatch) -> None:
    """Devuelve la explicación y el lenguaje que dio la IA (mockeada)."""
    monkeypatch.setattr(
        router_summarize, "resumir_codigo", lambda code: ("Suma dos números.", "python")
    )

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

    def explota(code: str) -> tuple[str, str | None]:
        raise RuntimeError("boom")

    monkeypatch.setattr(router_summarize, "resumir_codigo", explota)

    res = client.post("/summarize", json={"code": "print(1)"})

    assert res.status_code == 502

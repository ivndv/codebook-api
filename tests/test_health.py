from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    """El health responde ok (lo usa el monitoreo)."""
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

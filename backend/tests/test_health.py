"""Unit tests for FastAPI health check and root endpoints."""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "SMOKECUT" in data["app"]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_dashboard_endpoint():
    response = client.get("/app")
    assert response.status_code == 200
    assert "SMOKECUT" in response.text
    assert "AIRIMPACT" in response.text

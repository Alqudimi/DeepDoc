"""Tests for configuration endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_get_config(client):
    """Test getting configuration."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "config" in data
    assert "message" in data
    assert "ollama" in data["config"]
    assert "documentation" in data["config"]


def test_update_config(client):
    """Test updating configuration."""
    update_data = {
        "config": {
            "ollama": {
                "model": "codellama"
            }
        }
    }
    response = client.put("/config", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["config"]["ollama"]["model"] == "codellama"


def test_update_config_invalid(client):
    """Test updating configuration with invalid data."""
    response = client.put("/config", json={"invalid": "data"})
    assert response.status_code == 422


def test_reset_config(client):
    """Test resetting configuration to defaults."""
    response = client.post("/config/reset")
    assert response.status_code == 200
    data = response.json()
    assert "config" in data
    assert data["message"] == "Configuration reset to defaults"

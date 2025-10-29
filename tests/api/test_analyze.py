"""Tests for analyze endpoint."""

import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.core.task_manager import task_manager


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_tasks():
    """Clean up tasks after each test."""
    yield
    task_manager.tasks.clear()


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()
        
        (project_path / "main.py").write_text("print('Hello, world!')")
        (project_path / "README.md").write_text("# Test Project")
        
        yield str(project_path)


def test_analyze_no_params(client):
    """Test analyze without project_path or zip_file."""
    response = client.post("/analyze")
    assert response.status_code == 400
    assert "Either project_path or zip_file must be provided" in response.json()["detail"]


def test_analyze_both_params(client, temp_project):
    """Test analyze with both project_path and zip_file."""
    with open(temp_project + "/../dummy.zip", "wb") as f:
        f.write(b"PK\x03\x04")
    
    response = client.post(
        "/analyze",
        data={"project_path": temp_project},
        files={"zip_file": ("test.zip", open(temp_project + "/../dummy.zip", "rb"), "application/zip")}
    )
    assert response.status_code == 400
    assert "Provide either project_path or zip_file, not both" in response.json()["detail"]


def test_analyze_nonexistent_path(client):
    """Test analyze with nonexistent path."""
    response = client.post(
        "/analyze",
        data={"project_path": "/nonexistent/path"}
    )
    assert response.status_code == 404


def test_analyze_valid_path(client, temp_project):
    """Test analyze with valid project path."""
    response = client.post(
        "/analyze",
        data={
            "project_path": temp_project,
            "overwrite": "false"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "task_id" in data
    assert data["status"] == "pending"
    assert "message" in data
    assert "created_at" in data


def test_analyze_with_model_override(client, temp_project):
    """Test analyze with model name override."""
    response = client.post(
        "/analyze",
        data={
            "project_path": temp_project,
            "model_name": "codellama"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data


def test_analyze_with_config_overrides(client, temp_project):
    """Test analyze with configuration overrides."""
    import json
    
    config_overrides = json.dumps({
        "documentation": {
            "style": "technical"
        }
    })
    
    response = client.post(
        "/analyze",
        data={
            "project_path": temp_project,
            "config_overrides": config_overrides
        }
    )
    assert response.status_code == 200


def test_analyze_invalid_config_json(client, temp_project):
    """Test analyze with invalid config JSON."""
    response = client.post(
        "/analyze",
        data={
            "project_path": temp_project,
            "config_overrides": "not valid json"
        }
    )
    assert response.status_code == 400
    assert "Invalid config_overrides JSON" in response.json()["detail"]

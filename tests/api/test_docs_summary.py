"""Tests for docs and summary endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.core.task_manager import task_manager, TaskStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_tasks():
    """Clean up tasks after each test."""
    yield
    task_manager.tasks.clear()


def test_get_docs_nonexistent_task(client):
    """Test getting docs for nonexistent task."""
    response = client.get("/docs/nonexistent-task-id")
    assert response.status_code == 404


def test_get_docs_incomplete_task(client):
    """Test getting docs for incomplete task."""
    task_id = task_manager.create_task("/fake/path")
    
    response = client.get(f"/docs/{task_id}")
    assert response.status_code == 400
    assert "has not completed yet" in response.json()["detail"]


def test_get_summary_nonexistent_task(client):
    """Test getting summary for nonexistent task."""
    response = client.get("/summary/nonexistent-task-id")
    assert response.status_code == 404


def test_get_summary_incomplete_task(client):
    """Test getting summary for incomplete task."""
    task_id = task_manager.create_task("/fake/path")
    
    response = client.get(f"/summary/{task_id}")
    assert response.status_code == 400
    assert "has not completed yet" in response.json()["detail"]

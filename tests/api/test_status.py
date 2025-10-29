"""Tests for status endpoints."""

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


def test_get_nonexistent_task(client):
    """Test getting status of nonexistent task."""
    response = client.get("/status/nonexistent-task-id")
    assert response.status_code == 404


def test_get_task_status(client):
    """Test getting status of existing task."""
    task_id = task_manager.create_task("/fake/path")
    
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["task_id"] == task_id
    assert data["status"] == TaskStatus.PENDING.value
    assert "progress" in data
    assert "message" in data


def test_get_all_tasks_empty(client):
    """Test getting all tasks when none exist."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 0


def test_get_all_tasks(client):
    """Test getting all tasks."""
    task_id_1 = task_manager.create_task("/path/1")
    task_id_2 = task_manager.create_task("/path/2")
    
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert task_id_1 in data
    assert task_id_2 in data

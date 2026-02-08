"""Pytest fixtures for API and service tests."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on path when running tests from project root
import sys
_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

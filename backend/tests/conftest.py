import os
import sys
from typing import Generator
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path so tests can find app package
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    TestClient fixture for making HTTP requests to endpoints.
    """
    with TestClient(app) as c:
        yield c

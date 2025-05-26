import os
import sys
from fastapi.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
from src.main import app

client = TestClient(app)


def test_login():
    response = client.post(
        "/token",
        data={"username": "johndoe", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print(response.json())
    assert response.json()["token_type"] == "bearer"


# CMD: pytest -s

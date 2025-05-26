import os
import sys
from fastapi import status
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.main import app
from src.services.password import pwd_context

client = TestClient(app)


def test_login():
    response = client.post(
        "/token",
        data={"username": "johndoe", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()
    assert response["token_type"] == "bearer"
    assert "access_token" in response


def test_signup_password_hashing():
    unhashed_password = "secret"
    response = client.post(
        url=f"/auth/signup?password={unhashed_password}",
        json={
            "username": "johndoe2",
            "full_name": "John Doe2",
            "email": "johndoe2@example.com",
            "disabled": False,
        },
    )
    response_json = response.json()
    hashed_password = response_json["hashed_password"]
    assert response.status_code == status.HTTP_201_CREATED
    assert hashed_password != unhashed_password
    assert pwd_context.verify(unhashed_password, hashed_password) is True


def test_signup_validation():
    response = client.post(
        "/auth/signup?password=secret",
        json={
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "disabled": False,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "400: User already exists."}


# CMD: pytest -s
# SERVER CMD: python3 -m src.main

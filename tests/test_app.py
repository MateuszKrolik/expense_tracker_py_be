import json
import os
import sys
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.models.user import User
from src.main import app
from src.services.password import pwd_context
from src.services.database import get_session as get_session_original
from src.data.dummy_users import fake_users_db

sqlite_url = "sqlite+aiosqlite:///:memory:"

connect_args = {"check_same_thread": False}

engine = create_async_engine(sqlite_url, connect_args=connect_args, echo=False)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


app.dependency_overrides[get_session_original] = get_session


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def setup_and_teardown_db():
    async with engine.begin() as conn:
        # from src.models.category import Category

        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        user = User(**fake_users_db["johndoe"])
        session.add(user)
        await session.commit()
        await session.refresh(user)

    yield


async def get_auth_token(async_client):
    response = await async_client.post(
        "/token",
        data={"username": "johndoe", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return f"Bearer {response.json()['access_token']}"


@pytest.mark.asyncio
async def test_login(async_client):
    response = (
        await async_client.post(
            "/token",
            data={"username": "johndoe", "password": "secret"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    ).json()
    assert response["token_type"] == "bearer"
    assert "access_token" in response


@pytest.mark.asyncio
async def test_signup_password_hashing(async_client):
    unhashed_password = "secret"
    response = await async_client.post(
        url=f"/auth/signup?password={unhashed_password}",
        json={
            "username": "johndoe4",
            "full_name": "John Doe4",
            "email": "johndoe4@example.com",
            "disabled": False,
        },
    )
    response_json = response.json()
    print(f"response_json: {json.dumps(response_json)}")
    hashed_password = response_json["hashed_password"]
    assert response.status_code == status.HTTP_201_CREATED
    assert hashed_password != unhashed_password
    assert pwd_context.verify(unhashed_password, hashed_password) is True


@pytest.mark.asyncio
async def test_signup_validation(async_client):
    response = await async_client.post(
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


# @pytest.mark.asyncio
# async def test_create_category(async_client):
#     auth_token = await get_auth_token(async_client)
#     category_base = {"name": "random_name", "is_offline": False}
#     response = await async_client.post(
#         url="/users/me/categories",
#         json=category_base,
#         headers={
#             "Authorization": auth_token,
#         },
#     )
#     print(response.json())
#     assert response.status_code == 201
#     response = await async_client.post(
#         url="/users/me/categories",
#         json=category_base,
#         headers={
#             "Authorization": auth_token,
#         },
#     )
#     assert response.status_code == 400
#     assert response.json()["detail"] == "400: Category with given name already exists."


# CMD: pytest -s
# SERVER CMD: python3 -m src.main

import os
from typing import Annotated, List
from fastapi import Depends
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from src.data.dummy_users import fake_users_db

from src.decorators.db_exception_handlers import command_exception_handler
from src.models.user import User

SQLITE_FILE_NAME = "database.db"


is_docker = os.getenv("IS_DOCKER", "false").lower() == "true"

connect_args = {}

if is_docker:
    database_url = os.getenv("DATABASE_URL")
else:
    database_url = f"sqlite+aiosqlite:///{SQLITE_FILE_NAME}"
    connect_args["check_same_thread"] = False

engine = create_async_engine(database_url, connect_args=connect_args, echo=False)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@command_exception_handler
async def seed_dummy_users() -> List[User]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        users: List[User] = []
        for _, fake_user in fake_users_db.items():
            user = User(**fake_user)
            user = await session.merge(user)
            users.append(user)
        await session.commit()
        return users


async def create_db_and_tables():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

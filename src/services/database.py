from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from data.dummy_users import fake_users_db

from models.user import User

sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_async_engine(sqlite_url, connect_args=connect_args, echo=True)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def seed_dummy_users() -> List[User]:
    users: List[User] = []
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            for _, fake_user in fake_users_db.items():
                user = User(**fake_user)
                user = await session.merge(user)
                users.append(user)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    return users


async def create_db_and_tables():
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from decorators.db_exception_handlers import query_exception_handler
from models.user import User
from services.database import SessionDep, engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@query_exception_handler
async def get_user(session: SessionDep, username: str):
    user = await session.get(User, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    return user


async def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    async with AsyncSession(engine) as session:
        user = await get_user(session, token)
        return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def fake_hash_password(password: str):
    return "fakehashed" + password

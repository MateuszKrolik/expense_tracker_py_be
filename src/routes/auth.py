from typing import Annotated
from fastapi import APIRouter, Depends

from models.user import User
from services.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user

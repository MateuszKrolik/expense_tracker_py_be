from typing import Annotated
from fastapi import APIRouter, Depends

from models.user import User
from services.auth import get_current_active_user


router = APIRouter(prefix="/users/me", tags=["users"])


@router.get("")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.get("/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

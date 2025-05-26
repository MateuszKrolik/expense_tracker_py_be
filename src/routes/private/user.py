from typing import Annotated
from fastapi import APIRouter, Depends

from src.models.user import User
from src.services.auth import get_current_active_user
from src.routes.private.category import router as category_routes
from src.routes.private.budget import router as budget_routes
from src.routes.private.expense import router as expense_routes

router = APIRouter(prefix="/users/me", tags=["users"])
router.include_router(category_routes)
router.include_router(budget_routes)
router.include_router(expense_routes)


@router.get("")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user

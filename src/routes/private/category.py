from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query, status

from src.dtos.paged_response import PagedResponse
from src.models.category import Category, CategoryBase
from src.models.user import User
from src.services.auth import get_current_active_user
from src.services.category import (
    create_category,
    create_offline_categories_batch,
    get_all_categories,
)
from src.services.database import SessionDep


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_category_entity(
    session: SessionDep,
    category_base: CategoryBase,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Optional[Category]:
    return await create_category(
        session=session, category_base=category_base, current_user=current_user
    )


@router.get("")
async def get_categories(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Category]:
    return await get_all_categories(session=session, current_user=current_user)


@router.post(path="/offline", status_code=status.HTTP_201_CREATED)
async def create_offline_categories(
    session: SessionDep,
    categories_base: List[CategoryBase],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[Category]:
    return await create_offline_categories_batch(
        session=session, categories_base=categories_base, current_user=current_user
    )

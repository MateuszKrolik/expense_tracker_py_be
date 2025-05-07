from typing import Annotated, List, Optional
from fastapi import APIRouter, Query, status

from dtos.paged_response import PagedResponse
from models.category import Category, CategoryBase
from services.category import (
    create_category,
    create_offline_categories_batch,
    get_all_categories,
)
from services.database import SessionDep


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_category_entity(
    session: SessionDep, category_base: CategoryBase
) -> Optional[Category]:
    return await create_category(session=session, category_base=category_base)


@router.get("")
async def get_categories(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Category]:
    return await get_all_categories(session=session)


@router.post(path="/offline", status_code=status.HTTP_201_CREATED)
async def create_offline_categories(
    session: SessionDep, categories_base: List[CategoryBase]
) -> List[Category]:
    return await create_offline_categories_batch(
        session=session, categories_base=categories_base
    )

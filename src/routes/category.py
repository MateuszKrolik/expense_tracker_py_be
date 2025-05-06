from typing import List, Optional
from fastapi import APIRouter, status

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
    return create_category(session=session, category_base=category_base)


@router.get("")
async def get_categories(session: SessionDep) -> PagedResponse[Category]:
    return get_all_categories(session=session)


@router.post(path="/offline", status_code=status.HTTP_201_CREATED)
async def create_offline_categories(
    session: SessionDep, categories_base: List[CategoryBase]
) -> List[Category]:
    return create_offline_categories_batch(
        session=session, categories_base=categories_base
    )

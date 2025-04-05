from typing import Optional
from fastapi import APIRouter, status

from models.category import Category, CategoryBase
from services.category import create_category, get_all_categories
from services.database import SessionDep


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_category_entity(
    session: SessionDep, category_base: CategoryBase
) -> Optional[Category]:
    return create_category(session=session, category_base=category_base)


@router.get("")
async def get_categories(session: SessionDep):
    return get_all_categories(session=session)

from typing import List, Optional
from fastapi import status, HTTPException
from sqlmodel import select
from models.category import Category, CategoryBase
from services.database import SessionDep


def get_all_categories(session: SessionDep) -> List[Category]:
    categories = []
    try:
        query = select(Category)
        categories.extend(session.exec(query).all())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return categories


def create_category(
    session: SessionDep, category_base: CategoryBase
) -> Optional[Category]:
    category = None
    _check_for_existing_category(session=session, category_base=category_base)
    try:
        category = Category(**category_base.model_dump())
        session.add(category)
        session.commit()
        session.refresh(category)  # to not return empty entity
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return category


def _check_for_existing_category(session: SessionDep, category_base: CategoryBase):
    existing = None
    try:
        existing = session.exec(
            select(Category).where(Category.name == category_base.name)
        ).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with given name already exists.",
        )

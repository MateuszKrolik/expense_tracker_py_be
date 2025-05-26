from typing import Annotated, List, Optional
from fastapi import Query, status, HTTPException
from sqlmodel import func, select
from src.decorators.db_exception_handlers import (
    command_exception_handler,
    query_exception_handler,
)
from src.dtos.paged_response import PagedResponse
from src.models.category import Category, CategoryBase
from src.models.user import User
from src.services.database import SessionDep


@query_exception_handler
async def get_all_categories(
    session: SessionDep,
    current_user: User,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Category]:
    query = select(Category).where(Category.owner == current_user.username)
    items = (await session.exec(query.offset(offset).limit(limit))).all()
    total_count = (await session.exec(select(func.count()).select_from(query))).one()
    return PagedResponse[Category](
        items=items, offset=offset, limit=limit, total_count=total_count
    )


@command_exception_handler
async def create_category(
    session: SessionDep,
    category_base: CategoryBase,
    current_user: User,
) -> Optional[Category]:
    exists = await _check_for_existing_category(
        session=session, category_base=category_base, current_user=current_user
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with given name already exists.",
        )
    category = Category(**category_base.model_dump())
    category.owner = current_user.username
    session.add(category)
    await session.commit()
    await session.refresh(category)  # to not return empty entity
    return category


@command_exception_handler
async def create_offline_categories_batch(
    session: SessionDep, categories_base: CategoryBase, current_user: User
) -> List[Category]:
    categories: List[Category] = []
    for category_base in categories_base:
        exists = await _check_for_existing_category(
            session=session, category_base=category_base, current_user=current_user
        )
        if exists or not category_base.is_offline:
            continue
        category = Category(**category_base.model_dump())
        category.owner = current_user.username
        session.add(category)
        categories.append(category)
    await session.commit()
    for category in categories:
        await session.refresh(category)
    return categories


@query_exception_handler
async def _check_for_existing_category(
    session: SessionDep,
    category_base: CategoryBase,
    current_user: User,
) -> Optional[bool]:
    return (
        await session.execute(
            select(Category).where(
                Category.name == category_base.name,
                Category.owner == current_user.username,
            )
        )
    ).first() is not None

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import Depends, Query, status, HTTPException
from sqlmodel import String, cast, func, or_, select
from src.decorators.db_exception_handlers import (
    command_exception_handler,
    query_exception_handler,
)
from src.dtos.paged_response import PagedResponse
from src.models.budget import Budget
from src.models.category import Category
from src.models.expense import Expense, ExpenseBase
from src.models.user import User
from src.services.auth import get_current_active_user
from src.services.budget import get_budget_for_given_month
from src.services.database import SessionDep


@command_exception_handler
async def save_expense_after_successful_validation(
    session: SessionDep, current_user: User, expense_base: ExpenseBase
) -> Optional[Expense]:
    expense = Expense(**expense_base.model_dump())
    expense.owner = current_user.username
    category = await session.get(Category, expense.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found, either pick from available or create one.",
        )
    if category.owner != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This category doesn't belong to you.",
        )
    decremented_budget = await _decrement_budget_if_possible_and_return_after(
        session=session, current_user=current_user, expense=expense
    )
    if not decremented_budget:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail="Decrement operation not possible, either the budget doesn't exist or is too low.",
        )
    # completes transaction
    return await _save_expense(session=session, expense=expense)


@query_exception_handler
async def get_all_expenses(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    category_id: Optional[UUID] = Query(None),
    name_query: Optional[str] = Query(None),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Expense]:
    query = select(Expense).where(Expense.owner == current_user.username)
    if category_id is not None:
        query = query.where(Expense.category_id == category_id)
    if name_query is not None:
        query = query.where(cast(Expense.name, String).ilike(f"%{name_query}%"))
    items = (await session.exec(query.offset(offset).limit(limit))).all()
    total_count = (await session.exec(select(func.count()).select_from(query))).one()
    return PagedResponse[Expense](
        items=items, offset=offset, limit=limit, total_count=total_count
    )


@query_exception_handler
async def get_single_expense_by_id(
    session: SessionDep, current_user: User, expense_id: UUID, is_public: bool = False
) -> Optional[Expense]:
    expense = await session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )
    if not is_public:
        if expense.owner != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This expense doesn't belong to you.",
            )

    return expense


@command_exception_handler
async def save_offline_expenses_batch(
    session: SessionDep, current_user: User, expenses_base: List[ExpenseBase]
) -> List[Expense]:
    expenses: List[Expense] = []
    for expense_base in expenses_base:
        expense = Expense(**expense_base.model_dump())
        expense.owner = current_user.username
        category = await session.get(Category, expense.category_id)
        decremented_budget = await _decrement_budget_if_possible_and_return_after(
            session=session, current_user=current_user, expense=expense
        )
        if category is None or decremented_budget is None:
            continue
        session.add(expense)
        expenses.append(expense)
    await session.commit()
    for expense in expenses:
        await session.refresh(expense)
    return expenses


async def _decrement_budget_if_possible_and_return_after(
    session: SessionDep, current_user: User, expense: Expense
) -> Optional[Budget]:
    budget = await get_budget_for_given_month(
        session=session,
        current_user=current_user,
        year=expense.timestamp.year,
        month=expense.timestamp.month,
    )
    budget_after_expense = budget.remaining_budget - expense.amount
    if budget is None or budget_after_expense < 0:
        return None
    budget.remaining_budget -= expense.amount
    return budget


@command_exception_handler
async def _save_expense(session: SessionDep, expense: Expense) -> Optional[Expense]:
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


@command_exception_handler
async def share_expense(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    expense_id: UUID,
):
    expense = await get_single_expense_by_id(
        session=session,
        current_user=current_user,
        expense_id=expense_id,
        is_public=True,
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.is_public = True
    session.add(expense)
    await session.commit()
    await session.refresh(expense)

    return expense


@query_exception_handler
async def get_all_public_expenses(
    session: SessionDep,
    category_id: Optional[UUID] = Query(None),
    query: Optional[str] = Query(None, description="Query by expense name or username"),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Expense]:
    sql_query = select(Expense).where(Expense.is_public)
    if category_id is not None:
        sql_query = sql_query.where(Expense.category_id == category_id)
    if query is not None:
        sql_query = sql_query.where(
            or_(
                cast(Expense.name, String).ilike(f"%{query}%"),
                cast(Expense.owner, String).ilike(f"%{query}%"),
            )
        )
    items = (await session.exec(sql_query.offset(offset).limit(limit))).all()
    total_count = (
        await session.exec(select(func.count()).select_from(sql_query))
    ).one()
    return PagedResponse[Expense](
        items=items, offset=offset, limit=limit, total_count=total_count
    )

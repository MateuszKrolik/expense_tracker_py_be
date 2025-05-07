from typing import Annotated, List, Optional
from uuid import UUID

from decorators.db_exception_handlers import (
    command_exception_handler,
    query_exception_handler,
)
from dtos.paged_response import PagedResponse
from models.budget import Budget
from models.category import Category
from models.expense import Expense, ExpenseBase
from services.budget import get_budget_for_given_month
from fastapi import Query, status, HTTPException
from services.database import SessionDep
from sqlmodel import String, cast, func, select


@command_exception_handler
async def save_expense_after_successful_validation(
    session: SessionDep, expense_base: ExpenseBase
) -> Optional[Expense]:
    expense = Expense(**expense_base.model_dump())
    category = await session.get(Category, expense.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found, either pick from available or create one.",
        )
    decremented_budget = await _decrement_budget_if_possible_and_return_after(
        session=session, expense=expense
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
    category_id: Optional[UUID] = Query(None),
    name_query: Optional[str] = Query(None),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Expense]:
    query = select(Expense)
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
    session: SessionDep, expense_id: UUID
) -> Optional[Expense]:
    expense = await session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    return expense


@query_exception_handler
async def get_all_expenses_for_category_id(
    session: SessionDep,
    category_id: UUID,
    name_query: Optional[str] = Query(None),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Expense]:
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    query = select(Expense)
    if name_query is not None:
        query = query.where(cast(Expense.name, String).ilike(f"%{name_query}%"))
    items = (
        await session.exec(
            query.where(Expense.category_id == category_id).offset(offset).limit(limit)
        )
    ).all()
    total_count = (await session.exec(select(func.count()).select_from(query))).one()
    return PagedResponse[Expense](
        items=items, offset=offset, limit=limit, total_count=total_count
    )


@command_exception_handler
async def save_offline_expenses_batch(
    session: SessionDep, expenses_base: List[ExpenseBase]
) -> List[Expense]:
    expenses: List[Expense] = []
    for expense_base in expenses_base:
        expense = Expense(**expense_base.model_dump())
        category = await session.get(Category, expense.category_id)
        decremented_budget = await _decrement_budget_if_possible_and_return_after(
            session=session, expense=expense
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
    session: SessionDep, expense: Expense
) -> Optional[Budget]:
    budget = await get_budget_for_given_month(
        session=session, year=expense.timestamp.year, month=expense.timestamp.month
    )
    budget_after_expense = budget.remaining_budget - expense.amount
    if budget is None or budget_after_expense < 0:
        return None
    budget.remaining_budget -= expense.amount
    return budget


async def _save_expense(session: SessionDep, expense: Expense) -> Optional[Expense]:
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense

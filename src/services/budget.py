from typing import List, Optional
from decorators.db_exception_handlers import (
    command_exception_handler,
    query_exception_handler,
)
from models.budget import Budget, BudgetBase
from fastapi import status, HTTPException
from sqlmodel import select
from models.user import User
from services.database import SessionDep


@command_exception_handler
async def set_budget_for_given_month(
    session: SessionDep, current_user: User, budget_base: BudgetBase
):
    exists = await _does_budget_already_exist(
        session=session, current_user=current_user, budget_base=budget_base
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Budget already exists for: {budget_base.month}/{budget_base.year}.",
        )
    budget = Budget(**budget_base.model_dump())
    budget.owner = current_user.username
    budget.remaining_budget = budget.max_budget
    session.add(budget)
    await session.commit()
    await session.refresh(budget)  # to not return empty entity
    return budget


@query_exception_handler
async def get_budget_for_given_month(
    session: SessionDep,
    current_user: User,
    year: int,
    month: int,
) -> Optional[Budget]:
    result = (
        await session.exec(
            select(Budget)
            .where(Budget.owner == current_user.username)
            .where(Budget.year == year)
            .where(Budget.month == month)
            .with_for_update()  # lock row to prevent concurrent updates
        )
    ).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No budget set for given month.",
        )
    return result


@command_exception_handler
async def create_offline_budgets_batch(
    session: SessionDep, current_user: User, budgets_base: BudgetBase
) -> List[Budget]:
    budgets: List[Budget] = []
    for budget_base in budgets_base:
        exists = await _does_budget_already_exist(
            session=session, current_user=current_user, budget_base=budget_base
        )
        if exists or not budget_base.is_offline:
            continue
        budget = Budget(**budget_base.model_dump())
        budget.owner = current_user.username
        budget.remaining_budget = budget.max_budget
        session.add(budget)
        budgets.append(budget)
    await session.commit()
    for budget in budgets:
        await session.refresh(budget)
    return budgets


@query_exception_handler
async def _does_budget_already_exist(
    session: SessionDep, current_user: User, budget_base: BudgetBase
) -> Optional[bool]:
    return (
        await session.exec(
            select(Budget)
            .where(Budget.owner == current_user.username)
            .where(Budget.year == budget_base.year)
            .where(Budget.month == budget_base.month)
        )
    ).first() is not None

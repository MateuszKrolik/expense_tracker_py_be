from typing import List, Optional, Tuple
from models.budget import Budget, BudgetBase
from fastapi import status, HTTPException
from sqlmodel import select
from services.database import SessionDep


def set_budget_for_given_month(session: SessionDep, budget_base: BudgetBase):
    result: Optional[Budget] = None
    exists = _does_budget_already_exist(session=session, budget_base=budget_base)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Budget already exists for: {budget_base.month}/{budget_base.year}.",
        )
    try:
        budget = Budget(**budget_base.model_dump())
        budget.remaining_budget = budget.max_budget
        result = budget
        session.add(budget)
        session.commit()
        session.refresh(budget)  # to not return empty entity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return result


def get_budget_for_given_month(
    session: SessionDep, year: int, month: int
) -> Optional[Budget]:
    result: Optional[Budget] = None
    try:
        result = session.exec(
            select(Budget)
            .where(Budget.year == year)
            .where(Budget.month == month)
            .with_for_update()  # lock row to prevent concurrent updates
        ).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No budget set for given month.",
        )

    return result


def create_offline_budgets_batch(
    session: SessionDep, budgets_base: BudgetBase
) -> List[Budget]:
    budgets: List[Budget] = []
    try:
        for budget_base in budgets_base:
            exists = _does_budget_already_exist(
                session=session, budget_base=budget_base
            )
            if exists or not budget_base.is_offline:
                continue
            budget = Budget(**budget_base.model_dump())
            session.add(budget)
            budgets.append(budget)
        session.commit()
        for budget in budgets:
            session.refresh(budget)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return budgets


def _does_budget_already_exist(
    session: SessionDep, budget_base: BudgetBase
) -> Optional[bool]:
    existing: Optional[Budget] = None
    try:
        existing = session.exec(
            select(Budget)
            .where(Budget.year == budget_base.year)
            .where(Budget.month == budget_base.month)
        ).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return existing is not None

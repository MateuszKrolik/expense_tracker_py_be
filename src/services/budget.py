from typing import Optional, Tuple
from models.budget import Budget, BudgetBase
from fastapi import status, HTTPException
from sqlmodel import select
from services.database import SessionDep


def set_budget_for_given_month(session: SessionDep, budget_base: BudgetBase):
    result: Optional[Budget] = None
    exists, _ = _check_for_existing_budget(session=session, budget_base=budget_base)
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


def _check_for_existing_budget(
    session: SessionDep, budget_base: BudgetBase
) -> Tuple[bool, Optional[Budget]]:
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

    return existing is not None, existing


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

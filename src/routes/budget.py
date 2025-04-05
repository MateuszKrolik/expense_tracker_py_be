from typing import Optional

from fastapi import APIRouter
from services.budget import get_budget_for_given_month, set_budget_for_given_month
from services.database import SessionDep
from models.budget import Budget, BudgetBase


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("")
async def set_budget_for_month(
    session: SessionDep, budget_base: BudgetBase
) -> Optional[Budget]:
    return set_budget_for_given_month(session=session, budget_base=budget_base)


@router.get("")
async def get_budget_for_month(
    session: SessionDep, year: int, month: int
) -> Optional[Budget]:
    return get_budget_for_given_month(session=session, year=year, month=month)

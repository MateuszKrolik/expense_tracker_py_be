from typing import List, Optional

from fastapi import APIRouter
from services.budget import (
    create_offline_budgets_batch,
    get_budget_for_given_month,
    set_budget_for_given_month,
)
from services.database import SessionDep
from models.budget import Budget, BudgetBase


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/offline")
async def set_offline_budgets_batch(
    session: SessionDep, budgets_base: List[BudgetBase]
) -> List[Budget]:
    return create_offline_budgets_batch(session=session, budgets_base=budgets_base)


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

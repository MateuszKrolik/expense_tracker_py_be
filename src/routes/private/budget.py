from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends
from models.user import User
from services.auth import get_current_active_user
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
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    budgets_base: List[BudgetBase],
) -> List[Budget]:
    return await create_offline_budgets_batch(
        session=session, current_user=current_user, budgets_base=budgets_base
    )


@router.post("")
async def set_budget_for_month(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    budget_base: BudgetBase,
) -> Optional[Budget]:
    return await set_budget_for_given_month(
        session=session, current_user=current_user, budget_base=budget_base
    )


@router.get("")
async def get_budget_for_month(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    year: int,
    month: int,
) -> Optional[Budget]:
    return await get_budget_for_given_month(
        session=session, current_user=current_user, year=year, month=month
    )

from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from dtos.paged_response import PagedResponse
from models.expense import Expense, ExpenseBase
from models.user import User
from services.auth import get_current_active_user
from services.database import SessionDep
from services.expense import (
    get_all_expenses,
    get_single_expense_by_id,
    save_expense_after_successful_validation,
    save_offline_expenses_batch,
    share_expense,
)


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post(path="", status_code=status.HTTP_201_CREATED)
async def save_expense(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    expense_base: ExpenseBase,
) -> Expense:
    return await save_expense_after_successful_validation(
        session=session, current_user=current_user, expense_base=expense_base
    )


@router.get("")
async def get_expenses(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    category_id: Optional[UUID] = Query(None),
    name_query: Optional[str] = Query(None),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Expense]:
    return await get_all_expenses(
        session=session,
        current_user=current_user,
        category_id=category_id,
        name_query=name_query,
    )


@router.get("/{expense_id}")
async def get_expense_by_id(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    expense_id: UUID,
):
    return await get_single_expense_by_id(
        session=session, current_user=current_user, expense_id=expense_id
    )


@router.patch("/{expense_id}/share", response_model=Expense)
async def share_expense_endpoint(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    expense_id: UUID,
):
    return await share_expense(
        session=session, current_user=current_user, expense_id=expense_id
    )


@router.post(path="/offline", status_code=status.HTTP_201_CREATED)
async def save_offline_expenses(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    expenses_base: List[ExpenseBase],
) -> List[Expense]:
    return await save_offline_expenses_batch(
        session=session, current_user=current_user, expenses_base=expenses_base
    )

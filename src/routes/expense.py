from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Query, status

from dtos.paged_response import PagedResponse
from models.expense import Expense, ExpenseBase
from services.database import SessionDep
from services.expense import (
    get_all_expenses,
    get_single_expense_by_id,
    save_expense_after_successful_validation,
    save_offline_expenses_batch,
)


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post(path="", status_code=status.HTTP_201_CREATED)
async def save_expense(session: SessionDep, expense_base: ExpenseBase) -> Expense:
    return await save_expense_after_successful_validation(
        session=session, expense_base=expense_base
    )


@router.get("")
async def get_expenses(
    session: SessionDep,
    category_id: Optional[UUID] = Query(None),
    name_query: Optional[str] = Query(None),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Expense]:
    return await get_all_expenses(
        session=session, category_id=category_id, name_query=name_query
    )


@router.get("/{expense_id}")
async def get_expense_by_id(session: SessionDep, expense_id: UUID):
    return await get_single_expense_by_id(session=session, expense_id=expense_id)


@router.post(path="/offline", status_code=status.HTTP_201_CREATED)
async def save_offline_expenses(
    session: SessionDep, expenses_base: List[ExpenseBase]
) -> List[Expense]:
    return await save_offline_expenses_batch(
        session=session, expenses_base=expenses_base
    )

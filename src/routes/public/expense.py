from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Query

from src.dtos.paged_response import PagedResponse
from src.models.expense import Expense
from src.services.database import SessionDep
from src.services.expense import get_all_public_expenses


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("")
async def get_public_expenses(
    session: SessionDep,
    category_id: Optional[UUID] = Query(None),
    query: Optional[str] = Query(None, description="Query by expense name or username"),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> PagedResponse[Expense]:
    return await get_all_public_expenses(
        session=session,
        category_id=category_id,
        query=query,
    )

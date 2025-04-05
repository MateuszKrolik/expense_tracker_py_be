from typing import List, Optional
from uuid import UUID
from models.category import Category
from models.expense import Expense, ExpenseBase
from services.budget import get_budget_for_given_month
from fastapi import Query, status, HTTPException
from services.database import SessionDep
from sqlmodel import String, cast, select


def save_expense_after_successful_validation(
    session: SessionDep, expense_base: ExpenseBase
) -> Optional[Expense]:
    result: Optional[Expense] = None
    expense = Expense(**expense_base.model_dump())
    category = session.get(Category, expense.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found, either pick from available or create one.",
        )
    budget = get_budget_for_given_month(
        session=session, year=expense.date.year, month=expense.date.month
    )
    budget_after_expense = budget.remaining_budget - expense.amount
    if budget_after_expense < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense too large for remaining budget in given month.",
        )
    budget.remaining_budget -= expense.amount
    # completes transaction
    result = _save_expense(session=session, expense=expense)

    return result


def _save_expense(session: SessionDep, expense: Expense) -> Optional[Expense]:
    result: Optional[Expense] = None
    try:
        session.add(expense)
        session.commit()
        session.refresh(expense)
        result = expense
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return result


def get_all_expenses(
    session: SessionDep, name_query: Optional[str] = Query(None)
) -> List[Expense]:
    try:
        query = select(Expense)
        if name_query is not None:
            query = query.where(cast(Expense.name, String).ilike(f"%{name_query}%"))
        return session.exec(query).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def get_single_expense_by_id(
    session: SessionDep, expense_id: UUID
) -> Optional[Expense]:
    expense = session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    return expense


def get_all_expenses_for_category_id(
    session: SessionDep, category_id: UUID, name_query: Optional[str] = Query(None)
) -> List[Expense]:
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    try:
        query = select(Expense)
        if name_query is not None:
            query = query.where(cast(Expense.name, String).ilike(f"%{name_query}%"))
        return session.exec(query.where(Expense.category_id == category_id)).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

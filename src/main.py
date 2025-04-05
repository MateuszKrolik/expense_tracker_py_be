from typing import List, Optional
from uuid import UUID
import uvicorn
from fastapi import FastAPI, Query, status

from models.budget import Budget, BudgetBase
from models.expense import Expense, ExpenseBase
from models.category import Category as CategoryModel, CategoryBase
from services.budget import get_budget_for_given_month, set_budget_for_given_month
from services.category import create_category, get_all_categories
from services.database import SessionDep, create_db_and_tables
from services.expense import (
    get_all_expenses,
    get_all_expenses_for_category_id,
    get_single_expense_by_id,
    save_expense_after_successful_validation,
)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post(path="/expenses", status_code=status.HTTP_201_CREATED)
async def save_expense(session: SessionDep, expense_base: ExpenseBase) -> Expense:
    return save_expense_after_successful_validation(
        session=session, expense_base=expense_base
    )


@app.get("/expenses")
async def get_expenses(
    session: SessionDep, name_query: Optional[str] = Query(None)
) -> List[Expense]:
    return get_all_expenses(session=session, name_query=name_query)


@app.get("/expenses/{expense_id}")
async def get_expense_by_id(session: SessionDep, expense_id: UUID):
    return get_single_expense_by_id(session=session, expense_id=expense_id)


@app.get("/categories/{category_id}/expenses")
async def get_expenses_by_category_id(
    session: SessionDep, category_id: UUID, name_query: Optional[str] = Query(None)
) -> List[Expense]:
    return get_all_expenses_for_category_id(
        session=session, category_id=category_id, name_query=name_query
    )


@app.post(path="/categories", status_code=status.HTTP_201_CREATED)
async def create_category_entity(
    session: SessionDep, category_base: CategoryBase
) -> Optional[CategoryModel]:
    return create_category(session=session, category_base=category_base)


@app.get("/categories")
async def get_categories(session: SessionDep):
    return get_all_categories(session=session)


@app.post("/budget")
async def set_budget_for_month(
    session: SessionDep, budget_base: BudgetBase
) -> Optional[Budget]:
    return set_budget_for_given_month(session=session, budget_base=budget_base)


@app.get("/budget")
async def get_budget_for_month(session: SessionDep, year: int, month: int):
    return get_budget_for_given_month(session=session, year=year, month=month)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

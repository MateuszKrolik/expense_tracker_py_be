from typing import Optional
import uvicorn
from fastapi import FastAPI, status

from models.budget import Budget, BudgetBase
from models.category import Category as CategoryModel, CategoryBase
from services.budget import get_budget_for_given_month, set_budget_for_given_month
from routes.expense import router as expense_routes
from services.category import create_category, get_all_categories
from services.database import SessionDep, create_db_and_tables

app = FastAPI()

app.include_router(expense_routes)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


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

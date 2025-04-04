import os.path
from uuid import UUID
import csv
import uvicorn
from fastapi import FastAPI, status, HTTPException

from models.budget import Budget, BudgetBase
from models.expense import Expense, ExpenseBase
from models.category import Category as CategoryModel, CategoryBase
from services.category import get_all_categories, get_all_category_ids
from services.database import create_db_and_tables
from services.expense import save_expense

EXPENSES_PATH = "data/expenses.csv"
BUDGETS_PATH = "data/budgets.csv"
CATEGORIES_PATH = "data/categories.csv"

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post(path="/expenses", status_code=status.HTTP_201_CREATED)
async def save_expense_to_file(expense_base: ExpenseBase) -> Expense:
    return save_expense(expense_base=expense_base)


@app.get("/categories")
async def get_categories():
    return get_all_categories()


@app.get("/expenses")
async def get_expenses():
    rows = []
    try:
        with open(EXPENSES_PATH, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(row)
            return rows
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/categories/{category_id}/expenses")
async def get_expenses_by_category_id(category_id: UUID):
    if category_id in get_all_category_ids():
        rows = []
        with open(EXPENSES_PATH, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if UUID(row["category_id"]) == category_id:
                    rows.append(row)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found, pick from existing ones.",
        )

    return rows


@app.get("/expenses/{expense_id}")
async def get_expense_by_id(expense_id: UUID):
    with open(EXPENSES_PATH, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if UUID(row["id"]) == expense_id:
                return row
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense with id: {expense_id} not found.",
                )


@app.post("/year/{year}/month/{month_number}/budget")
async def set_budget_for_month(year: int, month_number: int, budget_base: BudgetBase):
    try:
        budget = Budget(
            year=year,
            month=month_number,
            max_budget=budget_base.max_budget,
            remaining_budget=budget_base.max_budget,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e).replace("\n", " ")
        )
    with open(BUDGETS_PATH, "a") as file:
        writer = csv.writer(file)
        if not os.path.isfile(BUDGETS_PATH) or os.stat(BUDGETS_PATH).st_size == 0:
            writer.writerow(budget.model_dump().keys())
        writer.writerow(budget.model_dump().values())
    return budget


@app.post(path="/categories", status_code=status.HTTP_201_CREATED)
async def create_category(category_base: CategoryBase):
    category = CategoryModel(**category_base.model_dump())
    try:
        with open(CATEGORIES_PATH, "a") as file:
            writer = csv.writer(file)
            if (
                not os.path.isfile(CATEGORIES_PATH)
                or os.stat(CATEGORIES_PATH).st_size == 0
            ):
                writer.writerow(category.model_dump().keys())
            writer.writerow(category.model_dump().values())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return category


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

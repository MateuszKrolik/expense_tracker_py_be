import os.path
from typing import List
from uuid import UUID
import csv
from fastapi import FastAPI, status, HTTPException

from dtos.budget_base import BudgetBase
from dtos.category_base import CategoryBase
from dtos.expense_base import ExpenseBase

from models.budget import Budget
from models.expense import Expense
from models.category import Category as CategoryModel

EXPENSES_PATH = "data/expenses.csv"
BUDGETS_PATH = "data/budgets.csv"
CATEGORIES_PATH = "data/categories.csv"

app = FastAPI()

@app.post(path="/expenses", status_code=status.HTTP_201_CREATED)
async def save_expense_to_file(expense_base: ExpenseBase):
    expense = Expense(**expense_base.model_dump())
    budget_before_expense = _get_budget_for_given_month(year=expense.date.year, month=expense.date.month)
    budget_after_expense = budget_before_expense.remaining_budget - expense.amount
    if budget_after_expense < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense too large for remaining budget in given month.")
    else:
        _decrement_remaining_budget(budget=budget_before_expense, decrement=expense.amount)
    with open(EXPENSES_PATH, "a") as file:
        writer = csv.writer(file)
        if not os.path.isfile(EXPENSES_PATH) or os.stat(EXPENSES_PATH).st_size == 0:
            writer.writerow(expense.model_dump().keys())
        if expense.category_id in _get_all_category_ids():
            writer.writerow(expense.model_dump().values())
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category not found, pick from existing ones.")

    return expense

@app.get("/categories")
async def get_categories():
    return _get_all_categories()

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/categories/{category_id}/expenses")
async def get_expenses_by_category_id(category_id: UUID):
    if category_id in _get_all_category_ids():
        rows = []
        with open(EXPENSES_PATH, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if UUID(row["category_id"]) == category_id:
                    rows.append(row)
    else:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Category not found, pick from existing ones.")

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
                    detail=f"Expense with id: {expense_id} not found."
                )

@app.post("/year/{year}/month/{month_number}/budget")
async def set_budget_for_month(year: int, month_number: int, budget_base: BudgetBase):
    try:
        budget = Budget(
            year=year,
            month=month_number,
            max_budget=budget_base.max_budget,
            remaining_budget=budget_base.max_budget
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e).replace('\n', ' '))
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
            if not os.path.isfile(CATEGORIES_PATH) or os.stat(CATEGORIES_PATH).st_size == 0:
                writer.writerow(category.model_dump().keys())
            writer.writerow(category.model_dump().values())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return category

def _decrement_remaining_budget(budget: Budget, decrement: float):
    decrement_result = budget.remaining_budget - decrement
    if decrement_result >= 0:
        budget.remaining_budget = decrement_result
        _save_updated_budget(budget)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Balance after decrement must be more than or equal to 0."
        )


def _save_updated_budget(budget: Budget):
    rows = []
    with open(BUDGETS_PATH, "r") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        for row in reader:
            if not (int(row["year"]) == budget.year and
                    int(row["month"]) == budget.month):
                rows.append(row)
    rows.append(budget.model_dump())
    with open(BUDGETS_PATH, "w") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def _get_budget_for_given_month(year: int, month: int)-> Budget:
    with open(BUDGETS_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["year"]) == year and int(row["month"]) == month:
                return Budget(**row)

def _get_all_categories() -> List[CategoryModel]:
    try:
        with open(CATEGORIES_PATH, "r") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append(CategoryModel(**row))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return rows

def _get_all_category_ids() -> List[UUID]:
    categories = _get_all_categories()
    category_ids = []
    for category in categories:
        category_ids.append(category.id)

    return category_ids

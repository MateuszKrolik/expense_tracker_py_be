import os.path
from uuid import UUID
import csv
from fastapi import FastAPI, status, HTTPException
from dtos.expense_base import ExpenseBase
from enums.category import Category
from models.expense import Expense

FILE_PATH = "data/expenses.csv"
app = FastAPI()

@app.post(path="/expenses", status_code=status.HTTP_201_CREATED)
async def save_expense_to_file(expense_base: ExpenseBase):
    expense = Expense(**expense_base.model_dump())
    with open(FILE_PATH, "a") as file:
        writer = csv.writer(file)
        if not os.path.isfile(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
            writer.writerow(expense.model_dump().keys())
        if expense.category in range(len(Category)):
            writer.writerow(expense.model_dump().values())
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category not found, pick from 0-{(len(Category)) - 1}."
            )
    return expense

@app.get("/categories")
async def get_categories():
    return {category.name: category.value for category in Category}

@app.get("/expenses")
async def get_expenses():
    rows = []
    try:
        with open(FILE_PATH, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                    rows.append(row)
            return rows
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/categories/{category_number}")
async def get_expenses_by_category(category_number: int):
    if category_number in range(len(Category)):
        rows = []
        with open(FILE_PATH, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["category"]) == category_number:
                    rows.append(row)
            return rows
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Category not found, pick from 0-{(len(Category)) - 1}."
    )

@app.get("/expenses/{expense_id}")
async def get_expense_by_id(expense_id: UUID):
    with open(FILE_PATH, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if UUID(row["id"]) == expense_id:
                return row
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expense with id: {expense_id} not found."
                )
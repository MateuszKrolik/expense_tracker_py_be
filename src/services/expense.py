import os
import csv
from models.expense import Expense, ExpenseBase
from services.budget import decrement_remaining_budget, get_budget_for_given_month
from fastapi import status, HTTPException
from services.category import get_all_category_ids


EXPENSES_PATH = "data/expenses.csv"


def save_expense(expense_base: ExpenseBase) -> Expense:
    expense = Expense(**expense_base.model_dump())
    budget_before_expense = get_budget_for_given_month(
        year=expense.date.year, month=expense.date.month
    )
    budget_after_expense = budget_before_expense.remaining_budget - expense.amount
    if budget_after_expense < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense too large for remaining budget in given month.",
        )
    else:
        decrement_remaining_budget(
            budget=budget_before_expense, decrement=expense.amount
        )
    with open(EXPENSES_PATH, "a") as file:
        writer = csv.writer(file)
        if not os.path.isfile(EXPENSES_PATH) or os.stat(EXPENSES_PATH).st_size == 0:
            writer.writerow(expense.model_dump().keys())
        if expense.category_id in get_all_category_ids():
            writer.writerow(expense.model_dump().values())
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found, pick from existing ones.",
            )

    return expense

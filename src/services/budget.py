import csv
from typing import Optional
from models.budget import Budget
from fastapi import status, HTTPException

BUDGETS_PATH = "data/budgets.csv"


def decrement_remaining_budget(budget: Budget, decrement: float):
    decrement_result = budget.remaining_budget - decrement
    if decrement_result >= 0:
        budget.remaining_budget = decrement_result
        _save_updated_budget(budget)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Balance after decrement must be more than or equal to 0.",
        )


def _save_updated_budget(budget: Budget):
    rows = []
    with open(BUDGETS_PATH, "r") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        for row in reader:
            if not (
                int(row["year"]) == budget.year and int(row["month"]) == budget.month
            ):
                rows.append(row)
    rows.append(budget.model_dump())
    with open(BUDGETS_PATH, "w") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def get_budget_for_given_month(year: int, month: int) -> Optional[Budget]:
    with open(BUDGETS_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["year"]) == year and int(row["month"]) == month:
                return Budget(**row)

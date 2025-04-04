from datetime import datetime

from pydantic import BaseModel, Field


class BudgetBase(BaseModel):
    max_budget: float


class Budget(BudgetBase):
    year: int = Field(ge=datetime.now().year, description="Year must be in the future.")
    month: int = Field(ge=1, le=12, description="Month must be between 1-12.")
    remaining_budget: float = Field(default=0.0, ge=0)
    max_budget: float = Field(gt=0)


from uuid import uuid4, UUID
from datetime import datetime

from sqlmodel import SQLModel, Field


class BudgetBase(SQLModel):
    year: int = Field(
        ge=datetime.now().year, description="Year must be in the future.", index=True
    )
    month: int = Field(
        ge=1, le=12, description="Month must be between 1-12.", index=True
    )
    remaining_budget: float = Field(default=0.0, ge=0)
    max_budget: float = Field(gt=0)


class Budget(BudgetBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

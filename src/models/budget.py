from typing import Optional
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
    max_budget: float = Field(gt=0, index=True)
    is_offline: bool = Field(default=False, index=True)
    owner: Optional[str] = Field(default=None, foreign_key="user.username")


class Budget(BudgetBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    remaining_budget: float = Field(default=0.0, ge=0, index=True)

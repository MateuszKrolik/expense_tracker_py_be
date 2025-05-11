from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class ExpenseBase(SQLModel):
    name: str = Field(index=True)
    amount: float
    category_id: UUID = Field(foreign_key="category.id")
    is_offline: bool = Field(default=False)
    timestamp: date = Field(default_factory=date.today)


class Expense(ExpenseBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner: Optional[str] = Field(default=None, foreign_key="user.username", index=True)

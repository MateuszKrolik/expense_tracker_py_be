from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class ExpenseBase(SQLModel):
    name: str = Field(index=True)
    amount: float
    category_id: UUID = Field(foreign_key="category.id")


class Expense(ExpenseBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    date: datetime = Field(default_factory=datetime.now)

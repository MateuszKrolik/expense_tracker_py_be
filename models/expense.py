from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

from dtos.expense_base import ExpenseBase


class Expense(ExpenseBase):
    id: UUID = Field(default_factory=uuid4)
    name: str
    amount: float
    category_id: UUID
    date: datetime = Field(default_factory=datetime.now)
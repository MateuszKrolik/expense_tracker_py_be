from datetime import datetime
from pydantic import Field, BaseModel
from uuid import UUID, uuid4


class ExpenseBase(BaseModel):
    name: str
    category_id: UUID
    amount: float


class Expense(ExpenseBase):
    id: UUID = Field(default_factory=uuid4)
    name: str
    amount: float
    category_id: UUID
    date: datetime = Field(default_factory=datetime.now)

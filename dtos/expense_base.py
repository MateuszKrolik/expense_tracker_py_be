from pydantic import BaseModel
from uuid import UUID

class ExpenseBase(BaseModel):
    name: str
    category_id: UUID
    amount: float
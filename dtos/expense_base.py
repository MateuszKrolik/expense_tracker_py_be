from pydantic import BaseModel

class ExpenseBase(BaseModel):
    name: str
    category: int
    amount: float
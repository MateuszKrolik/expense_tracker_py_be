from pydantic import BaseModel

class BudgetBase(BaseModel):
    max_budget: float
from typing import Optional
from fastapi import UploadFile
from pydantic import BaseModel

from src.models.expense import ExpenseBase


class ExpenseCreateRequest(BaseModel):
    expense_base: ExpenseBase
    image: Optional[UploadFile] = None

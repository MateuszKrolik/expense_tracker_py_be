from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")


class PagedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
    offset: int
    limit: int

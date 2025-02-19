from uuid import UUID, uuid4

from pydantic import Field

from dtos.category_base import CategoryBase


class Category(CategoryBase):
    id: UUID = Field(default_factory=uuid4)
    name: str
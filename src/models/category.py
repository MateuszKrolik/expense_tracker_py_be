from uuid import UUID, uuid4

from pydantic import Field, BaseModel


class CategoryBase(BaseModel):
    name: str


class Category(CategoryBase):
    id: UUID = Field(default_factory=uuid4)
    name: str


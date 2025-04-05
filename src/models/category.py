from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class CategoryBase(SQLModel):
    name: str = Field(index=True)
    is_offline: bool = Field(default=False)


class Category(CategoryBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

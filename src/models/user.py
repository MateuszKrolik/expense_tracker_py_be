from typing import Optional
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str = Field(primary_key=True)
    email: Optional[str] = Field(default=None, index=True)
    full_name: Optional[str] = Field(default=None, index=True)
    disabled: Optional[bool] = Field(default=None, index=True)


class User(UserBase, table=True):
    hashed_password: str

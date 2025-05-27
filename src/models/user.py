from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str = Field(primary_key=True)
    email: str = Field(index=True)
    full_name: str = Field(index=True)
    disabled: bool = Field(default=False, index=True)


class User(UserBase, table=True):
    __tablename__ = "user"  # explicit naming for pipeline
    hashed_password: str

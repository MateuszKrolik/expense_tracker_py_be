from fastapi import APIRouter, HTTPException, status
from src.decorators.db_exception_handlers import command_exception_handler
from src.models.user import User, UserBase
from src.services.database import SessionDep
from src.services.password import pwd_context


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_user(
    session: SessionDep,
    user_base: UserBase,
    password: str,
):
    return await signup(
        session=session,
        user_base=user_base,
        password=password,
    )


@command_exception_handler
async def signup(
    session: SessionDep,
    user_base: UserBase,
    password: str,
):
    if await session.get(User, user_base.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    user = User(**user_base.model_dump(), hashed_password=pwd_context.hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

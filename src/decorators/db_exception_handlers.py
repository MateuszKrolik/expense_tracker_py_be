from fastapi import HTTPException, status
from functools import wraps
from typing import Callable, Coroutine, Any


def command_exception_handler(func: Callable[..., Coroutine[Any, Any, Any]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session = kwargs.get("session")

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if session:
                await session.rollback()
            raise HTTPException(
                status_code=getattr(
                    e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=str(e),
            )

    return wrapper


def query_exception_handler(func: Callable[..., Coroutine[Any, Any, Any]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            raise HTTPException(
                status_code=getattr(
                    e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=str(e),
            )

    return wrapper

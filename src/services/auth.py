from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    return fake_decode_token(token)


def fake_hash_password(password: str):
    return "fakehashed" + password

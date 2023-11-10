from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.api_models import UserInDB
from service.db_service import get_user_by_username
from utils.constants import (
    INVALID_AUTH_CREDENTIALS_ERROR,
    INACTIVE_OR_INVALID_USER_ERROR,
    INACTIVE_USER_ERROR,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def fake_decode_token(token):
    return UserInDB(username=token, disabled=False, hashed_password="fake")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_AUTH_CREDENTIALS_ERROR,
                            headers={"WWW-Authenticate": "Bearer"})

    user_in_db = get_user_by_username(user.username)
    if not user_in_db or user_in_db.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INACTIVE_OR_INVALID_USER_ERROR)

    user_data = {
        "username": user_in_db.username,
        "hashed_password": user_in_db.hashed_password,
        'disabled': user_in_db.disabled
    }
    return UserInDB(**user_data)


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INACTIVE_USER_ERROR)
    return current_user


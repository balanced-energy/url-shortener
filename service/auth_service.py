from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from service.db_service import get_user_by_id, get_user_by_username, verify_password
from models.db_models import UserInDB
from utils.logger_config import logger
from utils.constants import *


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    logger.info(GET_CURRENT_USER_INFO)
    payload = decode_access_token(token)
    if not payload:
        logger.error(INVALID_CREDENTIALS_ERROR)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS_ERROR,
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        logger.error(INVALID_CREDENTIALS_ERROR)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS_ERROR
        )

    user_in_db = get_user_by_id(user_id)
    if user_in_db is None:
        logger.warning(USER_NOT_FOUND_LOG.format(username=user_id))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INACTIVE_OR_INVALID_USER_ERROR,
        )
    user_data = {
        "user_id": user_in_db.user_id,
        "username": user_in_db.username,
        "url_limit": user_in_db.url_limit,
        "is_admin": user_in_db.is_admin,
        "hashed_password": user_in_db.hashed_password,
        "disabled": user_in_db.disabled,
    }
    return UserInDB(**user_data)


def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    if current_user.disabled:
        logger.warning(INACTIVE_USER_ERROR.format(username=current_user.username))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=INACTIVE_USER_ERROR
        )
    logger.info(GET_ACTIVE_USER_LOG.format(username=current_user.username))
    return current_user


def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(INVALID_CREDENTIALS_ERROR.format(username=username))
        return None
    logger.info(AUTHENTICATION_SUCCESS_LOG.format(username=username))
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.info(CREATE_ACCESS_TOKEN_LOG.format(username=data.get("sub")))
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        logger.info(JWT_DECODE_SUCCESS_LOG)
        return payload
    except JWTError as e:
        logger.error(JWT_DECODE_ERROR_LOG.format(error=e))
        return None

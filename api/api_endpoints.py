from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from models.api_models import URLRequest, User, CreateUserRequest
from service.auth_service import get_current_user
from service.api_service import create_custom_short_url, create_generated_short_url
from service.db_service import get_all_urls, get_original_url, get_user_by_username, fake_hash_password, create_user
from utils.logger_config import logger
from utils.constants import (
    CREATED_CUSTOM_URL_LOG,
    GENERATED_SHORT_URL_LOG,
    ERROR_SHORTEN_URL_LOG,
    RECEIVED_REQUEST_LIST_URLS_LOG,
    RETRIEVED_URLS_LOG,
    ERROR_LIST_URLS_LOG,
    REDIRECT_SUCCESS_LOG,
    REDIRECT_NOT_FOUND,
    UNEXPECTED_ERROR,
    INCORRECT_CREDENTIALS_ERROR,
    USER_CREATION_SUCCESS_MESSAGE,
    ACCESS_TOKEN_TYPE,
    USER_CREATED_LOG,
)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INCORRECT_CREDENTIALS_ERROR)

    hashed_password = fake_hash_password(form_data.password)
    if hashed_password != user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INCORRECT_CREDENTIALS_ERROR)

    return {"access_token": user.username, "token_type": ACCESS_TOKEN_TYPE}


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_data: CreateUserRequest):
    create_user(user_data.username, user_data.password)
    logger.info(USER_CREATED_LOG.format(username=user_data.username))
    return {"message": USER_CREATION_SUCCESS_MESSAGE.format(username=user_data.username)}


@app.post("/shorten_url")
async def shorten_url(request: URLRequest):
    try:
        if request.short_url:
            result = create_custom_short_url(request.url, request.short_url)
            logger.info(CREATED_CUSTOM_URL_LOG.format(short_url=result['short_url']))
            return result

        result = create_generated_short_url(request.url)
        logger.info(GENERATED_SHORT_URL_LOG.format(short_url=result['short_url']))
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Log the unexpected error and raise a generic HTTP exception
        logger.error(ERROR_SHORTEN_URL_LOG.format(error=e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=UNEXPECTED_ERROR.format(error=e))


# [TODO - handle authentication]
@app.get("/list_urls")
async def list_urls():
    logger.debug(RECEIVED_REQUEST_LIST_URLS_LOG)
    try:
        urls = get_all_urls()
        logger.debug(RETRIEVED_URLS_LOG.format(count=len(urls)))
        return urls
    except Exception as e:
        logger.error(ERROR_LIST_URLS_LOG.format(error=e))
        raise


@app.get("/redirect/{short_url}")
async def redirect(short_url: str):
    original_url = get_original_url(short_url)
    if original_url is None:
        # Log as info, because this is an expected situation that doesn't require intervention
        logger.info(REDIRECT_NOT_FOUND.format(short_url=short_url))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=REDIRECT_NOT_FOUND
        )
    # Log the redirect success as info
    logger.info(REDIRECT_SUCCESS_LOG.format(short_url=short_url, original_url=original_url))
    response = RedirectResponse(url=original_url)
    response.headers["X-Original-URL"] = original_url
    return response


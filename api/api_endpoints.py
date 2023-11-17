from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from models.api_models import (
    URLRequest,
    CreateUserRequest,
    Token,
    UpdateUrlLimitRequest,
)
from models.db_models import User, UserInDB
from service.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
)
from service.api_service import create_custom_short_url, create_generated_short_url
from service.db_service import *
from utils.constants import *

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    logger.info(READ_USERS_ME_LOG.format(username=current_user.username))
    return current_user


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(LOGIN_ATTEMPT_LOG.format(username=form_data.username))
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(INVALID_CREDENTIALS_ERROR.format(username=form_data.username))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS_ERROR
        )

    access_token_expires = timedelta(minutes=JWT_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    logger.info(CREATE_ACCESS_TOKEN_LOG.format(username=form_data.username))
    return {"access_token": access_token, "token_type": ACCESS_TOKEN_TYPE}


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_data: CreateUserRequest):
    create_user(user_data.username, user_data.password, user_data.admin)
    logger.info(USER_CREATED_LOG.format(username=user_data.username))
    return {
        "message": USER_CREATION_SUCCESS_MESSAGE.format(username=user_data.username)
    }


@app.post("/change_password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: UserInDB = Depends(get_current_user),
):
    logger.info(PASSWORD_CHANGE_REQUEST_LOG.format(user_id=current_user.username))
    user = get_user_by_id(current_user.user_id)
    if not user or not verify_password(old_password, user.hashed_password):
        logger.warning(ACCESS_DENIED)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ACCESS_DENIED
        )

    update_user_password(current_user.user_id, new_password)
    logger.info(PASSWORD_CHANGE_SUCCESS_LOG.format(user_id=current_user.username))
    return {"message": PASSWORD_CHANGE_SUCCESS_LOG.format(user_id=current_user.user_id)}


@app.post("/shorten_url")
async def shorten_url(
    request: URLRequest, current_user: UserInDB = Depends(get_current_user)
):
    try:
        # If short_url is given use it, otherwise generate a unique url and save it
        if request.short_url:
            result = create_custom_short_url(
                request.url, request.short_url, current_user.user_id
            )
            logger.info(CREATED_CUSTOM_URL_LOG.format(short_url=result["short_url"]))
            return result
        else:
            result = create_generated_short_url(request.url, current_user.user_id)
            logger.info(GENERATED_SHORT_URL_LOG.format(short_url=result["short_url"]))
            return result
    except HTTPException:
        # Raise any exceptions
        raise
    except Exception as e:
        logger.error(ERROR_SHORTEN_URL_LOG.format(error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(error=e),
        )


@app.get("/list_urls")
async def list_urls(current_user: User = Depends(get_current_user)):
    if not is_user_admin(current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ACCESS_DENIED)

    logger.debug(RECEIVED_REQUEST_LIST_URLS_LOG)
    try:
        urls = get_all_urls()
        logger.debug(RETRIEVED_URLS_LOG.format(count=len(urls)))
        return urls
    except Exception as e:
        logger.error(ERROR_LIST_URLS_LOG.format(error=e))
        raise


@app.get("/list_my_urls")
async def list_my_urls(current_user: User = Depends(get_current_active_user)):
    user_urls = get_urls_for_user(current_user.user_id)
    return user_urls


@app.post("/update_url_limit")
async def update_url_limit(
    request: UpdateUrlLimitRequest, current_user: UserInDB = Depends(get_current_user)
):
    # Ensure the current user is an admin
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ACCESS_DENIED)

    # Fetch the user to update
    user_to_update = get_user_by_id(request.user_id)
    if user_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_LOG.format(username=current_user.user_id),
        )

    # Get user's url info: limit and current count
    user_url_info = get_user_url_info(current_user.user_id)

    # Make sure new limit is greater than current url count
    if request.new_limit < user_url_info[URL_COUNT_KEY]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=UPDATE_URL_LIMIT_ERROR
        )

    # Update the user's URL limit
    user_to_update.url_limit = request.new_limit
    user_to_update.save()

    return {"message": UPDATE_URL_LIMIT_SUCCESS.format(user_id=user_to_update.user_id)}


@app.get("/redirect/{short_url}")
async def redirect(short_url: str):
    original_url = get_original_url(short_url)
    if original_url is None:
        # Log as info, because this is an expected situation that doesn't require intervention
        logger.info(REDIRECT_NOT_FOUND.format(short_url=short_url))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=REDIRECT_NOT_FOUND.format(short_url=short_url),
        )
    # Log the redirect success as info
    logger.info(
        REDIRECT_SUCCESS_LOG.format(short_url=short_url, original_url=original_url)
    )
    response = RedirectResponse(url=original_url)
    response.headers["X-Original-URL"] = original_url
    return response

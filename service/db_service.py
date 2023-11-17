from fastapi import HTTPException, status
from pynamodb.exceptions import PutError, DoesNotExist, PynamoDBConnectionError
from passlib.context import CryptContext
from models.db_models import URLModel, UserModel
from utils.logger_config import logger
from utils.constants import *
import traceback

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def save_url(url: str, short_url: str, user_id: str) -> bool:
    try:
        if url_limit_check(user_id):
            logger.warning(URL_LIMIT_REACHED_LOG.format(username=user_id))
            # Url limit reached
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=URL_LIMIT_REACHED_LOG.format(username=user_id),
            )
        # Directly use the provided data to create a new URLModel instance,
        # Object of type Url is not JSON serializable so cast url as string
        new_url = URLModel(short_url=short_url, url=str(url), user_id=user_id)
        # Save the new URLModel instance with a condition to ensure uniqueness of the short URL
        new_url.save(condition=URLModel.short_url.does_not_exist())

        logger.info(SAVED_URL_LOG.format(url=url, short_url=short_url))
        return True
    except PutError as e:
        # Checks if conditional save failed due to database already containing that short_url
        if "ConditionalCheckFailedException" in str(e):
            logger.warning(SHORT_URL_EXISTS_WARNING.format(short_url=short_url))
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=SHORT_URL_EXISTS_WARNING.format(short_url=short_url),
            )
        # Raise any other PutError that isn't the result of a conflicting short_url
        else:
            logger.error(UNEXPECTED_ERROR.format(error=e))
            raise
    except PynamoDBConnectionError:
        logger.error(DATABASE_UNREACHABLE_ERROR)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNREACHABLE_ERROR,
        )


def get_original_url(short_url: str):
    try:
        url_item = URLModel.get(hash_key=short_url)
        logger.info(RETRIEVED_ORIGINAL_URL_LOG.format(short_url=short_url))
        return url_item.url
    except DoesNotExist:
        logger.info(SHORT_URL_NOT_EXIST_LOG.format(short_url=short_url))
        # Return None to indicate short_url not found
        return None
    except Exception as e:
        logger.exception(UNEXPECTED_ERROR.format(error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_RETRIEVING_ALL_URLS_LOG.format(error=e),
        )


def get_all_urls():
    try:
        urls = [item for item in URLModel.scan()]
        logger.info(RETRIEVED_ALL_URLS_LOG)
        return [
            {"short_url": item.short_url, "original_url": item.url} for item in urls
        ]
    except Exception as e:
        logger.exception(ERROR_RETRIEVING_ALL_URLS_LOG.format(error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(error=e),
        )


def create_user(username: str, password: str, admin: bool):
    try:
        hashed_password = hash_password(password)
        new_user = UserModel(
            username=username, hashed_password=hashed_password, is_admin=admin
        )
        new_user.save()
        logger.info(USER_CREATED_LOG.format(username=username))
    except Exception as e:
        logger.error(USER_CREATION_FAILURE_LOG.format(username=username, error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(error=e),
        )


def get_user_by_username(username: str):
    try:
        # Query the GSI for the user with the matching username
        matching_users = UserModel.username_index.query(username)

        # Attempt to get the first result from the query
        user = next(matching_users, None)
        if user is None:
            logger.info(USER_NOT_FOUND_LOG.format(username=username))
            return None

        logger.info(USER_RETRIEVED_LOG.format(user_id=username))
        return user
    except UserModel.DoesNotExist:
        logger.info(USER_NOT_FOUND_LOG.format(username=username))
        return None
    except Exception as e:
        logger.error(UNEXPECTED_ERROR.format(error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(error=e),
        )


def get_user_by_id(user_id: str):
    try:
        logger.info(f"Getting current user by user_id:{user_id}")
        user = UserModel.get(user_id)
        logger.info(USER_RETRIEVED_LOG.format(user_id=user_id))
        return user
    except DoesNotExist:
        logger.info(USER_NOT_FOUND_LOG.format(username=user_id))
        return None
    except Exception as e:
        trace = traceback.format_exc()
        logger.error(f"Unexpected error occurred: {e}, Trace: {trace}")
        logger.error(UNEXPECTED_ERROR.format(error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(error=e),
        )


def is_user_admin(user_id: str) -> bool:
    try:
        user = UserModel.get(user_id)
        return user.is_admin
    except UserModel.DoesNotExist:
        logger.error(USER_NOT_FOUND_LOG.format(username=user_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_LOG.format(username=user_id),
        )
    except Exception as e:
        logger.error(UNEXPECTED_ERROR.format(username=user_id, error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(username=user_id, error=e),
        )


def update_user_password(user_id: str, new_password: str):
    try:
        user = UserModel.get(user_id)
        hashed_password = hash_password(new_password)
        user.hashed_password = hashed_password
        user.save()
        logger.info(PASSWORD_UPDATED_LOG.format(username=user_id))
    except UserModel.DoesNotExist:
        logger.error(USER_NOT_FOUND_LOG.format(username=user_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_LOG.format(username=user_id),
        )
    except PynamoDBConnectionError:
        logger.error(DATABASE_UNREACHABLE_ERROR)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNREACHABLE_ERROR,
        )
    except Exception as e:
        logger.error(UNEXPECTED_ERROR.format(error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(error=e),
        )


def get_urls_for_user(user_id: str):
    try:
        logger.info(RETRIEVING_USER_URLS_LOG.format(user_id=user_id))
        # Fetch the current URLs associated with the user
        urls = list(URLModel.user_id_index.query(user_id))

        return [
            {"short_url": item.short_url, "original_url": item.url} for item in urls
        ]
    except DoesNotExist:
        logger.info(USER_NOT_FOUND_LOG.format(username=user_id))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_LOG.format(username=user_id),
        )
    except PynamoDBConnectionError:
        logger.error(DATABASE_UNREACHABLE_ERROR)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNREACHABLE_ERROR,
        )
    except Exception as e:
        logger.error(UNEXPECTED_ERROR.format(user_id=user_id, error=e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR.format(error=e),
        )


def get_user_url_info(user_id: str):
    try:
        user = UserModel.get(user_id)
        # Fetch the current URLs associated with the user
        user_urls = list(URLModel.user_id_index.query(user_id))

        logger.info(USER_URL_INFO_FETCHED_SUCCESS)

        # Return the URL limit and the current URL count
        return {URL_LIMIT_KEY: user.url_limit, URL_COUNT_KEY: len(user_urls)}
    except UserModel.DoesNotExist:
        error_msg = USER_NOT_FOUND_LOG.format(username=user_id)
        logger.error(error_msg)
        raise HTTPException(status_code=404, detail=error_msg)
    except Exception as e:
        error_msg = UNEXPECTED_ERROR.format(user_id=user_id, error=e)
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


def url_limit_check(user_id: str) -> bool:
    user_url_info = get_user_url_info(user_id)
    url_limit = user_url_info[URL_LIMIT_KEY]
    url_count = user_url_info[URL_COUNT_KEY]
    # Log the URL limit check
    logger.info(
        URL_LIMIT_CHECK.format(
            user_id=user_id, url_limit=url_limit, url_count=url_count
        )
    )
    return url_limit <= url_count

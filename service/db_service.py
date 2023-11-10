from fastapi import HTTPException, status
from pynamodb.exceptions import PutError, DoesNotExist, PynamoDBConnectionError
from models.db_models import URLModel, URLModelPydantic, UserModel
from utils.logger_config import logger
from utils.constants import (
    SAVED_URL_LOG,
    SHORT_URL_EXISTS_WARNING,
    UNEXPECTED_ERROR,
    DATABASE_UNREACHABLE_ERROR,
    RETRIEVED_ORIGINAL_URL_LOG,
    SHORT_URL_NOT_EXIST_LOG,
    RETRIEVED_ALL_URLS_LOG,
    ERROR_RETRIEVING_ALL_URLS_LOG,
    USER_CREATION_SUCCESS_LOG,
    USER_CREATION_FAILURE_LOG,
    USER_RETRIEVAL_LOG,
    USER_NOT_FOUND_LOG
)


def save_url(url: str, short_url: str) -> bool:
    try:
        validated_data = URLModelPydantic(url=str(url), short_url=short_url)
        URLModel(short_url=validated_data.short_url, url=validated_data.url).save(URLModel.short_url.does_not_exist())
        logger.info(SAVED_URL_LOG.format(url=url, short_url=short_url))
        return True
    except PutError as e:
        if "ConditionalCheckFailedException" in str(e):
            logger.warning(SHORT_URL_EXISTS_WARNING.format(short_url=short_url))
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=SHORT_URL_EXISTS_WARNING.format(short_url=short_url))
        # Raise any other PutError that isn't the result of a conflicting short_url
        else:
            logger.error(UNEXPECTED_ERROR.format(error=e))
            raise
    except PynamoDBConnectionError:
        logger.error(DATABASE_UNREACHABLE_ERROR)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=DATABASE_UNREACHABLE_ERROR)
    except Exception as e:
        logger.exception(UNEXPECTED_ERROR.format(error=e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=UNEXPECTED_ERROR.format(error=e))


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=ERROR_RETRIEVING_ALL_URLS_LOG.format(error=e))


def get_all_urls():
    try:
        urls = [item for item in URLModel.scan()]
        logger.info(RETRIEVED_ALL_URLS_LOG)
        return [{"short_url": item.short_url, "original_url": item.url} for item in urls]
    except Exception as e:
        logger.exception(ERROR_RETRIEVING_ALL_URLS_LOG.format(error=e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=UNEXPECTED_ERROR.format(error=e))


def create_user(username: str, password: str):
    try:
        hashed_password = fake_hash_password(password)
        new_user = UserModel(
            username=username,
            hashed_password=hashed_password,
        )
        new_user.save()
        logger.info(USER_CREATION_SUCCESS_LOG.format(username=username))
    except Exception as e:
        logger.error(USER_CREATION_FAILURE_LOG.format(username=username, error=e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=UNEXPECTED_ERROR.format(error=e))


def get_user_by_username(username: str):
    try:
        user = UserModel.get(username)
        logger.info(USER_RETRIEVAL_LOG.format(username=username))
        return user
    except UserModel.DoesNotExist:
        logger.info(USER_NOT_FOUND_LOG.format(username=username))
        return None
    except Exception as e:
        logger.error(UNEXPECTED_ERROR.format(error=e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=UNEXPECTED_ERROR.format(error=e))


def fake_hash_password(password: str) -> str:
    return "fakehashed" + password

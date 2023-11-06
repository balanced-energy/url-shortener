from pynamodb.exceptions import PutError, DoesNotExist, PynamoDBConnectionError
from models.db_models import URLModel, URLModelPydantic
from fastapi.exceptions import HTTPException
from logger_config import logger
from constants import (
    SAVED_URL_LOG,
    SHORT_URL_EXISTS_WARNING,
    UNEXPECTED_ERROR,
    DATABASE_UNREACHABLE_ERROR,
    RETRIEVED_ORIGINAL_URL_LOG,
    SHORT_URL_NOT_EXIST_LOG,
    RETRIEVED_ALL_URLS_LOG,
    ERROR_RETRIEVING_ALL_URLS_LOG,
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
            raise HTTPException(status_code=409, detail=SHORT_URL_EXISTS_WARNING.format(short_url=short_url))
        # Raise any other PutError that isn't the result of a conflicting short_url
        else:
            logger.error(UNEXPECTED_ERROR.format(error=e))
            raise
    except PynamoDBConnectionError:
        logger.error(DATABASE_UNREACHABLE_ERROR)
        raise HTTPException(status_code=503, detail=DATABASE_UNREACHABLE_ERROR)
    except Exception as e:
        logger.exception(UNEXPECTED_ERROR.format(error=e))
        raise HTTPException(status_code=500, detail=UNEXPECTED_ERROR.format(error=e))


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
        raise HTTPException(status_code=500, detail=UNEXPECTED_ERROR.format(error=e))


def get_all_urls():
    try:
        urls = [item for item in URLModel.scan()]
        logger.info(RETRIEVED_ALL_URLS_LOG)
        return [{"short_url": item.short_url, "original_url": item.url} for item in urls]
    except Exception as e:
        logger.exception(ERROR_RETRIEVING_ALL_URLS_LOG.format(error=e))
        raise HTTPException(status_code=500, detail=ERROR_RETRIEVING_ALL_URLS_LOG.format(error=e))
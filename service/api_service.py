import uuid
from fastapi.exceptions import HTTPException
from .db_service import save_url
from logger_config import logger
from constants import (
    BASE_URL,
    SHORT_URL_EXISTS_WARNING,
    CREATED_CUSTOM_URL_LOG,
    GENERATED_SHORT_URL_LOG,
    ERROR_MAX_RETRIES
)

# Use the local server address


def generate_short_url() -> str:
    # Generate a UUID and remove hyphens, take first 10 characters and combine with Base Url
    return BASE_URL + str(uuid.uuid4()).replace("-", "")[:10]


def create_custom_short_url(url: str, custom_short_url: str) -> dict:
    if not save_url(url, custom_short_url):
        logger.warning(SHORT_URL_EXISTS_WARNING.format(short_url=custom_short_url))
        raise HTTPException(status_code=404, detail=SHORT_URL_EXISTS_WARNING.format(short_url=custom_short_url))
    logger.info(CREATED_CUSTOM_URL_LOG.format(short_url=custom_short_url))
    return {"short_url": custom_short_url}


def create_generated_short_url(url: str) -> dict:
    max_retries = 5
    for i in range(max_retries):
        short_url = generate_short_url()
        if save_url(url, short_url):
            logger.info(GENERATED_SHORT_URL_LOG.format(short_url=short_url))
            return {"short_url": short_url}
    logger.error(ERROR_MAX_RETRIES)
    raise HTTPException(status_code=400, detail=ERROR_MAX_RETRIES)
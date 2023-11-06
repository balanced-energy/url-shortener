import uuid
from fastapi.exceptions import HTTPException
from .db_service import save_url
from logger_config import logger
from constants import (
    SHORT_URL_EXISTS_WARNING,
    CREATED_CUSTOM_URL_LOG,
    GENERATED_SHORT_URL_LOG,
    ERROR_MAX_RETRIES
)


def generate_short_url_id() -> str:
    # Generate a UUID and remove hyphens, take first 10 characters and combine with Base Url
    return str(uuid.uuid4()).replace("-", "")[:10]


def create_custom_short_url(url: str, custom_short_url: str) -> dict:
    if not save_url(url, custom_short_url):
        logger.warning(SHORT_URL_EXISTS_WARNING.format(short_url=custom_short_url))
        raise HTTPException(status_code=409, detail=SHORT_URL_EXISTS_WARNING.format(short_url=custom_short_url))
    logger.info(CREATED_CUSTOM_URL_LOG.format(short_url=custom_short_url))
    return {"short_url": custom_short_url}


def create_generated_short_url(url: str) -> dict:
    max_retries = 5
    for _ in range(max_retries):
        try:
            short_url_id = generate_short_url_id()
            save_url(url, short_url_id)
            logger.info(GENERATED_SHORT_URL_LOG.format(short_url=short_url_id))
            return {"short_url": short_url_id}
        except HTTPException as http_exc:
            if http_exc.status_code != 409:
                # If the HTTPException is not a conflict, it's unexpected, so re-raise it.
                raise
    # If we reach this point, we've exhausted the maximum number of retries.
    logger.error(ERROR_MAX_RETRIES)
    raise HTTPException(status_code=400, detail=ERROR_MAX_RETRIES)

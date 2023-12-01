import uuid
from fastapi import HTTPException, status
from .db_service import save_url
from utils.logger_config import logger
from utils.constants import *


def generate_short_url_id() -> str:
    # Generate a UUID and remove hyphens, take first 10 characters and combine with Base Url
    return str(uuid.uuid4()).replace("-", "")[:10]


def create_custom_short_url(url: str, custom_short_url: str, user_id: str) -> dict:
    try:
        save_url(url, custom_short_url, user_id)
        logger.info(CREATED_CUSTOM_URL_LOG.format(short_url=custom_short_url))
        return {"short_url": custom_short_url}
    except HTTPException:
        raise


def create_generated_short_url(url: str, user_id: str) -> dict:
    max_retries = 5
    for _ in range(max_retries):
        try:
            short_url_id = generate_short_url_id()
            save_url(url, short_url_id, user_id)
            logger.info(GENERATED_SHORT_URL_LOG.format(short_url=short_url_id))
            return {"short_url": short_url_id}
        except HTTPException as http_exc:
            # Not a conflict, unexpected error
            if http_exc.status_code != status.HTTP_409_CONFLICT:
                raise
    # If we reach this point, we've exhausted the maximum number of retries.
    logger.error(ERROR_MAX_RETRIES)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MAX_RETRIES
    )

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import RedirectResponse
from pynamodb.exceptions import DoesNotExist
from models.api_models import URLRequest
from service.api_service import create_custom_short_url, create_generated_short_url
from service.db_service import get_all_urls, get_original_url
from logger_config import logger
from constants import (
    CREATED_CUSTOM_URL_LOG,
    GENERATED_SHORT_URL_LOG,
    ERROR_SHORTEN_URL_LOG,
    RECEIVED_REQUEST_LIST_URLS_LOG,
    RETRIEVED_URLS_LOG,
    ERROR_LIST_URLS_LOG,
    REDIRECT_SUCCESS_LOG,
    REDIRECT_NOT_FOUND_LOG,
    UNEXPECTED_ERROR_LOG,
)

app = FastAPI()


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
    except Exception as e:
        logger.error(ERROR_SHORTEN_URL_LOG.format(error=e))
        raise


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
    print(f'redirect endpoint')
    try:
        # Attempt to retrieve the item from the database
        original_url = get_original_url(short_url)
        logger.info(REDIRECT_SUCCESS_LOG.format(short_url=short_url, original_url=original_url))
        response = RedirectResponse(url=original_url)
        response.headers["X-Original-URL"] = original_url
        return response
    except DoesNotExist:
        logger.warning(REDIRECT_NOT_FOUND_LOG.format(short_url=short_url))
        raise HTTPException(
            status_code=404,
            detail=f'No URL for "{short_url}" found'
        )
    except Exception as e:
        logger.exception(UNEXPECTED_ERROR_LOG.format(error=e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


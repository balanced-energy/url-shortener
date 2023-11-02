from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pynamodb.exceptions import DoesNotExist
from models.db_models import URLModel
from models.api_models import URLRequest
from service.url_service import create_custom_short_url, create_generated_short_url
from service.db_service import get_all_urls
app = FastAPI()


@app.post("/shorten_url")
async def shorten_url(request: URLRequest):
    if request.short_url:
        return create_custom_short_url(request.url, request.short_url)

    # If no custom short_url is provided, generate one
    return create_generated_short_url(request.url)


# [TODO - handle authentication]
@app.get("/list_urls")
async def list_urls():
    return get_all_urls()


# Define the redirect endpoint
@app.get("/redirect/{short_url}", response_model=None)
async def redirect(short_url: str):
    try:
        # Attempt to retrieve the item from the database
        item = URLModel.get(short_url)
        return RedirectResponse(url=item.url)
    except DoesNotExist:
        # If the item does not exist, return a 404 error
        raise HTTPException(
            status_code=404,
            detail=f'No URL for "{short_url}" found'
        )
    except Exception as e:
        # If any other exception occurred, return a 500 error
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )

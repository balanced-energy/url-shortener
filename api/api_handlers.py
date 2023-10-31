from fastapi import FastAPI, HTTPException
from models.api_models import URLRequest
from service.url_service import create_custom_short_url, create_generated_short_url

app = FastAPI()


@app.post("/shorten_url")
async def shorten_url(request: URLRequest):
    if request.short_url:
        return create_custom_short_url(request.url, request.short_url)

    # If no custom short_url is provided, generate one
    return create_generated_short_url(request.url)

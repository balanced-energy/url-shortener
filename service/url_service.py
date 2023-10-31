import uuid
from fastapi.exceptions import HTTPException
from .db_service import save_url


# Use the local server address to see redirection during testing with Postman
BASE_URL = "http://localhost:8000/"
ERROR_MAX_RETRIES = 'Max retries reached. Unable to create short URL.'


def generate_short_url() -> str:
    # Generate a UUID and remove hyphens
    uuid_str = str(uuid.uuid4()).replace("-", "")
    # Take first 6 characters of the UUID to create a shorter URL identifier
    short_url_identifier = uuid_str[:6]
    # Combine with the base URL to form a complete URL
    full_short_url = BASE_URL + short_url_identifier
    return full_short_url


def create_custom_short_url(url: str, custom_short_url: str) -> dict:
    if not save_url(url, custom_short_url):
        raise HTTPException(status_code=404, detail=f"Short URL '{custom_short_url}' already exists.")
    return {"short_url": custom_short_url}


def create_generated_short_url(url: str) -> dict:
    max_retries = 5
    for i in range(max_retries):
        short_url = generate_short_url()
        if save_url(url, short_url):
            return {"short_url": short_url}
    raise HTTPException(status_code=400, detail=ERROR_MAX_RETRIES)
from pydantic import BaseModel, HttpUrl
from typing import Optional


# Define a pydantic model for request and response
class URLRequest(BaseModel):
    url: HttpUrl
    short_url: Optional[str] = None



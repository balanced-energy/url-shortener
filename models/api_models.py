from pydantic import BaseModel, HttpUrl, constr, field_validator, Field
from typing import Optional


# Define a pydantic model for request and response
class URLRequest(BaseModel):
    url: HttpUrl
    # Specify the maximum length allowed for custom short URLs
    short_url: Optional[constr(max_length=50)] = None

    @field_validator("url")
    def validate_url_length(cls, value):
        max_length = 2048
        if len(value.__str__()) > max_length:
            raise ValueError(f"URL must be {max_length} characters or less")
        return value


class CreateUserRequest(BaseModel):
    username: str
    password: str
    admin: bool = Field(bool=False)


class Token(BaseModel):
    access_token: str
    token_type: str


class UpdateUrlLimitRequest(BaseModel):
    user_id: str
    new_limit: int

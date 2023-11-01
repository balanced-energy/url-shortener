from pynamodb.exceptions import PutError
from models.db_models import URLModel, URLModelPydantic
from fastapi.exceptions import HTTPException


def save_url(url: str, short_url: str) -> bool:
    try:
        # Http object can't be serialized, need to save it as a string
        url_str = str(url)
        validated_data = URLModelPydantic(url=url_str, short_url=short_url)
        URLModel(short_url=validated_data.short_url, url=validated_data.url).save(URLModel.short_url.does_not_exist())
        return True
    except PutError as e:
        # short_url already exists in URLs table
        if "ConditionalCheckFailedException" in str(e):
            return False
        # Another error occurred
        raise e


def get_all_urls():
    """
    Fetch all URLs from the DynamoDB table.
    """
    urls = []
    try:
        for item in URLModel.scan():
            urls.append({
                "short_url": item.short_url,
                "original_url": item.url
            })
    except Exception as e:
        # Handle other unforeseen exceptions
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    return urls

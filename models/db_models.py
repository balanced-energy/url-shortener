from pydantic import BaseModel, HttpUrl
from decouple import config
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute
from pynamodb.connection.base import Connection


# Keys in .env file
AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"
AWS_REGION = "AWS_REGION"


class URLModelPydantic(BaseModel):
    short_url: str
    url: str


# Pynamo Models for Dynamo DB Tables

# Configure PynamoDB to use your AWS credentials and region
Connection.AWS_ACCESS_KEY_ID = config(AWS_ACCESS_KEY_ID)
Connection.AWS_SECRET_ACCESS_KEY = config(AWS_SECRET_ACCESS_KEY)
Connection.AWS_REGION = config(AWS_REGION)


class URLModel(Model):
    """
    A DynamoDB URL table
    """

    class Meta:
        table_name = "URLs"

    # Primary Key (Hash Key)
    short_url = UnicodeAttribute(hash_key=True)
    url = UnicodeAttribute()


# Table creation
try:
    if not URLModel.exists():
        URLModel.create_table(read_capacity_units=5, write_capacity_units=5, wait=True)
except Exception as e:
    print(f"Error creating tables: {e}")

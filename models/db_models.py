from pydantic import BaseModel
from decouple import config
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute
from pynamodb.connection.base import Connection
from utils.logger_config import logger
from utils.constants import (
    DYNAMODB_TABLE_CREATION_SUCCESS_LOG,
    DYNAMODB_TABLE_CREATION_ERROR_LOG,
)


class URLModelPydantic(BaseModel):
    short_url: str
    url: str


# Pynamo Models for Dynamo DB Tables

# Configure PynamoDB to use your AWS credentials and region
Connection.AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
Connection.AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
Connection.AWS_REGION = config('AWS_REGION')


class URLModel(Model):
    """
    A DynamoDB URL table
    """

    class Meta:
        table_name = "URLs"

    # Primary Key (Hash Key)
    short_url = UnicodeAttribute(hash_key=True)
    url = UnicodeAttribute()


class UserModel(Model):
    """
    A DynamoDB User table
    """

    class Meta:
        table_name = "Users"

    username = UnicodeAttribute(hash_key=True)
    hashed_password = UnicodeAttribute()
    disabled = BooleanAttribute(default=True)


# Table creation
try:
    if not URLModel.exists():
        URLModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        logger.info(DYNAMODB_TABLE_CREATION_SUCCESS_LOG.format(table_name=URLModel.Meta.table_name))
    if not UserModel.exists():
        UserModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        logger.info(DYNAMODB_TABLE_CREATION_SUCCESS_LOG.format(table_name=UserModel.Meta.table_name))
except Exception as e:
    logger.exception(DYNAMODB_TABLE_CREATION_ERROR_LOG.format(error=e))

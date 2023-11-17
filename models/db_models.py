from pydantic import BaseModel, Field
from decouple import config
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, NumberAttribute
from pynamodb.connection.base import Connection
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
import uuid
from utils.logger_config import logger
from utils.constants import (
    DYNAMODB_TABLE_CREATION_SUCCESS_LOG,
    DYNAMODB_TABLE_CREATION_ERROR_LOG,
)


# Creates new User ID
def generate_uuid():
    return str(uuid.uuid4())


# Pydantic Models for database
class URLModelPydantic(BaseModel):
    short_url: str
    url: str


# Model shown to users
class User(BaseModel):
    username: str
    user_id: str
    url_limit: int = 3
    is_admin: bool = False


# Hides sensitive data from users
class UserInDB(User):
    hashed_password: str
    disabled: bool = Field(bool=False)


# Pynamo Models for Dynamo DB Tables
# Configure PynamoDB to use your AWS credentials and region
Connection.AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
Connection.AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
Connection.AWS_REGION = config("AWS_REGION")


class URLModel(Model):
    """
    A DynamoDB URL table
    """

    class Meta:
        table_name = "URLs"

    # Primary Key (Hash Key)
    short_url = UnicodeAttribute(hash_key=True)
    url = UnicodeAttribute()
    user_id = UnicodeAttribute()

    # GSI for querying by user_id
    class UserIdIndex(GlobalSecondaryIndex):
        class Meta:
            index_name = "UserIdIndex"
            read_capacity_units = 1
            write_capacity_units = 1
            projection = AllProjection()

        user_id = UnicodeAttribute(hash_key=True)

    user_id_index = UserIdIndex()


class UserModel(Model):
    """
    A DynamoDB User table
    """

    class Meta:
        table_name = "Users"

    user_id = UnicodeAttribute(hash_key=True, default_for_new=generate_uuid, null=False)
    username = UnicodeAttribute()
    url_limit = NumberAttribute(default=3)
    hashed_password = UnicodeAttribute()
    is_admin = BooleanAttribute(default=False)
    disabled = BooleanAttribute(default=False)

    # GSI for querying by username
    class UsernameIndex(GlobalSecondaryIndex):
        class Meta:
            index_name = "UsernameIndex"
            read_capacity_units = 1
            write_capacity_units = 1
            projection = AllProjection()

        # Hash key for the GSI
        username = UnicodeAttribute(hash_key=True)

    # Reference to the GSI
    username_index = UsernameIndex()


# Table creation
try:
    if not URLModel.exists():
        URLModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        logger.info(
            DYNAMODB_TABLE_CREATION_SUCCESS_LOG.format(
                table_name=URLModel.Meta.table_name
            )
        )
    if not UserModel.exists():
        UserModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        logger.info(
            DYNAMODB_TABLE_CREATION_SUCCESS_LOG.format(
                table_name=UserModel.Meta.table_name
            )
        )
except Exception as e:
    logger.exception(DYNAMODB_TABLE_CREATION_ERROR_LOG.format(error=e))

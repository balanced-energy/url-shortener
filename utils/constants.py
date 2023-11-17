from decouple import config

# API endpoints
READ_USERS_ME_LOG = "Fetching user data for user: {username}"
CREATED_CUSTOM_URL_LOG = "Created custom short URL: {short_url}"
GENERATED_SHORT_URL_LOG = "Generated short URL: {short_url}"
ERROR_SHORTEN_URL_LOG = "Error in shorten_url: {error}"
RECEIVED_REQUEST_LIST_URLS_LOG = "Received request to list all URLs."
RETRIEVED_URLS_LOG = "Retrieved {count} URLs."
ERROR_LIST_URLS_LOG = "Error in list_urls: {error}"
REDIRECT_SUCCESS_LOG = "Redirect successful: {short_url} -> {original_url}"
REDIRECT_NOT_FOUND = "Redirect failed: No URL for '{short_url}' found"
URL_LIMIT_REACHED_LOG = "URL Limit reached for user ID: {username}"
UPDATE_URL_LIMIT_ERROR = "New limit cannot be lower than the current number of URLs"
UPDATE_URL_LIMIT_SUCCESS = "URL limit updated successfully for user ID: {user_id}."

# api_service.py
SHORT_URL_EXISTS_WARNING = "Short URL '{short_url}' already exists."
ERROR_MAX_RETRIES = "Max retries reached. Unable to create short URL."

# Database
DYNAMODB_TABLE_CREATION_SUCCESS_LOG = (
    "DynamoDB table '{table_name}' created successfully."
)
DYNAMODB_TABLE_CREATION_ERROR_LOG = "Error creating DynamoDB table: {error}"
DATABASE_UNREACHABLE_ERROR = "Database is currently unreachable."
SAVED_URL_LOG = "Saved URL: {url} with short URL: {short_url}"
UNEXPECTED_ERROR = "Unexpected error occurred: {error}"
RETRIEVED_ALL_URLS_LOG = "Retrieved all URLs from the database."
ERROR_RETRIEVING_ALL_URLS_LOG = "Error retrieving all URLs: {error}"
RETRIEVED_ORIGINAL_URL_LOG = "Retrieved original URL for short URL: {short_url}"
SHORT_URL_NOT_EXIST_LOG = "Short URL does not exist"
USER_RETRIEVED_LOG = "Retrieved user: {user_id}"
USER_NOT_FOUND_LOG = "User not found: {username}"
USER_CREATED_LOG = "Successfully created user: {username}"
USER_CREATION_FAILURE_LOG = "Failed to create user: {username}, error: {error}"
PASSWORD_UPDATED_LOG = "Successfully updated password"
RETRIEVING_USER_URLS_LOG = "Retrieving URLs for user: {user_id}"
USER_URL_INFO_FETCHED_SUCCESS = "User URL info fetched successfully."
URL_LIMIT_CHECK = "Checking URL limit for user: {user_id}, URL Limit: {url_limit}, URL Count: {url_count}"

# Authentication
LOGIN_ATTEMPT_LOG = "Attempting login for user: {username}"
INVALID_CREDENTIALS_ERROR = "Incorrect username or password"
INACTIVE_OR_INVALID_USER_ERROR = "Inactive or invalid user"
INACTIVE_USER_ERROR = "Inactive user"
USER_CREATION_SUCCESS_MESSAGE = "User: '{username}' created successfully."
ACCESS_DENIED = "Access denied"
AUTHENTICATION_SUCCESS_LOG = "User authenticated successfully: {username}"
JWT_DECODE_ERROR_LOG = "JWT decoding error: {error}"
JWT_DECODE_SUCCESS_LOG = "JWT decoded successfully"
GET_CURRENT_USER_INFO = "Getting current user"
GET_ACTIVE_USER_LOG = "Retrieved active user: {username}"
CREATE_ACCESS_TOKEN_LOG = "Created access token for user: {username}"
PASSWORD_CHANGE_REQUEST_LOG = "Password change request for user: {user_id}"
PASSWORD_CHANGE_SUCCESS_LOG = "Password changed successfully for user: {user_id}"

# Token data constants
ACCESS_TOKEN_TYPE = "bearer"
JWT_SECRET_KEY = config("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_TOKEN_EXPIRE_MINUTES = 30

# URL info limit keys for get_user_url_info output
URL_LIMIT_KEY = "url_limit"
URL_COUNT_KEY = "current_url_count"

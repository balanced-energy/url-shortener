# Logging messages organized by module use
# api_endpoints.py
CREATED_CUSTOM_URL_LOG = "Created custom short URL: {short_url}"
GENERATED_SHORT_URL_LOG = "Generated short URL: {short_url}"
ERROR_SHORTEN_URL_LOG = "Error in shorten_url: {error}"
RECEIVED_REQUEST_LIST_URLS_LOG = "Received request to list all URLs."
RETRIEVED_URLS_LOG = "Retrieved {count} URLs."
ERROR_LIST_URLS_LOG = "Error in list_urls: {error}"
REDIRECT_SUCCESS_LOG = "Redirect successful: {short_url} -> {original_url}"
REDIRECT_NOT_FOUND = "Redirect failed: No URL for '{short_url}' found"
USER_CREATED_LOG = "Created new user: {username}"

# api_service.py
SHORT_URL_EXISTS_WARNING = "Short URL '{short_url}' already exists."
ERROR_MAX_RETRIES = 'Max retries reached. Unable to create short URL.'

# db_service.py
SAVED_URL_LOG = "Saved URL: {url} with short URL: {short_url}"
UNEXPECTED_ERROR = "Unexpected error occurred: {error}"
DATABASE_UNREACHABLE_ERROR = "Database is currently unreachable."
RETRIEVED_ALL_URLS_LOG = "Retrieved all URLs from the database."
ERROR_RETRIEVING_ALL_URLS_LOG = "Error retrieving all URLs: {error}"
RETRIEVED_ORIGINAL_URL_LOG = "Retrieved original URL for short URL: {short_url}"
SHORT_URL_NOT_EXIST_LOG = "Short URL does not exist"
USER_RETRIEVAL_LOG = "Retrieved user: {username}"
USER_NOT_FOUND_LOG = "User not found: {username}"
USER_CREATION_SUCCESS_LOG = "Successfully created user: {username}"
USER_CREATION_FAILURE_LOG = "Failed to create user: {username}, error: {error}"

# db_models.py
DYNAMODB_TABLE_CREATION_SUCCESS_LOG = "DynamoDB table '{table_name}' created successfully."
DYNAMODB_TABLE_CREATION_ERROR_LOG = "Error creating DynamoDB table: {error}"

# Authentication messages
INCORRECT_CREDENTIALS_ERROR = "Incorrect username or password"
INVALID_AUTH_CREDENTIALS_ERROR = "Invalid authentication credentials"
INACTIVE_OR_INVALID_USER_ERROR = "Inactive or invalid user"
INACTIVE_USER_ERROR = "Inactive user"
USER_CREATION_SUCCESS_MESSAGE = "User '{username}' created successfully."

# Token related constants
ACCESS_TOKEN_TYPE = "bearer"
# Base URL for short URL generation, set as local server address for testing
BASE_URL = "http://127.0.0.1:8000/"

# Logging messages organized by module use
# api_handlers.py
CREATED_CUSTOM_URL_LOG = "Created custom short URL: {short_url}"
GENERATED_SHORT_URL_LOG = "Generated short URL: {short_url}"
ERROR_SHORTEN_URL_LOG = "Error in shorten_url: {error}"
RECEIVED_REQUEST_LIST_URLS_LOG = "Received request to list all URLs."
RETRIEVED_URLS_LOG = "Retrieved {count} URLs."
ERROR_LIST_URLS_LOG = "Error in list_urls: {error}"

# api_service.py
SHORT_URL_EXISTS_WARNING = "Short URL '{short_url}' already exists."
ERROR_MAX_RETRIES = 'Max retries reached. Unable to create short URL.'

# db_service.py
SAVED_URL_LOG = "Saved URL: {url} with short URL: {short_url}"
UNEXPECTED_ERROR_LOG = "Unexpected error occurred: {error}"
DATABASE_UNREACHABLE_ERROR = "Database is currently unreachable."
RETRIEVED_ALL_URLS_LOG = "Retrieved all URLs from the database."
ERROR_RETRIEVING_ALL_URLS_LOG = "Error retrieving all URLs: {error}"
RETRIEVED_ORIGINAL_URL_LOG = "Retrieved original URL for short URL: {short_url}"
SHORT_URL_NOT_EXIST_ERROR = "Short URL does not exist"

# db_models.py
DYNAMODB_TABLE_CREATION_SUCCESS_LOG = "DynamoDB table '{table_name}' created successfully."
DYNAMODB_TABLE_CREATION_ERROR_LOG = "Error creating DynamoDB table: {error}"




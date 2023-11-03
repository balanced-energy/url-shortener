from loguru import logger

# Configure the logger
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", retention='30 days')

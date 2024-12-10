import logging

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define the log format
)

# Create a logger instance for the project
logger = logging.getLogger("app")  # Replace "app" with your project name

import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file into environment variables

class Settings:
    PROJECT_NAME: str = "Fintech Analysis Website"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # API Keys - store these in your .env file
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY") # Example for news fetching
    # TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY") # Example for Twitter

    # Rate Limiting (example, implement as needed)
    DEFAULT_RATE_LIMIT: str = "100/hour"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "app.log")

    # Templates and Static files
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "templates")
    STATIC_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "static")

settings = Settings()

# Ensure logs directory exists
if not os.path.exists(os.path.dirname(settings.LOG_FILE_PATH)):
    os.makedirs(os.path.dirname(settings.LOG_FILE_PATH)) 
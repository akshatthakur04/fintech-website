import uvicorn
from config import settings
import logging

# Configure basic logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE_PATH),
        logging.StreamHandler() # Also print to console
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting Uvicorn server for {settings.PROJECT_NAME}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log file path: {settings.LOG_FILE_PATH}")
    
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG, # Reload only in debug mode
        log_level=settings.LOG_LEVEL.lower()
    ) 
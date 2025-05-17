from fastapi import APIRouter
from app.api import stock, sentiment # Use . for relative imports if preferred and works with your run structure
import logging

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Include stock routes
api_router.include_router(stock.router, prefix="/stocks", tags=["Stocks"])
# Include sentiment routes
api_router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"])

@api_router.get("/health")
async def health_check():
    logger.info("API health check accessed.")
    return {"status": "healthy", "message": "API is operational"}

logger.info("API router configured with stock and sentiment routes.") 
from fastapi import APIRouter, Query, HTTPException
from app.services.sentiment_analyzer import fetch_news_sentiment, analyze_text_sentiment
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/sentiment/news")
async def get_news_sentiment_api(query: str = Query(..., description="Search query for news articles, e.g., a stock symbol or company name")):
    logger.info(f"News sentiment API requested for query: {query}")
    try:
        sentiment_data = await fetch_news_sentiment(query)
        if not sentiment_data:
            logger.warning(f"No news sentiment data found for query: {query}")
            raise HTTPException(status_code=404, detail=f"No news sentiment data found for '{query}'")
        return sentiment_data # Expects a list of dicts or similar JSON serializable structure
    except Exception as e:
        logger.error(f"Error fetching news sentiment for '{query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching news sentiment.")

@router.get("/sentiment/text")
async def get_text_sentiment_api(text: str = Query(..., description="Text to analyze for sentiment")):
    logger.info(f"Text sentiment API requested for text: '{text[:50]}...'")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    try:
        sentiment_result = await analyze_text_sentiment(text)
        return sentiment_result # Expects a dict like {"sentiment": "positive", "score": 0.8}
    except Exception as e:
        logger.error(f"Error analyzing text sentiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error analyzing text sentiment.")

# Note: These are JSON API endpoints. 
# If you need to display sentiment on an HTML page (like stock.html for a stock symbol),
# you would typically call these API endpoints from JavaScript (e.g., in charts.js)
 
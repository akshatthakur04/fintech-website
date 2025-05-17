import aiohttp
import logging
from datetime import datetime, timedelta
from config import settings # For API keys

# Placeholder for actual News API (or other source) base URL and key
NEWS_API_BASE_URL = "https://newsapi.org/v2/everything" # Example

logger = logging.getLogger(__name__)

async def fetch_news_sentiment(query: str, from_days_ago: int = 7) -> list:
    """Fetches news articles related to a query and performs basic sentiment scoring (placeholder)."""
    logger.info(f"Fetching news for sentiment analysis on query: '{query}'")
    if not settings.NEWS_API_KEY:
        logger.error("News API key is not configured.")
        return []

    from_date = (datetime.now() - timedelta(days=from_days_ago)).strftime('%Y-%m-%d')

    params = {
        "q": query,
        "apiKey": settings.NEWS_API_KEY,
        "sortBy": "publishedAt", # or "relevancy", "popularity"
        "pageSize": 10, # Number of articles to fetch
        "from": from_date,
        "language": "en"
    }

    articles_with_sentiment = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NEWS_API_BASE_URL, params=params) as response:
                response.raise_for_status()
                news_data = await response.json()
                logger.debug(f"News API response for '{query}': {str(news_data)[:200]}...")
        
        if news_data.get("status") == "ok" and news_data.get("articles"):
            for article in news_data["articles"]:
                title = article.get("title", "")
                description = article.get("description", "")
                content_to_analyze = f"{title}. {description}" # Combine title and description
                
                # Placeholder sentiment analysis (very basic)
                # In a real app, use a proper NLP library (NLTK Vader, spaCy, Transformers, etc.)
                text_lower = content_to_analyze.lower()
                score = 0 # Neutral
                if any(positive_word in text_lower for positive_word in ["good", "great", "positive", "up", "profit", "buy"]):
                    score += 0.5
                if any(negative_word in text_lower for negative_word in ["bad", "poor", "negative", "down", "loss", "sell"]):
                    score -= 0.5
                
                sentiment = "neutral"
                if score > 0.1:
                    sentiment = "positive"
                elif score < -0.1:
                    sentiment = "negative"

                articles_with_sentiment.append({
                    "title": title,
                    "source": article.get("source", {}).get("name"),
                    "published_at": article.get("publishedAt"),
                    "url": article.get("url"),
                    "sentiment": sentiment,
                    "sentiment_score": round(score, 2)
                })
            logger.info(f"Processed {len(articles_with_sentiment)} articles for '{query}'")
        else:
            logger.warning(f"No articles found or error in News API response for '{query}': {news_data.get('message')}")
            if "message" in news_data:
                 logger.error(f"NewsAPI error for {query}: {news_data['message']}")

    except aiohttp.ClientError as e:
        logger.error(f"AIOHTTP client error fetching news for '{query}': {e}")
    except Exception as e:
        logger.error(f"General error fetching/processing news for '{query}': {e}", exc_info=True)
    
    return articles_with_sentiment

async def analyze_text_sentiment(text: str) -> dict:
    """Analyzes a given piece of text for sentiment (placeholder)."""
    logger.info(f"Analyzing sentiment for text: '{text[:50]}...'")
    # Placeholder sentiment analysis - replace with a real NLP model
    text_lower = text.lower()
    score = 0
    positive_keywords = ["excellent", "amazing", "fantastic", "love", "good", "great", "positive", "recommend", "strong buy"]
    negative_keywords = ["terrible", "awful", "bad", "poor", "hate", "negative", "avoid", "strong sell"]

    for kw in positive_keywords:
        if kw in text_lower:
            score += 0.2
    for kw in negative_keywords:
        if kw in text_lower:
            score -= 0.2
    
    # Normalize score (crude example)
    score = max(-1, min(1, score))

    sentiment_label = "neutral"
    if score >= 0.1:
        sentiment_label = "positive"
    elif score <= -0.1:
        sentiment_label = "negative"
    
    logger.info(f"Sentiment for text: {sentiment_label}, Score: {score:.2f}")
    return {"text": text, "sentiment": sentiment_label, "score": round(score, 2)}

# Example usage (for testing this module directly)
# import asyncio
# async def main_test():
#     query = "Tesla"
#     news_sentiments = await fetch_news_sentiment(query)
#     print(f"--- News Sentiments for {query} ---")
#     for item in news_sentiments[:2]: # Print first 2
#         print(item)
    
#     custom_text = "This stock is performing exceptionally well, great outlook."
#     text_sentiment = await analyze_text_sentiment(custom_text)
#     print(f"--- Text Sentiment for '{custom_text}' ---")
#     print(text_sentiment)

# if __name__ == "__main__":
#     asyncio.run(main_test()) 
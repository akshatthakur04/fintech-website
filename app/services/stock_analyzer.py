import pandas as pd
import aiohttp # For asynchronous HTTP requests
from datetime import datetime, timedelta
import logging
from config import settings # Assuming API key is here

logger = logging.getLogger(__name__)

# Placeholder for actual Alpha Vantage (or other API) base URL and key
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

async def fetch_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """Fetches historical stock data (e.g., daily) for a given symbol and period."""
    logger.info(f"Fetching stock data for {symbol}, period: {period}")
    if not settings.ALPHA_VANTAGE_API_KEY:
        logger.error("Alpha Vantage API key is not configured.")
        return pd.DataFrame() # Return empty DataFrame if API key is missing

    # Determine function and outputsize based on period (simplified)
    # Alpha Vantage's free tier has limitations on data size and frequency
    if period in ["1mo", "3mo"]:
        av_function = "TIME_SERIES_DAILY"
        outputsize = "compact" # Last 100 data points
    else: # For "1y", "5y", "max" - adjust as needed, might require TIME_SERIES_DAILY_ADJUSTED for longer periods
        av_function = "TIME_SERIES_DAILY_ADJUSTED"
        outputsize = "full" # Full history (can be large)

    params = {
        "function": av_function,
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
        "datatype": "json" # Or "csv"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ALPHA_VANTAGE_BASE_URL, params=params) as response:
                response.raise_for_status() # Raise HTTPError for bad responses (4XX or 5XX)
                data = await response.json()
                logger.debug(f"Alpha Vantage API response for {symbol}: {str(data)[:200]}...") # Log snippet of response

        # Process data based on function (TIME_SERIES_DAILY, TIME_SERIES_INTRADAY, etc.)
        # This parsing logic needs to be robust to AV API response structure
        if "Time Series (Daily)" in data:
            df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient='index')
        elif "Monthly Adjusted Time Series" in data: # Example for monthly
             df = pd.DataFrame.from_dict(data["Monthly Adjusted Time Series"], orient='index')
        # Add more conditions based on the AV functions you use
        else:
            logger.warning(f"Unexpected data format from Alpha Vantage for {symbol}: {list(data.keys())}")
            if "Error Message" in data:
                logger.error(f"Alpha Vantage API Error for {symbol}: {data['Error Message']}")
            elif "Information" in data: # E.g., API call frequency limit
                logger.warning(f"Alpha Vantage API Info for {symbol}: {data['Information']}")
            return pd.DataFrame()
        
        df.index = pd.to_datetime(df.index)
        df = df.astype(float) # Ensure numeric types
        # Standardize column names (Alpha Vantage uses "1. open", "2. high", etc.)
        df.rename(columns=lambda x: x.split('. ')[-1].capitalize(), inplace=True)
        df = df.sort_index(ascending=True)
        
        # Filter by period (rough estimation, AV outputsize can be tricky)
        # For more precise period filtering, you might fetch 'full' and then slice
        if period == "1mo":
            df = df[df.index >= (datetime.now() - timedelta(days=30))]
        elif period == "3mo":
            df = df[df.index >= (datetime.now() - timedelta(days=90))]
        elif period == "1y":
            df = df[df.index >= (datetime.now() - timedelta(days=365))]
        elif period == "5y":
            df = df[df.index >= (datetime.now() - timedelta(days=365*5))]
        # 'max' uses all data fetched by 'full' outputsize

        logger.info(f"Successfully fetched and processed data for {symbol}. Shape: {df.shape}")
        return df

    except aiohttp.ClientError as e:
        logger.error(f"AIOHTTP client error fetching data for {symbol}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"General error fetching/processing data for {symbol}: {e}", exc_info=True)
        return pd.DataFrame()

async def analyze_stock_data(df: pd.DataFrame) -> dict:
    """Performs basic analysis on the stock data DataFrame (e.g., calculate indicators)."""
    if df.empty:
        return {"error": "No data to analyze"}

    analysis = {}
    try:
        # Example: Calculate 50-day and 200-day moving averages
        if 'Close' in df.columns:
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            analysis['current_price'] = df['Close'].iloc[-1] if not df.empty else None
            analysis['ma50'] = df['MA50'].iloc[-1] if not df.empty and not pd.isna(df['MA50'].iloc[-1]) else None
            analysis['ma200'] = df['MA200'].iloc[-1] if not df.empty and not pd.isna(df['MA200'].iloc[-1]) else None
            # Simple buy/sell signal (very naive)
            if analysis['ma50'] and analysis['ma200']:
                if analysis['ma50'] > analysis['ma200']:
                    analysis['signal'] = "Potential Buy (Golden Cross pattern if recent)"
                else:
                    analysis['signal'] = "Potential Sell (Death Cross pattern if recent)"
            else:
                analysis['signal'] = "Not enough data for MA signal"
        else:
            logger.warning("'Close' column not found for MA calculation.")
            analysis['signal'] = "Close price data missing for analysis"

        # Add more indicators: RSI, MACD, Bollinger Bands, etc.
        # For Plotly, you might want to return the DataFrame with these indicators added
        # or specific data points for a summary.
        analysis["data_for_chart_with_indicators"] = df.to_dict(orient='split')
        logger.info(f"Stock data analysis completed. Signal: {analysis.get('signal')}")
        
    except Exception as e:
        logger.error(f"Error during stock data analysis: {e}", exc_info=True)
        analysis["error"] = str(e)
    
    return analysis

# Example usage (for testing this module directly)
# import asyncio
# async def main_test():
#     symbol = "AAPL"
#     df = await fetch_stock_data(symbol, period="3mo")
#     if not df.empty:
#         print(f"--- Data for {symbol} ---")
#         print(df.tail())
#         analysis_results = await analyze_stock_data(df.copy()) # Pass a copy for analysis
#         print(f"--- Analysis for {symbol} ---")
#         for key, value in analysis_results.items():
#             if key != "data_for_chart_with_indicators": # Don't print the full df
#                 print(f"{key}: {value}")
#     else:
#         print(f"Could not fetch data for {symbol}")

# if __name__ == "__main__":
#     asyncio.run(main_test()) 
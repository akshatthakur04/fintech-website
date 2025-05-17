from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.templates import templates  # Updated import to break circular dependency
from app.services.stock_analyzer import fetch_stock_data, analyze_stock_data
import logging
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stock/{symbol}", response_class=HTMLResponse)
async def get_stock_page(request: Request, symbol: str):
    logger.info(f"Stock page requested for symbol: {symbol.upper()}")
    try:
        # In a real app, you might fetch more comprehensive data or pre-calculated analysis
        # For now, let's assume stock_analyzer gives us what we need for the template
        raw_data = await fetch_stock_data(symbol.upper())
        if raw_data.empty:
            logger.warning(f"No data found for symbol: {symbol.upper()}")
            raise HTTPException(status_code=404, detail=f"No data found for stock symbol {symbol.upper()}")
        
        # For the stock.html template, we might pass the raw data or a summary
        # The actual plotting might happen client-side via Plotly.js or server-side
        context = {
            "request": request,
            "symbol": symbol.upper(),
            "title": f"{symbol.upper()} Stock Analysis",
            "data_summary": raw_data.head().to_html() # Example: pass first 5 rows as HTML table
        }
        return templates.TemplateResponse("stock.html", context)
    except HTTPException as he:
        logger.error(f"HTTPException for {symbol.upper()}: {he.detail}")
        raise he # Re-raise HTTPException to let FastAPI handle it
    except Exception as e:
        logger.error(f"Error fetching stock page for {symbol.upper()}: {e}", exc_info=True)
        # Render an error page or return a JSON error
        raise HTTPException(status_code=500, detail=f"An internal error occurred while fetching data for {symbol.upper()}.")

@router.get("/stock/{symbol}/data") # JSON endpoint for fetching data for charts
async def get_stock_json_data(symbol: str, period: str = Query("1y", description="Period for stock data e.g., 1mo, 3mo, 1y, 5y, max")):
    logger.info(f"Stock JSON data requested for symbol: {symbol.upper()}, period: {period}")
    try:
        stock_df = await fetch_stock_data(symbol.upper(), period=period)
        if stock_df.empty:
            logger.warning(f"No JSON data found for symbol: {symbol.upper()} with period {period}")
            raise HTTPException(status_code=404, detail=f"No data found for {symbol.upper()}")
        
        # Convert DataFrame to JSON suitable for Plotly.js or other charting libraries
        # Ensure datetime index is converted to string if it's not already JSON serializable
        if isinstance(stock_df.index, pd.DatetimeIndex):
            stock_df.index = stock_df.index.strftime('%Y-%m-%d')
        return stock_df.to_dict(orient='split') # Example: {'index': [...], 'columns': [...], 'data': [[...], ...]}
    except Exception as e:
        logger.error(f"Error fetching stock JSON data for {symbol.upper()}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching stock data.")

# Add more JSON endpoints as needed, e.g., for specific indicators 
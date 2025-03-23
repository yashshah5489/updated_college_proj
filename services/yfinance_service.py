import yfinance as yf
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class YFinanceService:
    def __init__(self):
        logger.info("Yahoo Finance service initialized")

    def _normalize_symbol(self, symbol):
        """
        If the symbol doesn't include an exchange suffix (a dot),
        assume it's an Indian stock on the NSE and append '.NS'.
        """
        if '.' not in symbol:
            return f"{symbol}.NS"
        return symbol

    def get_stock_quote(self, symbol):
        """
        Get current stock quote information using yfinance.
        
        Args:
            symbol (str): Stock symbol (e.g., 'INFY' for Infosys, will be normalized to 'INFY.NS')
            
        Returns:
            dict: Quote data containing symbol, price, change, change percent, previous close, timestamp
        """
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            ticker = yf.Ticker(normalized_symbol)
            info = ticker.info
            if not info:
                logger.error("No quote data available for %s", normalized_symbol)
                return {"error": "No quote data available", "symbol": symbol}
            
            quote = {
                "symbol": info.get("symbol", symbol),
                "price": info.get("regularMarketPrice", "N/A"),
                "change": info.get("regularMarketChange", "N/A"),
                "change_percent": info.get("regularMarketChangePercent", "N/A"),
                "previous_close": info.get("previousClose", "N/A"),
                "timestamp": datetime.now().strftime("%Y-%m-%d")
            }
            return quote
        except Exception as e:
            logger.error("Exception in get_stock_quote: %s", str(e))
            return {"error": str(e), "symbol": symbol}
    
    def get_company_overview(self, symbol):
        """
        Get fundamental company data using yfinance.
        
        Returns a dict with:
          - name
          - sector
          - industry
          - market_cap
          - pe_ratio
          - dividend_yield
          - previous_close (for redundancy)
        """
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            ticker = yf.Ticker(normalized_symbol)
            info = ticker.info
            if not info:
                logger.error("No profile data available for %s", normalized_symbol)
                return {"error": "Unable to fetch company data", "symbol": symbol}
            
            overview = {
                "symbol": info.get("symbol", symbol),
                "name": info.get("shortName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "previous_close": info.get("previousClose", "N/A"),
                "timestamp": datetime.now().strftime("%Y-%m-%d")
            }
            return overview
        except Exception as e:
            logger.error("Exception in get_company_overview: %s", str(e))
            return {"error": str(e), "symbol": symbol}
    
    def get_stock_data(self, symbol):
        """
        Get combined stock data including quote and fundamental data.
        
        Args:
            symbol (str): Stock symbol (e.g., 'INFY' or 'RELIANCE')
            
        Returns:
            dict: Combined stock data with the requested fields.
        """
        quote = self.get_stock_quote(symbol)
        overview = self.get_company_overview(symbol)
        
        # Combine data giving precedence to the fundamental data where available.
        stock_data = {
            **quote,
            "name": overview.get("name", "N/A"),
            "sector": overview.get("sector", "N/A"),
            "industry": overview.get("industry", "N/A"),
            "market_cap": overview.get("market_cap", "N/A"),
            "pe_ratio": overview.get("pe_ratio", "N/A"),
            "dividend_yield": overview.get("dividend_yield", "N/A"),
            "previous_close": quote.get("previous_close", overview.get("previous_close", "N/A")),
            "timestamp": datetime.now().strftime("%Y-%m-%d")
        }
        return stock_data

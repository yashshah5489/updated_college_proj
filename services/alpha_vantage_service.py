import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AlphaVantageService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        logger.info("Alpha Vantage service initialized")
    
    def get_stock_quote(self, symbol):
        """
        Get current stock quote information.
        
        Args:
            symbol (str): Stock symbol (e.g., 'INFY.BSE' for Infosys on BSE)
            
        Returns:
            dict: Stock quote data
        """
        try:
            # Normalize Indian stock symbols
            if '.' not in symbol and symbol.isalpha():
                # If no exchange is specified, check both BSE and NSE
                bse_symbol = f"{symbol}.BSE"
                nse_symbol = f"{symbol}.NSE"
                
                # Try NSE first, then BSE if NSE fails
                quote = self._fetch_quote(nse_symbol)
                if not quote or "Error Message" in quote:
                    quote = self._fetch_quote(bse_symbol)
                    if not quote or "Error Message" in quote:
                        # Try without exchange suffix as a fallback
                        quote = self._fetch_quote(symbol)
            else:
                # Symbol already has exchange information or is international
                quote = self._fetch_quote(symbol)
            
            if not quote or "Error Message" in quote:
                logger.error(f"Error fetching stock quote for {symbol}: {quote.get('Error Message') if quote else 'No data'}")
                return {
                    "symbol": symbol,
                    "price": "N/A",
                    "change": "N/A",
                    "change_percent": "N/A",
                    "timestamp": "N/A",
                    "error": "Unable to fetch stock data"
                }
            
            # Extract the relevant information
            global_quote = quote.get("Global Quote", {})
            if not global_quote:
                return {
                    "symbol": symbol,
                    "price": "N/A",
                    "change": "N/A",
                    "change_percent": "N/A",
                    "timestamp": "N/A",
                    "error": "No quote data available"
                }
                
            return {
                "symbol": global_quote.get("01. symbol", symbol),
                "price": global_quote.get("05. price", "N/A"),
                "change": global_quote.get("09. change", "N/A"),
                "change_percent": global_quote.get("10. change percent", "N/A"),
                "timestamp": global_quote.get("07. latest trading day", datetime.now().strftime("%Y-%m-%d"))
            }
                
        except Exception as e:
            logger.error(f"Exception in get_stock_quote: {str(e)}")
            return {
                "symbol": symbol,
                "price": "N/A",
                "change": "N/A",
                "change_percent": "N/A",
                "timestamp": "N/A",
                "error": str(e)
            }
    
    def _fetch_quote(self, symbol):
        """Helper method to fetch stock quote from Alpha Vantage API"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_company_overview(self, symbol):
        """
        Get company overview information.
        
        Args:
            symbol (str): Stock symbol (e.g., 'INFY.BSE' for Infosys on BSE)
            
        Returns:
            dict: Company overview data
        """
        try:
            # Normalize Indian stock symbols similar to get_stock_quote
            if '.' not in symbol and symbol.isalpha():
                bse_symbol = f"{symbol}.BSE"
                nse_symbol = f"{symbol}.NSE"
                
                overview = self._fetch_overview(nse_symbol)
                if not overview or "Error Message" in overview:
                    overview = self._fetch_overview(bse_symbol)
                    if not overview or "Error Message" in overview:
                        overview = self._fetch_overview(symbol)
            else:
                overview = self._fetch_overview(symbol)
            
            if not overview or "Error Message" in overview:
                logger.error(f"Error fetching company overview for {symbol}")
                return {
                    "symbol": symbol,
                    "name": "N/A",
                    "description": "N/A",
                    "sector": "N/A",
                    "industry": "N/A",
                    "market_cap": "N/A",
                    "pe_ratio": "N/A",
                    "dividend_yield": "N/A",
                    "error": "Unable to fetch company data"
                }
            
            return {
                "symbol": overview.get("Symbol", symbol),
                "name": overview.get("Name", "N/A"),
                "description": overview.get("Description", "N/A"),
                "sector": overview.get("Sector", "N/A"),
                "industry": overview.get("Industry", "N/A"),
                "market_cap": overview.get("MarketCapitalization", "N/A"),
                "pe_ratio": overview.get("PERatio", "N/A"),
                "dividend_yield": overview.get("DividendYield", "N/A"),
                "exchange": overview.get("Exchange", "N/A")
            }
                
        except Exception as e:
            logger.error(f"Exception in get_company_overview: {str(e)}")
            return {
                "symbol": symbol,
                "name": "N/A",
                "description": "N/A",
                "sector": "N/A",
                "industry": "N/A",
                "market_cap": "N/A",
                "pe_ratio": "N/A",
                "dividend_yield": "N/A",
                "error": str(e)
            }
    
    def _fetch_overview(self, symbol):
        """Helper method to fetch company overview from Alpha Vantage API"""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_stock_data(self, symbol):
        """
        Get combined stock data including quote and company overview.
        
        Args:
            symbol (str): Stock symbol (e.g., 'INFY' for Infosys)
            
        Returns:
            dict: Combined stock data
        """
        quote = self.get_stock_quote(symbol)
        overview = self.get_company_overview(symbol)
        
        # Combine the data
        stock_data = {
            **quote,
            "name": overview.get("name", "N/A"),
            "description": overview.get("description", "N/A"),
            "sector": overview.get("sector", "N/A"),
            "industry": overview.get("industry", "N/A"),
            "market_cap": overview.get("market_cap", "N/A"),
            "pe_ratio": overview.get("pe_ratio", "N/A"),
            "dividend_yield": overview.get("dividend_yield", "N/A"),
            "exchange": overview.get("exchange", "N/A")
        }
        
        return stock_data
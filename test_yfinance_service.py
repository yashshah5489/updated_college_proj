import logging
import json
from services.yfinance_service import YFinanceService

def main():
    logging.basicConfig(level=logging.INFO)
    service = YFinanceService()
    
    # For Indian stocks, use symbols without an exchange suffix (they'll be normalized to .NS)
    symbol = "INFY"  # Infosys on NSE (INFY.NS) or use "RELIANCE" for Reliance Industries (RELIANCE.NS)
    print(f"Fetching fundamental data for: {symbol}")
    
    stock_data = service.get_stock_data(symbol)
    print(json.dumps(stock_data, indent=2))
    
if __name__ == "__main__":
    main()

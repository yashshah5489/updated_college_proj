import yfinance as yf

def test_symbol(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    if not info:
        print(f"No data found for symbol: {symbol}")
    else:
        print(f"Data for {symbol}: {info}")

# Test the symbol "NEED.NS"
test_symbol("NEED.NS")

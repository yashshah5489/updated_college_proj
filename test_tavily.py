import logging
from tavily_service import TavilyService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Replace with your valid Tavily API key
API_KEY = "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"

def test_tavily_api():
    """Test the TavilyService search function."""
    tavily = TavilyService(API_KEY)
    query = "Indian stock market trends"
    logger.info("Testing Tavily API...")
    
    try:
        response = tavily.search_financial_news(query)
        if response and response.get("results"):
            logger.info(f"Received {len(response['results'])} articles.")
            for article in response["results"][:3]:  # Print first 3 articles
                print(f"\nTitle: {article['title']}\nURL: {article['url']}\n")
        else:
            logger.warning("No results received.")
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    test_tavily_api()

import requests
import logging
import json
import time
from datetime import datetime, timedelta
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)

class TavilyService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/v1"
        logger.info("Tavily service initialized")
        
    def search_financial_news(self, query, max_results=5, max_retries=3):
        """
        Search for financial news using Tavily API with retry logic.
        
        Args:
            query (str): The financial query to search for
            max_results (int): Maximum number of results to return
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            list: List of news articles
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.debug(f"Searching for financial news with query: {query} (Attempt {retry_count + 1})")
                
                # Set up the search parameters - updated to fix 404 error
                search_params = {
                    "api_key": self.api_key,
                    "query": f"Latest Indian financial news about {query}, focus on stock market impact",
                    "search_depth": "advanced",
                    "include_domains": [
                        "economictimes.indiatimes.com", 
                        "moneycontrol.com", 
                        "livemint.com", 
                        "financialexpress.com", 
                        "business-standard.com", 
                        "ndtv.com/business", 
                        "cnbctv18.com",
                        "zeenews.india.com/markets",
                        "reuters.com", 
                        "bloomberg.com"
                    ],
                    "max_results": max_results,
                    "include_answer": True,
                    "include_images": False,  # Reduce response size
                    "include_raw_content": False
                }
                
                # Make the API request with retry mechanism
                try:
                    response = requests.post(
                        f"{self.base_url}/search",
                        json=search_params,
                        headers={"Content-Type": "application/json"},
                        timeout=20  # Extended timeout to prevent hanging
                    )
                    
                    # Check for successful response
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Process the results
                        processed_results = []
                        for result in data.get("results", []):
                            processed_results.append({
                                "title": result.get("title", "No title"),
                                "url": result.get("url", ""),
                                "content": result.get("content", "No content available"),
                                "published_date": result.get("published_date", "Unknown date"),
                                "source": result.get("source", "Unknown source")
                            })
                        
                        # Get the summary if available
                        summary = data.get("answer", "No summary available")
                        
                        return {
                            "results": processed_results,
                            "summary": summary
                        }
                    elif response.status_code == 404:
                        # Specific handling for 404 errors - try alternative endpoint
                        logger.warning(f"404 error from Tavily API, trying alternative approach on attempt {retry_count + 1}")
                        
                        # Try without include_domains if we get a 404
                        if "include_domains" in search_params:
                            del search_params["include_domains"]
                            logger.info("Removed include_domains parameter to fix 404 error")
                        
                        # Retry with modified parameters
                        retry_count += 1
                        time.sleep(1)  # Short delay before retry
                        continue
                    else:
                        logger.error(f"Error searching Tavily API: {response.status_code} - {response.text}")
                        # Retry with exponential backoff
                        retry_count += 1
                        if retry_count < max_retries:
                            sleep_time = 2 ** retry_count  # Exponential backoff
                            logger.info(f"Retrying in {sleep_time} seconds...")
                            time.sleep(sleep_time)
                            continue
                        else:
                            return {
                                "results": [],
                                "summary": "Unable to fetch financial news at this time."
                            }
                
                except (Timeout, ConnectionError) as e:
                    logger.warning(f"Network error during Tavily API request: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        sleep_time = 2 ** retry_count
                        logger.info(f"Retrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise
                        
            except Exception as e:
                logger.error(f"Exception in Tavily search: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    sleep_time = 2 ** retry_count
                    logger.info(f"Retrying in {sleep_time} seconds due to error: {str(e)}")
                    time.sleep(sleep_time)
                else:
                    return {
                        "results": [],
                        "summary": "An error occurred while fetching financial news."
                    }
        
        # If we've exhausted all retries
        logger.error(f"All {max_retries} attempts to fetch news failed for query: {query}")
        return {
            "results": [],
            "summary": "Unable to fetch financial news after multiple attempts."
        }
    
    def get_financial_context(self, financial_query):
        """
        Get financial context for a given query using Tavily API.
        
        Args:
            financial_query (str): The financial query to get context for
            
        Returns:
            dict: Financial context data
        """
        try:
            news_data = self.search_financial_news(financial_query)
            
            # Extract key information
            context = {
                "news_summary": news_data.get("summary", "No summary available"),
                "articles": news_data.get("results", []),
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": financial_query
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting financial context: {str(e)}")
            return {
                "news_summary": "Unable to retrieve financial context at this time.",
                "articles": [],
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": financial_query
            }

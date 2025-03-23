import requests
import logging
import time
from datetime import datetime
from requests.exceptions import Timeout, ConnectionError

logger = logging.getLogger(__name__)

class TavilyService:
    def __init__(self, api_key):
        self.api_key = api_key
        # Updated base URL per the documentation (remove /v1)
        self.base_url = "https://api.tavily.com"
        logger.info("Tavily service initialized")

    def search_financial_news(self, query, max_results=5, max_retries=3):
        """
        Search for financial news using Tavily API with retry logic.

        Args:
            query (str): The financial query to search for.
            max_results (int): Maximum number of results to return.
            max_retries (int): Maximum number of retry attempts.

        Returns:
            dict: Contains news 'results' and a 'summary'.
        """
        retry_count = 0
        # API key passed in header per docs
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        while retry_count < max_retries:
            try:
                logger.debug(f"Searching for financial news with query: {query} (Attempt {retry_count + 1})")
                
                # Build search parameters (simplified to match Tavily documentation)
                search_params = {
                    "query": f"Latest Indian financial news about {query}, focus on stock market impact",
                    "search_depth": "advanced",
                    "max_results": max_results,
                    "include_answer": True,
                    "include_images": False,
                    "include_raw_content": False
                }
                
                # Updated endpoint URL as per docs: https://api.tavily.com/search
                response = requests.post(
                    f"{self.base_url}/search",
                    json=search_params,
                    headers=headers,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    processed_results = []
                    for result in data.get("results", []):
                        processed_results.append({
                            "title": result.get("title", "No title"),
                            "url": result.get("url", ""),
                            "content": result.get("content", "No content available"),
                            "published_date": result.get("published_date", "Unknown date"),
                            "source": result.get("source", "Unknown source")
                        })
                    summary = data.get("answer", "No summary available")
                    return {
                        "results": processed_results,
                        "summary": summary
                    }
                elif response.status_code == 404:
                    logger.warning(f"404 error from Tavily API on attempt {retry_count + 1}")
                    retry_count += 1
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Error searching Tavily API: {response.status_code} - {response.text}")
                    retry_count += 1
                    if retry_count < max_retries:
                        sleep_time = 2 ** retry_count
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
        logger.error(f"All {max_retries} attempts to fetch news failed for query: {query}")
        return {
            "results": [],
            "summary": "Unable to fetch financial news after multiple attempts."
        }
    
    def get_financial_context(self, financial_query):
        """
        Get financial context for a given query using Tavily API.
        
        Args:
            financial_query (str): The financial query to get context for.
            
        Returns:
            dict: Financial context data.
        """
        try:
            news_data = self.search_financial_news(financial_query)
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

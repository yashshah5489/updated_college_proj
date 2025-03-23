import requests
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TavilyService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/v1"
        logger.info("Tavily service initialized")
        
    def search_financial_news(self, query, max_results=5):
        """
        Search for financial news using Tavily API.
        
        Args:
            query (str): The financial query to search for
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of news articles
        """
        try:
            logger.debug(f"Searching for financial news with query: {query}")
            
            # Set up the search parameters - updated to fix 404 error
            search_params = {
                "api_key": self.api_key,
                "query": f"Indian financial news about {query}",
                "search_depth": "advanced",
                "include_domains": [
                    "economictimes.indiatimes.com", 
                    "moneycontrol.com", 
                    "livemint.com", 
                    "financialexpress.com", 
                    "business-standard.com", 
                    "ndtv.com/business", 
                    "cnbctv18.com",
                    "reuters.com", 
                    "bloomberg.com"
                ],
                "max_results": max_results,
                "include_answer": True,
                "include_images": False,  # Reduce response size
                "include_raw_content": False
            }
            
            # Make the API request - fixing endpoint and adding timeout
            response = requests.post(
                f"{self.base_url}/search",
                json=search_params,
                headers={"Content-Type": "application/json"},
                timeout=15  # Adding timeout to prevent hanging
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
            else:
                logger.error(f"Error searching Tavily API: {response.status_code} - {response.text}")
                return {
                    "results": [],
                    "summary": "Unable to fetch financial news at this time."
                }
                
        except Exception as e:
            logger.error(f"Exception in Tavily search: {str(e)}")
            return {
                "results": [],
                "summary": "An error occurred while fetching financial news."
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

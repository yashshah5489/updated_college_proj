import requests
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"
        logger.info("Groq service initialized with Llama 3.3 70B model")
    
    def _prepare_prompt(self, financial_query, context):
        """
        Prepare the prompt for the Llama model.
        
        Args:
            financial_query (str): The user's financial query
            context (dict): Context information including news articles
            
        Returns:
            str: Formatted prompt for the model
        """
        # Get news context
        news_summary = context.get("news_summary", "No news summary available")
        
        # Get articles
        articles = context.get("articles", [])
        article_text = ""
        for i, article in enumerate(articles[:3], 1):  # Limiting to 3 articles to avoid token limit
            article_text += f"\nArticle {i}:\nTitle: {article.get('title')}\nContent: {article.get('content')[:500]}...\n"
        
        # Get stock data if available
        stock_data = context.get("stock_data", {})
        stock_info = ""
        if stock_data and stock_data.get("symbol") != "N/A":
            stock_info = f"""
STOCK INFORMATION:
Symbol: {stock_data.get('symbol')}
Company: {stock_data.get('name', 'N/A')}
Current Price: {stock_data.get('price', 'N/A')}
Change: {stock_data.get('change', 'N/A')} ({stock_data.get('change_percent', 'N/A')})
Sector: {stock_data.get('sector', 'N/A')}
Industry: {stock_data.get('industry', 'N/A')}
Market Cap: {stock_data.get('market_cap', 'N/A')}
P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}
Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}
Exchange: {stock_data.get('exchange', 'N/A')}
"""
        
        # Format the prompt
        prompt = f"""You are an expert financial advisor focusing on the Indian financial markets. You specialize in analyzing financial queries based on the latest Indian news, market data, and economic trends.

USER QUERY: {financial_query}

LATEST FINANCIAL NEWS SUMMARY: 
{news_summary}

RELEVANT FINANCIAL ARTICLES:
{article_text}
{stock_info}
Based on the above information about Indian markets, please provide:
1. A comprehensive analysis of the financial query specifically for Indian investors
2. Key insights and implications for the Indian economic context
3. Potential risks and opportunities in the Indian market
4. Concrete recommendations and advice tailored for Indian investors
5. References to specific news or data points that influenced your analysis

Consider relevant Indian regulatory bodies (SEBI, RBI), tax implications in India, and local market conditions.
Format your response in a clear, professional manner with proper HTML formatting using <h3>, <p>, <ul>, <li>, <strong> tags for headers, paragraphs, lists, and emphasis.
"""
        return prompt
    
    def analyze_financial_query(self, financial_query, context):
        """
        Analyze a financial query using the Llama 3.3 70B model via Groq Cloud API.
        
        Args:
            financial_query (str): The financial query to analyze
            context (dict): Context information including news articles
            
        Returns:
            dict: Analysis results
        """
        try:
            logger.debug(f"Analyzing financial query with Groq API: {financial_query}")
            
            # Prepare the API request
            prompt = self._prepare_prompt(financial_query, context)
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a professional financial analyst providing accurate, helpful financial advice based on the latest market data and news."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 2000
            }
            
            # Make the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            
            # Check for successful response
            if response.status_code == 200:
                data = response.json()
                analysis_text = data.get("choices", [{}])[0].get("message", {}).get("content", "No analysis available")
                
                # Process the analysis
                analysis_result = {
                    "analysis": analysis_text,
                    "query": financial_query,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model": self.model
                }
                
                return analysis_result
            else:
                logger.error(f"Error from Groq API: {response.status_code} - {response.text}")
                return {
                    "analysis": "Unable to analyze the financial query at this time. Please try again later.",
                    "query": financial_query,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model": self.model,
                    "error": f"API Error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Exception in Groq analysis: {str(e)}")
            return {
                "analysis": "An error occurred while analyzing your financial query.",
                "query": financial_query,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": self.model,
                "error": str(e)
            }

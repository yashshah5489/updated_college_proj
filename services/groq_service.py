import requests
import logging
import json
from datetime import datetime
import dotenv
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()
logger.info("Loaded environment variables from .env file")

class GroqService:
    def __init__(self, api_key):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

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
        prompt = f"""You are a seasoned Indian financial advisor with extensive expertise in analyzing financial markets, regulatory trends, and economic data specific to India. Your role is to deliver actionable, data-driven advice tailored to Indian investors, considering local market conditions, tax implications, and guidelines from Indian regulatory bodies (such as SEBI and RBI).

USER QUERY: {financial_query}

LATEST FINANCIAL NEWS SUMMARY:
{news_summary}

RELEVANT FINANCIAL ARTICLES:
{article_text}
{stock_info}

Based on the above information, please provide a response that includes:

<h3>1. Comprehensive Analysis</h3>
<p>
   Deliver a detailed examination of the user’s query, incorporating current market data, economic trends, and insights drawn from the latest news and articles. Your analysis should be specifically tailored for Indian investors and reflect the nuances of the Indian financial landscape.
</p>

<h3>2. Key Insights and Implications</h3>
<p>
   Identify and explain the major insights from your analysis. Discuss how the information impacts the Indian economy and financial markets, including factors such as market volatility, liquidity, and regulatory changes.
</p>

<h3>3. Risks and Opportunities</h3>
<p>
   Outline potential risks and opportunities in the current market context. Consider aspects like market sentiment, regulatory shifts, tax changes, and global economic influences as they relate to India.
</p>

<h3>4. Concrete Recommendations</h3>
<p>
   Offer actionable recommendations for Indian investors. Your advice should address both short-term strategies and long-term planning, including specific investment strategies, portfolio diversification tips, and risk management techniques.
</p>

<h3>5. Supporting References</h3>
<p>
   Clearly reference specific news items, data points, or financial articles from the provided summaries that have shaped your analysis.
</p>

<p>
   <strong>Additional Considerations:</strong> 
   In your analysis, factor in the latest developments in monetary and fiscal policy, historical market trends, and any relevant tax implications. Ensure that the response is professional, well-structured, and formatted using proper HTML tags (e.g., <code>&lt;h3&gt;</code>, <code>&lt;p&gt;</code>, <code>&lt;ul&gt;</code>, <code>&lt;li&gt;</code>, <code>&lt;strong&gt;</code>).
</p>
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
                "max_tokens": 1000
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

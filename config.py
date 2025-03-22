import os

# Flask app configuration
SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")
DEBUG = True

# MongoDB configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/financial_analyzer")

# API Keys
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "your-tavily-api-key")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your-groq-api-key")

# Llama 3.3 70B model configuration
LLAMA_MODEL = "llama-3.3-70b"

# Application configuration
MAX_QUERY_LENGTH = 500
MAX_HISTORY_ITEMS = 10

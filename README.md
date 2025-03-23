# Smart Financial Analyzer

A Flask-based AI-driven financial analysis tool focused on the Indian market that provides insights using Tavily for financial news, Alpha Vantage for real-time stock data, and Groq Cloud API with Llama 3.3 70B model for AI analysis. Enhanced with wisdom from popular financial self-help books through RAG.

## Features

- User registration and authentication
- Financial query analysis using AI with India-specific insights
- Integration with Alpha Vantage for real-time Indian stock information
- News article integration from Indian financial sources
- RAG-based financial wisdom from popular self-help books
- History of financial analyses
- Dark gradient-themed UI
- Responsive design

## Prerequisites

Before running the application, make sure you have the following installed on your Windows machine:

1. Python 3.8 or higher
2. MongoDB Community Edition (local installation)
3. Git (optional, for cloning the repository)

## Installation Guide for Windows

### 1. Install Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation by opening Command Prompt and running:
   ```
   python --version
   ```

### 2. Install MongoDB Community Edition

1. Download MongoDB Community Server from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Follow the installation instructions
3. After installation, create a data directory:
   ```
   mkdir C:\data\db
   ```
4. Start the MongoDB service:
   ```
   "C:\Program Files\MongoDB\Server\{version}\bin\mongod.exe" --dbpath="C:\data\db"
   ```
   Replace `{version}` with your installed MongoDB version (e.g., 6.0)

### 3. Clone or Download the Project

If using Git:
```
git clone <repository-url>
cd smart-financial-analyzer
```

Or download and extract the ZIP file.

### 4. Set Up a Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

### 5. Install Dependencies

```
pip install -r requirements.txt
```

If requirements.txt is not available, install these packages:
```
pip install flask flask-login flask-pymongo pymongo bson email-validator python-dotenv gunicorn requests werkzeug
```

### 6. Configure Environment Variables

1. Create a `.env` file in the project root by copying the contents from `.env.example`
2. Fill in your API keys:
   - Get a Tavily API key from [tavily.com](https://tavily.com)
   - Get a Groq API key from [console.groq.com](https://console.groq.com)
   - Get an Alpha Vantage API key from [alphavantage.co](https://www.alphavantage.co/support/#api-key)
   - Get an Anthropic API key (for Claude) from [console.anthropic.com](https://console.anthropic.com)
   - Set a strong `SESSION_SECRET` for Flask (you can generate one with `python -c "import secrets; print(secrets.token_hex(16))"`)
   - Make sure `MONGO_URI` is set to `mongodb://localhost:27017/financial_analyzer`

### 7. Run the Application

```
python main.py
```

The application will be available at `http://localhost:5000`

## Project Structure

- `app.py` - Flask application initialization
- `main.py` - Application entry point
- `models.py` - Data models
- `routes/` - Application routes
  - `auth_routes.py` - Authentication routes
  - `analyzer_routes.py` - Financial analysis routes
- `services/` - Service modules
  - `mongodb_service.py` - MongoDB operations
  - `tavily_service.py` - Financial news API (India-focused)
  - `groq_service.py` - AI analysis API
  - `alpha_vantage_service.py` - Stock data API for Indian markets
  - `finance_rag_service.py` - RAG service for financial wisdom
- `data/` - Data files
  - `finance_wisdom/` - Text snippets from popular financial self-help books
- `static/` - Static assets
- `templates/` - HTML templates

## Using the Application

1. Register a new account
2. Log in with your credentials
3. On the analyzer page, enter a financial query
4. View the AI-generated analysis and relevant news articles
5. Access your history of previous analyses

## Troubleshooting

- **MongoDB Connection Issues**: Ensure MongoDB is running locally and accessible at `mongodb://localhost:27017`
- **API Key Issues**: Verify that you've obtained valid API keys and added them to your `.env` file
- **Module Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

## Requirements.txt

If you need to create a requirements.txt file, here's the content:

```
anthropic
bson
email-validator
flask
flask-login
flask-pymongo
gunicorn
pymongo
python-dotenv
requests
werkzeug
```

Save this as `requirements.txt` in the project root.
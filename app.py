import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure MongoDB
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/financial_analyzer")
mongo = PyMongo(app)

# Configure Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.analyzer_routes import analyzer_bp

app.register_blueprint(auth_bp)
app.register_blueprint(analyzer_bp)

# Import User model for Flask-Login
from models import User

@login_manager.user_loader
def load_user(user_id):
    from bson import ObjectId
    try:
        # Convert string ID to ObjectId
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

# Initialize services
from services.tavily_service import TavilyService
from services.groq_service import GroqService
from services.mongodb_service import MongoDBService
from services.alpha_vantage_service import AlphaVantageService

tavily_service = TavilyService(api_key=os.environ.get("TAVILY_API_KEY", "your-tavily-api-key"))
groq_service = GroqService(api_key=os.environ.get("GROQ_API_KEY", "your-groq-api-key"))
mongodb_service = MongoDBService(mongo.db)
alpha_vantage_service = AlphaVantageService(api_key=os.environ.get("ALPHA_VANTAGE_API_KEY", "your-alpha-vantage-api-key"))

# Make services available to the app context
app.tavily_service = tavily_service
app.groq_service = groq_service
app.mongodb_service = mongodb_service
app.alpha_vantage_service = alpha_vantage_service

logger.info("Application initialized successfully")

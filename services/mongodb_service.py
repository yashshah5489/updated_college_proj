import logging
from datetime import datetime
import bson
from models import User, FinancialAnalysis

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self, db):
        self.db = db
        logger.info("MongoDB service initialized")
    
    # User operations
    def create_user(self, username, email, password):
        """
        Create a new user in the database
        
        Args:
            username (str): Username
            email (str): Email address
            password (str): Password
            
        Returns:
            User: Created user object or None if failed
        """
        try:
            # Check if user already exists
            if self.db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
                logger.warning(f"User with username {username} or email {email} already exists")
                return None
            
            # Create new user
            user = User({
                "_id": bson.ObjectId(),
                "username": username,
                "email": email,
                "password_hash": None  # Will be set below
            })
            
            # Set password hash
            user.set_password(password)
            
            # Insert user to database
            user_data = user.to_dict()
            user_data["_id"] = bson.ObjectId()
            user_data["created_at"] = datetime.now()
            
            result = self.db.users.insert_one(user_data)
            
            if result.inserted_id:
                user.id = str(result.inserted_id)
                logger.info(f"User created: {username}")
                return user
            else:
                logger.error("Failed to insert user into database")
                return None
                
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    def get_user_by_username(self, username):
        """
        Get a user by username
        
        Args:
            username (str): Username to find
            
        Returns:
            User: User object or None if not found
        """
        try:
            user_data = self.db.users.find_one({"username": username})
            if user_data:
                return User(user_data)
            return None
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id):
        """
        Get a user by ID
        
        Args:
            user_id (str): User ID to find
            
        Returns:
            User: User object or None if not found
        """
        try:
            user_data = self.db.users.find_one({"_id": bson.ObjectId(user_id)})
            if user_data:
                return User(user_data)
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    # Financial Analysis operations
    def save_financial_analysis(self, user_id, query, context, analysis):
        """
        Save a financial analysis to the database
        
        Args:
            user_id (str): ID of the user who made the query
            query (str): The financial query
            context (dict): Context data including news articles
            analysis (dict): Analysis results
            
        Returns:
            str: ID of the saved analysis or None if failed
        """
        try:
            analysis_data = {
                "_id": bson.ObjectId(),
                "user_id": user_id,
                "query": query,
                "context": context,
                "analysis": analysis,
                "created_at": datetime.now()
            }
            
            result = self.db.financial_analyses.insert_one(analysis_data)
            
            if result.inserted_id:
                logger.info(f"Financial analysis saved for user {user_id}")
                return str(result.inserted_id)
            else:
                logger.error("Failed to insert financial analysis into database")
                return None
                
        except Exception as e:
            logger.error(f"Error saving financial analysis: {str(e)}")
            return None
    
    def get_financial_analysis(self, analysis_id):
        """
        Get a financial analysis by ID
        
        Args:
            analysis_id (str): ID of the analysis to retrieve
            
        Returns:
            FinancialAnalysis: Analysis object or None if not found
        """
        try:
            analysis_data = self.db.financial_analyses.find_one({"_id": bson.ObjectId(analysis_id)})
            if analysis_data:
                return FinancialAnalysis(analysis_data)
            return None
        except Exception as e:
            logger.error(f"Error getting financial analysis: {str(e)}")
            return None
    
    def get_user_financial_analyses(self, user_id, limit=10):
        """
        Get financial analyses for a user
        
        Args:
            user_id (str): User ID
            limit (int): Maximum number of analyses to retrieve
            
        Returns:
            list: List of FinancialAnalysis objects
        """
        try:
            analyses = []
            cursor = self.db.financial_analyses.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
            
            for analysis_data in cursor:
                analyses.append(FinancialAnalysis(analysis_data))
                
            return analyses
        except Exception as e:
            logger.error(f"Error getting user financial analyses: {str(e)}")
            return []
    
    def delete_financial_analysis(self, analysis_id, user_id):
        """
        Delete a financial analysis by ID
        
        Args:
            analysis_id (str): ID of the analysis to delete
            user_id (str): ID of the user who owns the analysis
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            result = self.db.financial_analyses.delete_one({"_id": bson.ObjectId(analysis_id), "user_id": user_id})
            
            if result.deleted_count > 0:
                logger.info(f"Financial analysis {analysis_id} deleted for user {user_id}")
                return True
            else:
                logger.warning(f"No financial analysis found with ID {analysis_id} for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting financial analysis: {str(e)}")
            return False

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import bson

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get('_id'))
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash
        }
    
    def get_id(self):
        return self.id

class FinancialAnalysis:
    def __init__(self, analysis_data=None):
        if analysis_data:
            self.id = str(analysis_data.get('_id')) if analysis_data.get('_id') else None
            self.user_id = analysis_data.get('user_id')
            self.query = analysis_data.get('query')
            self.context = analysis_data.get('context', {})
            self.analysis = analysis_data.get('analysis', {})
            self.created_at = analysis_data.get('created_at')
        else:
            self.id = None
            self.user_id = None
            self.query = None
            self.context = {}
            self.analysis = {}
            self.created_at = None
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'query': self.query,
            'context': self.context,
            'analysis': self.analysis,
            'created_at': self.created_at
        }

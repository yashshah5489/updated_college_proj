"""
Local Setup Script for Smart Financial Analyzer
Run this script once before starting the application locally on Windows
"""

import os
import sys
import shutil
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"Using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_mongodb():
    """Check if MongoDB is running"""
    print("Checking MongoDB connection...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()  # This will raise an exception if the server is not available
        print("MongoDB connection successful!")
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
        print("Please make sure MongoDB is running on localhost:27017")

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("Setting up environment file...")
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print(".env file created from .env.example")
            print("Please edit the .env file to add your API keys")
        else:
            print("Creating .env file with default settings...")
            with open('.env', 'w') as f:
                f.write("""# Smart Financial Analyzer - Environment Variables
# Make a copy of this file as .env and fill in your values

# Flask session secret key
SESSION_SECRET=your-secret-key-here

# MongoDB connection
MONGO_URI=mongodb://localhost:27017/financial_analyzer

# Tavily API - Get your key at https://tavily.com
TAVILY_API_KEY=your-tavily-api-key-here

# Groq API - Get your key at https://console.groq.com
GROQ_API_KEY=your-groq-api-key-here
""")
            print(".env file created. Please edit it to add your API keys")
    else:
        print(".env file already exists")

def check_dependencies():
    """Check for required Python packages"""
    print("Checking dependencies...")
    required_packages = [
        "flask", "flask-login", "flask-pymongo", "pymongo", "bson",
        "email-validator", "python-dotenv", "gunicorn", "requests", "werkzeug"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing packages: " + ", ".join(missing_packages))
        install = input("Would you like to install missing packages? (y/n): ")
        if install.lower() == 'y':
            subprocess.call([sys.executable, "-m", "pip", "install"] + missing_packages)
        else:
            print("Please install the missing packages manually")
    else:
        print("All required packages are installed")

def main():
    """Main setup function"""
    print("=" * 50)
    print("Smart Financial Analyzer - Local Setup")
    print("=" * 50)
    
    check_python_version()
    create_env_file()
    check_dependencies()
    check_mongodb()
    
    print("\nSetup complete! You can now run the application with:")
    print("python main.py")
    print("\nThe application will be available at http://localhost:5000")
    print("=" * 50)

if __name__ == "__main__":
    main()
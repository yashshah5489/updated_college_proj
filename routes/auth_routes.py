import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('analyzer.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return render_template('login.html')
        
        # Get user from database
        user = current_app.mongodb_service.get_user_by_username(username)
        
        if user and user.check_password(password):
            # Log the user in
            login_user(user)
            logger.info(f"User {username} logged in successfully")
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('analyzer.home'))
        else:
            flash('Invalid username or password', 'danger')
            logger.warning(f"Failed login attempt for user {username}")
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('analyzer.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate inputs
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Check if user already exists
        existing_user = current_app.mongodb_service.get_user_by_username(username)
        if existing_user:
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        # Create new user
        user = current_app.mongodb_service.create_user(username, email, password)
        
        if user:
            flash('Registration successful! You can now log in.', 'success')
            logger.info(f"User {username} registered successfully")
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
            logger.error(f"Registration failed for user {username}")
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    username = current_user.username
    logout_user()
    flash('You have been logged out', 'info')
    logger.info(f"User {username} logged out")
    return redirect(url_for('auth.login'))

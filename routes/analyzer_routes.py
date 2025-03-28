import logging
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime

logger = logging.getLogger(__name__)

analyzer_bp = Blueprint('analyzer', __name__)

def extract_stock_symbol(query):
    """
    Extract potential stock symbols from a query.
    
    Args:
        query (str): The financial query
        
    Returns:
        list: Extracted stock symbols
    """
    # Look for common patterns like "INFY", "RELIANCE", "TCS" in the query
    # This is a simple approach and can be improved with more sophisticated methods
    
    # Pattern for Indian stocks (typically uppercase letters, can include .BSE or .NSE)
    patterns = [
        r'\b([A-Z]{2,10})\b',                # General stock symbol pattern
        r'\b([A-Z]{2,10})\.BSE\b',           # BSE specific
        r'\b([A-Z]{2,10})\.NSE\b',           # NSE specific
        r'\b([A-Z]{2,10})(?:\.INDIAIDX)?\b'  # Indian indices
    ]
    
    # Common Indian stock names to look for
    common_stocks = {
        'RELIANCE': 'RELIANCE',
        'INFY': 'INFY',
        'TCS': 'TCS',
        'WIPRO': 'WIPRO', 
        'HDFCBANK': 'HDFCBANK',
        'ICICIBANK': 'ICICIBANK',
        'SBIN': 'SBIN',
        'TATAMOTORS': 'TATAMOTORS',
        'ONGC': 'ONGC',
        'ITC': 'ITC',
        'BHARTIARTL': 'BHARTIARTL',
        'SUNPHARMA': 'SUNPHARMA',
        'TECHM': 'TECHM',
        'KOTAKBANK': 'KOTAKBANK',
        'HINDUNILVR': 'HINDUNILVR',
        'MARUTI': 'MARUTI',
        'AXISBANK': 'AXISBANK',
        'BAJAJFINSV': 'BAJAJFINSV',
        'COALINDIA': 'COALINDIA',
        'HCLTECH': 'HCLTECH',
        'ZOMATO': 'ZOMATO',
        'PAYTM': 'PAYTM',
        'NYKAA': 'NYKAA'
    }
    
    stock_symbols = []
    
    # First check for exact stock name mentions
    query_upper = query.upper()
    for stock_name, symbol in common_stocks.items():
        if stock_name in query_upper:
            stock_symbols.append(symbol)
    
    # Try regex patterns if no exact match is found
    for pattern in patterns:
        matches = re.findall(pattern, query_upper)
        if matches:
            # Add matches to stock symbols
            stock_symbols.extend(matches)
    
    return list(set(stock_symbols))  # Return unique stock symbols

@analyzer_bp.route('/')
def home():
    """Home page route"""
    return render_template('home.html')

@analyzer_bp.route('/analyzer', methods=['GET', 'POST'])
@login_required
def analyzer():
    """Financial analyzer page"""
    if request.method == 'POST':
        # Get the financial query from the form
        financial_query = request.form.get('query')
        
        if not financial_query or len(financial_query.strip()) < 5:
            flash('Please enter a valid financial query (at least 5 characters)', 'danger')
            return render_template('analyzer.html')
            
        try:
            # Extract stock symbols if present in the query
            stock_symbols = extract_stock_symbol(financial_query)
            stock_data = []

            # Get stock data if symbols were found and are relevant
            stock_data = []
            if stock_symbols and hasattr(current_app, 'yfinance_service'):

                for stock_symbol in stock_symbols:
                    logger.info(f"Extracting stock data for symbol: {stock_symbol}")
                    data = current_app.yfinance_service.get_stock_data(stock_symbol)
                    if data and data.get('error'):
                        logger.warning(f"Error getting stock data: {data.get('error')}")
                    else:
                        stock_data.append(data)

            # Get financial context from Tavily
            logger.info(f"Getting financial context for query: {financial_query}")
            context = current_app.tavily_service.get_financial_context(financial_query)
            
            # Ensure both Groq and Tavily are called, and stock data is displayed
            context['stock_data'] = {}
            if stock_symbols:
                for symbol in stock_symbols:
                    data = current_app.yfinance_service.get_stock_data(symbol)
                    if data and data.get('error'):
                        logger.warning(f"Error getting stock data for {symbol}: {data.get('error')}")
                    else:
                        context['stock_data'][symbol] = data  # Store data in a dictionary with symbol as key


            # Always call Groq service with the context





            context['has_stock_data'] = True if stock_data else False
            
            # Get analysis from Groq, ensuring the context is correct
            logger.info(f"Analyzing financial query: {financial_query}")
            analysis_result = current_app.groq_service.analyze_financial_query(financial_query, context)

            
            # Save the analysis to the database
            analysis_id = current_app.mongodb_service.save_financial_analysis(
                current_user.id,
                financial_query,
                context,
                analysis_result
            )
            
            if analysis_id:
                logger.info(f"Analysis saved with ID: {analysis_id}")
            else:
                logger.warning("Failed to save analysis to database")
            
            # Render the template with the analysis results
            return render_template(
                'analyzer.html',
                query=financial_query,
                context=context,
                analysis=analysis_result,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            logger.error(f"Error processing financial query: {str(e)}")
            flash('An error occurred while processing your query. Please try again.', 'danger')
            return render_template('analyzer.html')
    
    # GET request - just show the form
    return render_template('analyzer.html')

@analyzer_bp.route('/history')
@login_required
def history():
    """View analysis history"""
    try:
        # Get the user's analysis history
        analyses = current_app.mongodb_service.get_user_financial_analyses(current_user.id)
        
        return render_template('history.html', analyses=analyses)
        
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        flash('An error occurred while retrieving your analysis history.', 'danger')
        return redirect(url_for('analyzer.home'))

@analyzer_bp.route('/analysis/<analysis_id>')
@login_required
def view_analysis(analysis_id):
    """View a specific analysis"""
    try:
        # Get the analysis from the database
        analysis = current_app.mongodb_service.get_financial_analysis(analysis_id)
        
        if not analysis or analysis.user_id != current_user.id:
            flash('Analysis not found or you do not have permission to view it', 'danger')
            return redirect(url_for('analyzer.history'))
        
        # Render the template with the analysis data
        return render_template(
            'analyzer.html',
            query=analysis.query,
            context=analysis.context,
            analysis=analysis.analysis,
            timestamp=analysis.created_at.strftime("%Y-%m-%d %H:%M:%S") if analysis.created_at else "Unknown"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        flash('An error occurred while retrieving the analysis.', 'danger')
        return redirect(url_for('analyzer.history'))

@analyzer_bp.route('/analysis/<analysis_id>/delete', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    """Delete a specific analysis"""
    try:
        # Delete the analysis from the database
        result = current_app.mongodb_service.delete_financial_analysis(analysis_id, current_user.id)
        
        if result:
            flash('Analysis deleted successfully', 'success')
            logger.info(f"Analysis {analysis_id} deleted by user {current_user.id}")
        else:
            flash('Failed to delete analysis', 'danger')
            logger.warning(f"Failed to delete analysis {analysis_id} by user {current_user.id}")
        
        return redirect(url_for('analyzer.history'))
        
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        flash('An error occurred while deleting the analysis.', 'danger')
        return redirect(url_for('analyzer.history'))

# Define a dictionary of Nifty 50 stocks
nifty_50_stocks = {
    'RELIANCE': 'RELIANCE',
    'INFY': 'INFY',
    'TCS': 'TCS',
    'WIPRO': 'WIPRO', 
    'HDFCBANK': 'HDFCBANK',
    'ICICIBANK': 'ICICIBANK',
    'SBIN': 'SBIN',
    'TATAMOTORS': 'TATAMOTORS',
    'ONGC': 'ONGC',
    'ITC': 'ITC',
    'BHARTIARTL': 'BHARTIARTL',
    'SUNPHARMA': 'SUNPHARMA',
    'TECHM': 'TECHM',
    'KOTAKBANK': 'KOTAKBANK',
    'HINDUNILVR': 'HINDUNILVR',
    'MARUTI': 'MARUTI',
    'AXISBANK': 'AXISBANK',
    'BAJAJFINSV': 'BAJAJFINSV',
    'COALINDIA': 'COALINDIA',
    'HCLTECH': 'HCLTECH',
    'ZOMATO': 'ZOMATO',
    'PAYTM': 'PAYTM',
    'NYKAA': 'NYKAA',
    'ADANIGREEN': 'ADANIGREEN',
    'ADANIPORTS': 'ADANIPORTS',
    'ASIANPAINT': 'ASIANPAINT',
    'BAJFINANCE': 'BAJFINANCE',
    'BAJAJAUTO': 'BAJAJAUTO',
    'BHARATFORG': 'BHARATFORG',
    'BPCL': 'BPCL',
    'CIPLA': 'CIPLA',
    'DIVISLAB': 'DIVISLAB',
    'DRREDDY': 'DRREDDY',
    'EICHERMOT': 'EICHERMOT',
    'GRASIM': 'GRASIM',
    'HINDALCO': 'HINDALCO',
    'HINDPETRO': 'HINDPETRO',
    'INDUSINDBK': 'INDUSINDBK',
    'INFY': 'INFY',
    'ITC': 'ITC',
    'JSWSTEEL': 'JSWSTEEL',
    'KOTAKBANK': 'KOTAKBANK',
    'LT': 'LT',
    'M&M': 'M&M',
    'MARUTI': 'MARUTI',
    'NESTLEIND': 'NESTLEIND',
    'NTPC': 'NTPC',
    'ONGC': 'ONGC',
    'POWERGRID': 'POWERGRID',
    'RELIANCE': 'RELIANCE',
    'SBIN': 'SBIN',
    'SHREECEM': 'SHREECEM',
    'SUNPHARMA': 'SUNPHARMA',
    'TATAMOTORS': 'TATAMOTORS',
    'TCS': 'TCS',
    'TECHM': 'TECHM',
    'ULTRACEMCO': 'ULTRACEMCO',
    'WIPRO': 'WIPRO'
}

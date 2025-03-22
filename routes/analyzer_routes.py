import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime

logger = logging.getLogger(__name__)

analyzer_bp = Blueprint('analyzer', __name__)

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
            # Get financial context from Tavily
            logger.info(f"Getting financial context for query: {financial_query}")
            context = current_app.tavily_service.get_financial_context(financial_query)
            
            # Get analysis from Groq
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

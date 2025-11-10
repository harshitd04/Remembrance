"""
Summary routes blueprint for viewing summaries.
"""
from flask import Blueprint, render_template, jsonify, current_app, session, request
import logging
from app.services.summary_service import SummaryService
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)

summary_bp = Blueprint('summary', __name__)


@summary_bp.route('/')
def summaries_page():
    """Render summaries page."""
    return render_template('summaries.html')


@summary_bp.route('/weekly/<int:week_num>/<int:year>', methods=['GET'])
@handle_errors
def get_weekly_summary(week_num, year):
    """
    Get specific weekly summary.
    
    Args:
        week_num: Week number (1-52)
        year: Year
        
    Returns:
        JSON response with weekly summary
    """
    current_user = session.get('current_user', 'harshit')
    force_regenerate = request.args.get('regenerate', 'false').lower() == 'true'
    
    summary_service = SummaryService(current_app.config['OPENAI_API_KEY'], username=current_user)
    summary = summary_service.generate_weekly_summary(week_num, year, force_regenerate=force_regenerate)
    
    return jsonify({
        'status': 'success',
        **summary
    }), 200


@summary_bp.route('/monthly/<int:month>/<int:year>', methods=['GET'])
@handle_errors
def get_monthly_summary(month, year):
    """
    Get specific monthly summary.
    
    Args:
        month: Month number (1-12)
        year: Year
        
    Returns:
        JSON response with monthly summary
    """
    current_user = session.get('current_user', 'harshit')
    force_regenerate = request.args.get('regenerate', 'false').lower() == 'true'
    
    summary_service = SummaryService(current_app.config['OPENAI_API_KEY'], username=current_user)
    summary = summary_service.generate_monthly_summary(month, year, force_regenerate=force_regenerate)
    
    return jsonify({
        'status': 'success',
        **summary
    }), 200


@summary_bp.route('/yearly/<int:year>', methods=['GET'])
@handle_errors
def get_yearly_summary(year):
    """
    Get specific yearly summary.
    
    Args:
        year: Year
        
    Returns:
        JSON response with yearly summary
    """
    current_user = session.get('current_user', 'harshit')
    force_regenerate = request.args.get('regenerate', 'false').lower() == 'true'
    
    summary_service = SummaryService(current_app.config['OPENAI_API_KEY'], username=current_user)
    summary = summary_service.generate_yearly_summary(year, force_regenerate=force_regenerate)
    
    return jsonify({
        'status': 'success',
        **summary
    }), 200

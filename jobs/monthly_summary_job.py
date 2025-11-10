"""
Monthly summary generation job.
"""
from datetime import datetime
import logging
from app.services.summary_service import SummaryService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


def generate_monthly_summary(app):
    """
    Generate summary for the previous month for all users.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            today = datetime.now()
            month = today.month - 1  # Previous month
            year = today.year
            
            if month < 1:
                # Handle year transition
                month = 12
                year -= 1
            
            logger.info(f"Starting monthly summary generation for {month}/{year}")
            
            # Get all users
            user_service = UserService(app.config['DATA_DIR'])
            users = user_service.get_all_users()
            
            # Generate summary for each user
            for username in users:
                try:
                    summary_service = SummaryService(app.config['OPENAI_API_KEY'], username=username)
                    summary = summary_service.generate_monthly_summary(month, year)
                    logger.info(f"Monthly summary generated for {username}: {summary['entries_count']} entries")
                except Exception as e:
                    logger.error(f"Monthly summary failed for {username}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Monthly summary generation failed: {str(e)}", exc_info=True)

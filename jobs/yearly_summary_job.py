"""
Yearly summary generation job.
"""
from datetime import datetime
import logging
from app.services.summary_service import SummaryService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


def generate_yearly_summary(app):
    """
    Generate summary for the previous year for all users.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            today = datetime.now()
            year = today.year - 1  # Previous year
            
            logger.info(f"Starting yearly summary generation for {year}")
            
            # Get all users
            user_service = UserService(app.config['DATA_DIR'])
            users = user_service.get_all_users()
            
            # Generate summary for each user
            for username in users:
                try:
                    summary_service = SummaryService(app.config['OPENAI_API_KEY'], username=username)
                    summary = summary_service.generate_yearly_summary(year)
                    logger.info(f"Yearly summary generated for {username}: {summary['entries_count']} entries")
                except Exception as e:
                    logger.error(f"Yearly summary failed for {username}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Yearly summary generation failed: {str(e)}", exc_info=True)

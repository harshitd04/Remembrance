"""
Weekly summary generation job.
"""
from datetime import datetime, timedelta
import logging
from app.services.summary_service import SummaryService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


def generate_weekly_summary(app):
    """
    Generate summary for the previous week for all users.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            today = datetime.now()
            week_num = today.isocalendar()[1] - 1  # Previous week
            year = today.year
            
            if week_num < 1:
                # Handle year transition
                week_num = 52
                year -= 1
            
            logger.info(f"Starting weekly summary generation for week {week_num}, {year}")
            
            # Get all users
            user_service = UserService(app.config['DATA_DIR'])
            users = user_service.get_all_users()
            
            # Generate summary for each user
            for username in users:
                try:
                    summary_service = SummaryService(app.config['OPENAI_API_KEY'], username=username)
                    summary = summary_service.generate_weekly_summary(week_num, year)
                    logger.info(f"Weekly summary generated for {username}: {summary['entries_count']} entries")
                except Exception as e:
                    logger.error(f"Weekly summary failed for {username}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Weekly summary generation failed: {str(e)}", exc_info=True)

"""
Scheduler jobs for automated summary generation.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def init_scheduler(app):
    """
    Initialize APScheduler for batch jobs.
    
    Args:
        app: Flask application instance
    """
    scheduler = BackgroundScheduler()
    
    with app.app_context():
        from jobs.weekly_summary_job import generate_weekly_summary
        from jobs.monthly_summary_job import generate_monthly_summary
        from jobs.yearly_summary_job import generate_yearly_summary
        
        # Weekly summary every Sunday at 00:00
        scheduler.add_job(
            func=lambda: generate_weekly_summary(app),
            trigger='cron',
            day_of_week=6,
            hour=0,
            minute=0,
            id='weekly_summary',
            name='Generate weekly summary'
        )
        
        # Monthly summary on 1st of month at 02:00
        scheduler.add_job(
            func=lambda: generate_monthly_summary(app),
            trigger='cron',
            day=1,
            hour=2,
            minute=0,
            id='monthly_summary',
            name='Generate monthly summary'
        )
        
        # Yearly summary on January 1st at 03:00
        scheduler.add_job(
            func=lambda: generate_yearly_summary(app),
            trigger='cron',
            month=1,
            day=1,
            hour=3,
            minute=0,
            id='yearly_summary',
            name='Generate yearly summary'
        )
        
        scheduler.start()
        logger.info("Scheduler initialized with summary generation jobs")

"""
Flask application factory for Remembrance.
"""
from flask import Flask
from app.config import Config
import os


def create_app(config_class=Config):
    """
    Create and configure Flask application instance.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure data directories exist
    os.makedirs(app.config['ENTRIES_DIR'], exist_ok=True)
    os.makedirs(app.config['SUMMARIES_DIR'], exist_ok=True)
    os.makedirs(app.config['EMBEDDINGS_DIR'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Initialize user service and ensure default user exists
    from app.services.user_service import UserService
    user_service = UserService(app.config['DATA_DIR'])
    
    # Register blueprints
    from app.routes.journal_bp import journal_bp
    from app.routes.search_bp import search_bp
    from app.routes.summary_bp import summary_bp
    from app.routes.main_bp import main_bp
    from app.routes.settings_bp import settings_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(journal_bp, url_prefix='/journal')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(summary_bp, url_prefix='/summary')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    # Add context processor for current user
    @app.context_processor
    def inject_user():
        from flask import session
        return dict(current_user=session.get('current_user', 'harshit'))
    
    # Initialize scheduler for batch jobs
    if app.config['BATCH_PROCESSING_ENABLED']:
        from jobs import init_scheduler
        init_scheduler(app)
    
    return app

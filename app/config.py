"""
Configuration management for Remembrance application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Data storage paths
    DATA_DIR = os.getenv('DATA_DIR', './data')
    ENTRIES_DIR = os.getenv('ENTRIES_DIR', './data/entries')
    SUMMARIES_DIR = os.getenv('SUMMARIES_DIR', './data/summaries')
    EMBEDDINGS_DIR = os.getenv('EMBEDDINGS_DIR', './data/embeddings')
    
    # Batch processing
    BATCH_PROCESSING_ENABLED = os.getenv('BATCH_PROCESSING_ENABLED', 'True') == 'True'
    BATCH_PROCESS_TIME = os.getenv('BATCH_PROCESS_TIME', '02:00')
    BATCH_API_TIMEOUT = int(os.getenv('BATCH_API_TIMEOUT', '86400'))
    
    # Application settings
    MAX_RECORDING_DURATION = int(os.getenv('MAX_RECORDING_DURATION', '900'))
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '26214400'))
    APP_THEME = os.getenv('APP_THEME', 'crystal_violet')
    
    # File upload settings
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE
    UPLOAD_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.webm', '.mp4', '.mpga', '.mpeg'}

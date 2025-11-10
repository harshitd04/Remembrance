"""
Custom decorators for Remembrance application.
"""
from functools import wraps
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def handle_errors(f):
    """
    Decorator to handle errors and return JSON responses.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error in {f.__name__}: {str(e)}")
            return jsonify({
                'status': 'error',
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }), 400
        except FileNotFoundError as e:
            logger.error(f"File not found in {f.__name__}: {str(e)}")
            return jsonify({
                'status': 'error',
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }), 404
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred'
            }), 500
    
    return decorated_function

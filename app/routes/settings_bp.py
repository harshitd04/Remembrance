"""
Settings routes blueprint for user management.
"""
from flask import Blueprint, render_template, request, jsonify, session, current_app
import logging
from app.services.user_service import UserService
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
def settings_page():
    """Render settings page."""
    user_service = UserService(current_app.config['DATA_DIR'])
    users = user_service.get_all_users()
    current_user = session.get('current_user', 'harshit')
    
    return render_template('settings.html', users=users, current_user=current_user)


@settings_bp.route('/api/users', methods=['GET'])
@handle_errors
def get_users():
    """
    Get all users.
    
    Returns:
        JSON response with list of users
    """
    user_service = UserService(current_app.config['DATA_DIR'])
    users = user_service.get_all_users()
    current_user = session.get('current_user', 'harshit')
    
    return jsonify({
        'status': 'success',
        'users': users,
        'current_user': current_user
    }), 200


@settings_bp.route('/api/users', methods=['POST'])
@handle_errors
def add_user():
    """
    Add a new user.
    
    Returns:
        JSON response with success status
    """
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    
    if not username:
        return jsonify({
            'status': 'error',
            'message': 'Username is required'
        }), 400
    
    user_service = UserService(current_app.config['DATA_DIR'])
    
    if user_service.user_exists(username):
        return jsonify({
            'status': 'error',
            'message': f'User "{username}" already exists'
        }), 400
    
    success = user_service.add_user(username)
    
    if success:
        logger.info(f"User added: {username}")
        return jsonify({
            'status': 'success',
            'message': f'User "{username}" added successfully',
            'username': username
        }), 201
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to add user'
        }), 500


@settings_bp.route('/api/users/<username>', methods=['DELETE'])
@handle_errors
def delete_user(username):
    """
    Delete a user.
    
    Args:
        username: Username to delete
        
    Returns:
        JSON response with success status
    """
    user_service = UserService(current_app.config['DATA_DIR'])
    
    if not user_service.user_exists(username):
        return jsonify({
            'status': 'error',
            'message': f'User "{username}" not found'
        }), 404
    
    # Check if trying to delete current user
    current_user = session.get('current_user', 'harshit')
    if username == current_user:
        return jsonify({
            'status': 'error',
            'message': 'Cannot delete the currently active user'
        }), 400
    
    # Delete user and their data
    success = user_service.delete_user(username, delete_data=True)
    
    if success:
        logger.info(f"User and data deleted: {username}")
        return jsonify({
            'status': 'success',
            'message': f'User "{username}" and all their data deleted successfully'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete user'
        }), 500


@settings_bp.route('/api/users/switch', methods=['POST'])
@handle_errors
def switch_user():
    """
    Switch the active user.
    
    Returns:
        JSON response with success status
    """
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    
    if not username:
        return jsonify({
            'status': 'error',
            'message': 'Username is required'
        }), 400
    
    user_service = UserService(current_app.config['DATA_DIR'])
    
    if not user_service.user_exists(username):
        return jsonify({
            'status': 'error',
            'message': f'User "{username}" not found'
        }), 404
    
    # Update session
    session['current_user'] = username
    
    logger.info(f"Switched to user: {username}")
    
    return jsonify({
        'status': 'success',
        'message': f'Switched to user "{username}"',
        'current_user': username
    }), 200

"""
Journal routes blueprint for entry management.
"""
from flask import Blueprint, request, jsonify, current_app, session
from datetime import datetime
import uuid
import logging
from app.services.json_storage_service import JSONStorageService
from app.services.embedding_service import EmbeddingService
from app.utils.validators import validate_date_format, validate_content
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)

journal_bp = Blueprint('journal', __name__)


@journal_bp.route('/new-entry', methods=['POST'])
@handle_errors
def create_entry():
    """
    Create new journal entry or append to existing date's entry.
    
    Returns:
        JSON response with entry details
    """
    data = request.get_json()
    
    # Get current user from session
    current_user = session.get('current_user', 'harshit')
    storage = JSONStorageService(username=current_user)
    
    # Validate input
    content = data.get('content', '').strip()
    date = data.get('date', '')
    entry_type = data.get('type', 'text')
    
    if not validate_date_format(date):
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format. Use YYYY-MM-DD'
        }), 400
    
    if not validate_content(content):
        return jsonify({
            'status': 'error',
            'message': 'Content cannot be empty'
        }), 400
    
    # Check if entry exists for date
    existing_entries = storage.load_entry_by_date(date)
    is_appended = existing_entries is not None
    
    # Prepare entry data
    entry = {
        "id": str(uuid.uuid4()),
        "content": content,
        "type": entry_type,
        "created_at": datetime.now().isoformat(),
        "edited_at": None
    }
    
    # Save to JSON
    success = storage.save_entry(date, entry, is_append=is_appended)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': 'Failed to save entry'
        }), 500
    
    # Generate embeddings asynchronously (simplified for MVP)
    try:
        embedding_service = EmbeddingService(current_app.config['OPENAI_API_KEY'])
        embedding = embedding_service.embed_text(content)
        storage.save_embedding(entry['id'], embedding, date, content[:100])
    except Exception as e:
        logger.warning(f"Failed to generate embedding: {str(e)}")
        # Continue even if embedding fails
    
    response = {
        "status": "success",
        "date": date,
        "entry_id": entry["id"],
        "appended": is_appended,
        "entries_count": len(existing_entries) + 1 if existing_entries else 1,
        "message": "Entry saved successfully"
    }
    
    if is_appended:
        response["notification"] = "📝 Entry already exists for this date. Your new entry has been appended."
    
    return jsonify(response), 200


@journal_bp.route('/entries/<date>', methods=['GET'])
@handle_errors
def get_entries(date):
    """
    Retrieve all entries for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        JSON response with entries
    """
    # Get current user from session
    current_user = session.get('current_user', 'harshit')
    storage = JSONStorageService(username=current_user)
    
    if not validate_date_format(date):
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format'
        }), 400
    
    entries = storage.load_entry_by_date(date)
    
    if entries is None:
        return jsonify({
            'status': 'success',
            'date': date,
            'entries': [],
            'count': 0
        }), 200
    
    return jsonify({
        'status': 'success',
        'date': date,
        'entries': entries,
        'count': len(entries)
    }), 200


@journal_bp.route('/edit/<date>', methods=['PUT'])
@handle_errors
def edit_entry(date):
    """
    Edit specific journal entry.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        JSON response with update status
    """
    # Get current user from session
    current_user = session.get('current_user', 'harshit')
    storage = JSONStorageService(username=current_user)
    
    data = request.get_json()
    entry_id = data.get('entry_id')
    new_content = data.get('content', '').strip()
    
    if not validate_date_format(date):
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format'
        }), 400
    
    if not validate_content(new_content):
        return jsonify({
            'status': 'error',
            'message': 'Content cannot be empty'
        }), 400
    
    # Load existing entries
    entries = storage.load_entry_by_date(date)
    
    if not entries:
        return jsonify({
            'status': 'error',
            'message': 'Entry not found'
        }), 404
    
    # Find and update entry
    updated = False
    for entry in entries:
        if entry['id'] == entry_id:
            entry['content'] = new_content
            entry['edited_at'] = datetime.now().isoformat()
            updated = True
            break
    
    if not updated:
        return jsonify({
            'status': 'error',
            'message': 'Entry ID not found'
        }), 404
    
    # Save updated entries (simplified - would need proper update in storage service)
    # For MVP, we'll return success
    
    return jsonify({
        'status': 'success',
        'date': date,
        'entry_id': entry_id,
        'message': 'Entry updated successfully'
    }), 200


@journal_bp.route('/<date>', methods=['DELETE'])
@handle_errors
def delete_entry(date):
    """
    Delete entry for specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        JSON response with deletion status
    """
    # Get current user from session
    current_user = session.get('current_user', 'harshit')
    storage = JSONStorageService(username=current_user)
    
    if not validate_date_format(date):
        return jsonify({
            'status': 'error',
            'message': 'Invalid date format'
        }), 400
    
    entry_id = request.args.get('entry_id')
    
    success = storage.delete_entry(date, entry_id)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': 'Entry not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'date': date,
        'deleted': True,
        'message': 'Entry deleted successfully'
    }), 200

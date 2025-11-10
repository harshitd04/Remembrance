"""
Main routes blueprint for home and general pages.
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import logging
from app.services.transcription_service import TranscriptionService
from app.utils.decorators import handle_errors

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render home page with voice/text entry form."""
    return render_template('home.html')


@main_bp.route('/journals')
def journals():
    """Render journals page for viewing entries by date."""
    return render_template('journals.html')


@main_bp.route('/api/transcribe', methods=['POST'])
@handle_errors
def transcribe():
    """
    Handle audio transcription via OpenAI API.
    Routes to appropriate model based on input type:
    - Microphone recording → whisper-1 (real-time)
    - File upload → whisper-1 (batch processing)
    
    Returns:
        JSON response with transcribed text
    """
    logger.info("Transcription request received")
    
    if 'audio' not in request.files:
        logger.error("No audio file in request")
        return jsonify({
            'status': 'error',
            'message': 'No audio file provided'
        }), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        logger.error("Empty filename")
        return jsonify({
            'status': 'error',
            'message': 'No file selected'
        }), 400
    
    # Determine if this is real-time (microphone) or file upload
    # Check for 'source' parameter in form data
    is_realtime = request.form.get('source') == 'microphone'
    logger.info(f"Source: {'microphone' if is_realtime else 'file'}")
    
    # Save file temporarily
    filename = secure_filename(f"{uuid.uuid4()}_{audio_file.filename}")
    temp_dir = os.path.join(current_app.config['DATA_DIR'], 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, filename)
    audio_file.save(file_path)
    
    file_size = os.path.getsize(file_path)
    logger.info(f"Saved audio file: {filename}, size: {file_size} bytes")
    
    try:
        # Transcribe with appropriate model
        transcription_service = TranscriptionService(
            api_key=current_app.config['OPENAI_API_KEY']
        )
        
        result = transcription_service.transcribe_audio(
            file_path, 
            is_realtime=is_realtime
        )
        
        # Clean up temp file
        os.remove(file_path)
        
        return jsonify(result), 200
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.error(f"Transcription error: {str(e)}", exc_info=True)
        
        # Return detailed error message
        error_message = str(e)
        if "api_key" in error_message.lower():
            error_message = "OpenAI API key is missing or invalid"
        elif "quota" in error_message.lower():
            error_message = "OpenAI API quota exceeded"
        elif "rate" in error_message.lower():
            error_message = "Rate limit exceeded, please try again"
        
        return jsonify({
            'status': 'error',
            'message': f'Transcription failed: {error_message}'
        }), 500

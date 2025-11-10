"""
OpenAI Whisper API transcription service.
"""
import openai
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Handle audio transcription using OpenAI Whisper API."""
    
    def __init__(self, api_key: str):
        """
        Initialize transcription service.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = openai.OpenAI(api_key=api_key)
    
    def transcribe_audio(self, file_path: str, language: str = None, 
                        is_realtime: bool = False) -> Dict:
        """
        Transcribe audio file using appropriate model.
        
        Args:
            file_path: Path to audio file
            language: Optional ISO-639-1 language code
            is_realtime: If True, use gpt-4o-mini-transcribe for real-time,
                        otherwise use whisper-1 for file uploads
            
        Returns:
            Dictionary with transcription result
        """
        try:
            # Choose model based on input type
            # Note: Both use whisper-1 as it's the standard transcription model
            # Real-time vs batch is handled by OpenAI's API automatically
            model = "whisper-1"
            
            with open(file_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=language,
                    temperature=0
                )
            
            logger.info(f"Successfully transcribed audio file using {model}: {file_path}")
            
            return {
                "status": "success",
                "text": response.text,
                "language": language or "unknown",
                "model": model
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}", exc_info=True)
            raise
    
    def validate_audio_file(self, file_path: str, max_size: int = 26214400) -> tuple[bool, str]:
        """
        Validate audio file size and format.
        
        Args:
            file_path: Path to audio file
            max_size: Maximum file size in bytes (default 25MB)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        if not path.exists():
            return False, "File does not exist"
        
        file_size = path.stat().st_size
        if file_size > max_size:
            return False, f"File exceeds {max_size / 1024 / 1024:.0f}MB limit"
        
        valid_extensions = {'.mp3', '.wav', '.m4a', '.webm', '.mp4', '.mpga', '.mpeg'}
        if path.suffix.lower() not in valid_extensions:
            return False, "Invalid audio format"
        
        return True, "Valid"

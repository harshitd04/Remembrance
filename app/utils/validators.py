"""
Input validation functions for Remembrance application.
"""
from datetime import datetime
from pathlib import Path


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_content(content: str, min_length: int = 1, max_length: int = 50000) -> bool:
    """
    Validate journal entry content.
    
    Args:
        content: Content string to validate
        min_length: Minimum content length
        max_length: Maximum content length
        
    Returns:
        True if valid, False otherwise
    """
    if not content or not isinstance(content, str):
        return False
    
    content = content.strip()
    return min_length <= len(content) <= max_length


def validate_audio_file(file_path: str, max_size: int = 26214400) -> tuple[bool, str]:
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


def validate_query(query: str, min_length: int = 1, max_length: int = 500) -> bool:
    """
    Validate search query.
    
    Args:
        query: Search query string
        min_length: Minimum query length
        max_length: Maximum query length
        
    Returns:
        True if valid, False otherwise
    """
    if not query or not isinstance(query, str):
        return False
    
    query = query.strip()
    return min_length <= len(query) <= max_length

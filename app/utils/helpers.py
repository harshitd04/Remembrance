"""
Helper utility functions for Remembrance application.
"""
from datetime import datetime
import calendar


def format_date_display(date_str: str) -> str:
    """
    Format ISO date string for display (dd-mm-yyyy).
    
    Args:
        date_str: ISO format date string (YYYY-MM-DD)
        
    Returns:
        Formatted date string (dd-mm-yyyy)
    """
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime('%d-%m-%Y')
    except (ValueError, TypeError):
        return date_str


def parse_display_date(display_date: str) -> str:
    """
    Parse display date (dd-mm-yyyy) to ISO format (YYYY-MM-DD).
    
    Args:
        display_date: Date in dd-mm-yyyy format
        
    Returns:
        ISO format date string (YYYY-MM-DD)
    """
    try:
        date_obj = datetime.strptime(display_date, '%d-%m-%Y')
        return date_obj.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return display_date


def get_month_name(month_num: int) -> str:
    """
    Get month name from month number.
    
    Args:
        month_num: Month number (1-12)
        
    Returns:
        Month name in lowercase
    """
    return calendar.month_name[month_num].lower()


def get_week_number(date_str: str) -> int:
    """
    Get ISO week number for a date.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Week number (1-53)
    """
    date_obj = datetime.fromisoformat(date_str)
    return date_obj.isocalendar()[1]


def get_year(date_str: str) -> int:
    """
    Extract year from ISO date string.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Year as integer
    """
    date_obj = datetime.fromisoformat(date_str)
    return date_obj.year


def extract_excerpt(text: str, max_length: int = 100) -> str:
    """
    Extract excerpt from text with ellipsis.
    
    Args:
        text: Full text
        max_length: Maximum excerpt length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length].rsplit(' ', 1)[0] + '...'


def highlight_keywords(text: str, keywords: list[str]) -> str:
    """
    Highlight keywords in text (case-insensitive).
    
    Args:
        text: Text to highlight
        keywords: List of keywords to highlight
        
    Returns:
        Text with highlighted keywords
    """
    for keyword in keywords:
        # Simple case-insensitive replacement
        text = text.replace(keyword, f'<mark>{keyword}</mark>')
        text = text.replace(keyword.capitalize(), f'<mark>{keyword.capitalize()}</mark>')
        text = text.replace(keyword.upper(), f'<mark>{keyword.upper()}</mark>')
    
    return text

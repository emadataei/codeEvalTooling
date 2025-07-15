"""
Simple string utility functions.
"""


def capitalize_words(text: str) -> str:
    """
    Capitalize the first letter of each word in a string.
    
    Args:
        text: Input string to capitalize
        
    Returns:
        str: String with each word capitalized
    """
    if not text:
        return ""
    
    return text.title()


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate a string to a maximum length and add ellipsis if needed.
    
    Args:
        text: Input string to truncate
        max_length: Maximum length (default: 50)
        
    Returns:
        str: Truncated string with ellipsis if needed
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

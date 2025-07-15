"""
Utility functions for data validation and formatting.
This module provides common validation and formatting utilities
used across the application.
"""

import re
import datetime
from typing import Optional, Dict, Any, List


def validate_email(email: str) -> bool:
    """
    Validate email address format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def format_phone_number(phone: str) -> Optional[str]:
    """
    Format phone number to standard (XXX) XXX-XXXX format.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        str: Formatted phone number or None if invalid
    """
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if we have exactly 10 digits
    if len(digits) != 10:
        return None
    
    # Format as (XXX) XXX-XXXX
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def calculate_age(birth_date: datetime.date) -> int:
    """
    Calculate age in years from birth date.
    
    Args:
        birth_date: Date of birth
        
    Returns:
        int: Age in years
    """
    today = datetime.date.today()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if today < birth_date.replace(year=today.year):
        age -= 1
    
    return age


def sanitize_user_input(user_input: str, max_length: int = 255) -> str:
    """
    Sanitize user input by removing potentially dangerous characters
    and limiting length.
    
    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized input string
    """
    if not user_input:
        return ""
    
    # Remove HTML tags and script content
    clean_input = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', user_input, flags=re.IGNORECASE)
    clean_input = re.sub(r'<[^>]+>', '', clean_input)
    
    # Remove potentially dangerous characters
    clean_input = re.sub(r'[<>"\']', '', clean_input)
    
    # Limit length
    if len(clean_input) > max_length:
        clean_input = clean_input[:max_length]
    
    return clean_input.strip()


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength and return detailed feedback.
    
    Args:
        password: Password to validate
        
    Returns:
        dict: Validation results with score and feedback
    """
    if not password:
        return {"valid": False, "score": 0, "feedback": ["Password is required"]}
    
    feedback = []
    score = 0
    
    # Length check
    if len(password) >= 8:
        score += 25
    else:
        feedback.append("Password must be at least 8 characters long")
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 25
    else:
        feedback.append("Password must contain at least one uppercase letter")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 25
    else:
        feedback.append("Password must contain at least one lowercase letter")
    
    # Number check
    if re.search(r'\d', password):
        score += 15
    else:
        feedback.append("Password must contain at least one number")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 10
    else:
        feedback.append("Password should contain special characters")
    
    return {
        "valid": score >= 75,
        "score": score,
        "feedback": feedback if feedback else ["Password meets all requirements"]
    }


def parse_csv_line(line: str, delimiter: str = ',') -> List[str]:
    """
    Parse a CSV line handling quoted fields and escape characters.
    
    Args:
        line: CSV line to parse
        delimiter: Field delimiter (default: comma)
        
    Returns:
        list: Parsed fields
    """
    if not line:
        return []
    
    fields = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(line):
        char = line[i]
        
        if char == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                # Escaped quote
                current_field += '"'
                i += 1  # Skip next quote
            else:
                # Toggle quote state
                in_quotes = not in_quotes
        elif char == delimiter and not in_quotes:
            # End of field
            fields.append(current_field.strip())
            current_field = ""
        else:
            current_field += char
        
        i += 1
    
    # Add the last field
    fields.append(current_field.strip())
    
    return fields

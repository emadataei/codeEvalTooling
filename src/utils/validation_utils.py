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


def format_currency(amount: float, currency_code: str = "USD") -> str:
    """
    Format a monetary amount with currency symbol.
    
    Args:
        amount: The monetary amount to format
        currency_code: ISO currency code (default: USD)
        
    Returns:
        str: Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€", 
        "GBP": "£",
        "JPY": "¥"
    }
    
    symbol = currency_symbols.get(currency_code, currency_code)
    return f"{symbol}{amount:,.2f}"


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


def validate_user_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user profile data with business rules and field requirements.
    
    Performs comprehensive validation including required fields, format validation,
    business rule compliance, and data consistency checks.
    
    Args:
        profile_data: Dictionary containing user profile information
        
    Returns:
        dict: Validation results with errors, warnings, and suggestions
    """
    errors = []
    warnings = []
    suggestions = []
    score = 100  # Start with perfect score, deduct for issues
    
    # Required field validation
    required_fields = ['username', 'email', 'first_name', 'last_name']
    for field in required_fields:
        if field not in profile_data or not profile_data[field]:
            errors.append(f"Required field '{field}' is missing or empty")
            score -= 15
    
    # Username validation with business rules
    if 'username' in profile_data:
        username = profile_data['username']
        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")
            score -= 10
        elif len(username) > 20:
            errors.append("Username must be 20 characters or less")
            score -= 10
        
        # Check for inappropriate patterns
        restricted_patterns = ['admin', 'root', 'test', 'demo']
        if any(pattern in username.lower() for pattern in restricted_patterns):
            warnings.append("Username contains restricted pattern")
            score -= 5
        
        # Check for special characters
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            errors.append("Username can only contain letters, numbers, dots, hyphens, and underscores")
            score -= 10
    
    # Email validation and domain checking
    if 'email' in profile_data:
        email = profile_data['email']
        if not validate_email(email):
            errors.append("Invalid email format")
            score -= 15
        else:
            # Business email domain preferences
            domain = email.split('@')[1].lower()
            business_domains = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
            if domain not in business_domains:
                suggestions.append("Consider using a common email provider for better deliverability")
            
            # Check for suspicious domains
            suspicious_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            if domain in suspicious_domains:
                warnings.append("Temporary email domains may cause account issues")
                score -= 20
    
    # Name validation
    if 'first_name' in profile_data and 'last_name' in profile_data:
        first_name = profile_data['first_name']
        last_name = profile_data['last_name']
        
        if len(first_name) < 2 or len(last_name) < 2:
            warnings.append("Names should be at least 2 characters long")
            score -= 5
        
        # Check for numeric characters in names
        if any(char.isdigit() for char in first_name + last_name):
            warnings.append("Names should not contain numbers")
            score -= 5
    
    # Age validation if birth_date provided
    if 'birth_date' in profile_data:
        try:
            age = calculate_age(profile_data['birth_date'])
            if age < 13:
                errors.append("Users must be at least 13 years old")
                score -= 25
            elif age < 18:
                warnings.append("Users under 18 may have limited features")
                score -= 5
            elif age > 120:
                warnings.append("Please verify birth date - age seems unusually high")
                score -= 10
        except Exception:
            errors.append("Invalid birth date format")
            score -= 10
    
    # Phone number validation if provided
    if 'phone' in profile_data and profile_data['phone']:
        formatted_phone = format_phone_number(profile_data['phone'])
        if not formatted_phone:
            warnings.append("Phone number format could not be validated")
            score -= 5
        else:
            suggestions.append("Phone number successfully formatted")
    
    # Profile completeness scoring
    optional_fields = ['phone', 'address', 'birth_date', 'bio', 'website']
    completed_optional = sum(1 for field in optional_fields if field in profile_data and profile_data[field])
    completeness_percentage = (completed_optional / len(optional_fields)) * 100
    
    if completeness_percentage < 50:
        suggestions.append("Complete more profile fields to improve account features")
    
    # Final validation result
    is_valid = len(errors) == 0
    final_score = max(0, score)  # Ensure score doesn't go negative
    
    return {
        "valid": is_valid,
        "score": final_score,
        "completeness_percentage": completeness_percentage,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "summary": f"Profile validation {'passed' if is_valid else 'failed'} with score {final_score}/100"
    }

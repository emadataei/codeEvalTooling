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


def validate_business_rules(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complex business rules for user registration and profile updates.
    
    This function implements multi-step validation including age verification,
    geographic restrictions, subscription tier validation, and promotional eligibility.
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        dict: Validation results with detailed feedback and action items
    """
    errors = []
    warnings = []
    actions = []
    risk_score = 0
    
    # Age and eligibility validation
    if 'birth_date' in user_data:
        age = calculate_age(user_data['birth_date'])
        if age < 13:
            errors.append("User must be at least 13 years old")
            risk_score += 50
        elif age < 18:
            warnings.append("Minor account requires parental consent")
            actions.append("request_parental_consent")
            risk_score += 20
        elif age > 120:
            errors.append("Invalid birth date - age exceeds reasonable limits")
            risk_score += 30
    
    # Geographic and regulatory compliance
    if 'country' in user_data:
        restricted_countries = ['XX', 'YY', 'ZZ']  # Placeholder codes
        if user_data['country'] in restricted_countries:
            errors.append(f"Service not available in {user_data['country']}")
            risk_score += 100
        
        # GDPR compliance for EU countries
        eu_countries = ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'IE']
        if user_data['country'] in eu_countries:
            actions.append("require_gdpr_consent")
            if 'gdpr_consent' not in user_data or not user_data['gdpr_consent']:
                errors.append("GDPR consent required for EU residents")
    
    # Subscription and feature validation
    if 'subscription_tier' in user_data:
        tier = user_data['subscription_tier'].lower()
        if tier == 'premium':
            # Premium users get additional validation
            if 'payment_method' not in user_data:
                errors.append("Premium subscription requires valid payment method")
            else:
                if not validate_payment_method(user_data['payment_method']):
                    errors.append("Invalid payment method for premium subscription")
                    
        elif tier == 'enterprise':
            # Enterprise validation
            if 'company_domain' not in user_data:
                errors.append("Enterprise subscription requires company domain")
            elif not user_data.get('email', '').endswith('@' + user_data['company_domain']):
                warnings.append("Email domain does not match company domain")
                risk_score += 15
    
    # Promotional and marketing validation
    if user_data.get('promotional_emails', False):
        if 'marketing_consent' not in user_data:
            warnings.append("Promotional emails require explicit marketing consent")
            actions.append("request_marketing_consent")
    
    # Calculate final validation status
    is_valid = len(errors) == 0
    requires_manual_review = risk_score > 50 or len(warnings) > 2
    
    return {
        "valid": is_valid,
        "requires_manual_review": requires_manual_review,
        "risk_score": risk_score,
        "errors": errors,
        "warnings": warnings,
        "required_actions": actions,
        "summary": f"Validation {'passed' if is_valid else 'failed'} with risk score {risk_score}"
    }


def validate_payment_method(payment_data: Dict[str, Any]) -> bool:
    """
    Validate payment method information for subscription processing.
    
    Args:
        payment_data: Dictionary containing payment method details
        
    Returns:
        bool: True if payment method is valid
    """
    if not payment_data or 'type' not in payment_data:
        return False
    
    payment_type = payment_data['type'].lower()
    
    if payment_type == 'credit_card':
        required_fields = ['number', 'expiry_month', 'expiry_year', 'cvv']
        for field in required_fields:
            if field not in payment_data:
                return False
        
        # Basic card number validation (simplified)
        card_number = str(payment_data['number']).replace(' ', '').replace('-', '')
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return False
            
    elif payment_type == 'paypal':
        if 'email' not in payment_data:
            return False
        if not validate_email(payment_data['email']):
            return False
            
    elif payment_type == 'bank_transfer':
        required_fields = ['account_number', 'routing_number', 'account_type']
        for field in required_fields:
            if field not in payment_data:
                return False
    else:
        return False  # Unsupported payment type
    
    return True

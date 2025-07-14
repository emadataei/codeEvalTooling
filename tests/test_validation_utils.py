"""
Test cases for validation utilities.
"""

import pytest
import datetime
from src.utils.validation_utils import (
    validate_email,
    format_phone_number,
    calculate_age,
    sanitize_user_input,
    validate_password_strength,
    parse_csv_line
)


class TestEmailValidation:
    """Test email validation functionality."""
    
    def test_valid_emails(self):
        """Test valid email formats."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "123@numbers.net"
        ]
        
        for email in valid_emails:
            assert validate_email(email) == True, f"Should accept valid email: {email}"
    
    def test_invalid_emails(self):
        """Test invalid email formats."""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user@domain",
            "",
            None,
            123
        ]
        
        for email in invalid_emails:
            assert validate_email(email) == False, f"Should reject invalid email: {email}"


class TestPhoneFormatting:
    """Test phone number formatting."""
    
    def test_valid_phone_numbers(self):
        """Test formatting of valid phone numbers."""
        test_cases = [
            ("1234567890", "(123) 456-7890"),
            ("123-456-7890", "(123) 456-7890"),
            ("(123) 456-7890", "(123) 456-7890"),
            ("123.456.7890", "(123) 456-7890")
        ]
        
        for input_phone, expected in test_cases:
            result = format_phone_number(input_phone)
            assert result == expected, f"Expected {expected}, got {result}"
    
    def test_invalid_phone_numbers(self):
        """Test handling of invalid phone numbers."""
        invalid_phones = [
            "123456789",  # Too short
            "12345678901",  # Too long
            "",
            None,
            "abc-def-ghij"
        ]
        
        for phone in invalid_phones:
            assert format_phone_number(phone) is None


class TestAgeCalculation:
    """Test age calculation functionality."""
    
    def test_age_calculation(self):
        """Test age calculation from birth dates."""
        today = datetime.date.today()
        
        # Test exact years
        birth_date = datetime.date(today.year - 25, today.month, today.day)
        assert calculate_age(birth_date) == 25
        
        # Test birthday not yet occurred this year
        if today.month > 1:
            birth_date = datetime.date(today.year - 30, today.month + 1, today.day)
            assert calculate_age(birth_date) == 29
    
    def test_leap_year_birthday(self):
        """Test age calculation for leap year birthdays."""
        # Born on leap day
        birth_date = datetime.date(2000, 2, 29)
        age = calculate_age(birth_date)
        expected_age = datetime.date.today().year - 2000
        
        # Adjust if leap day hasn't occurred this year
        today = datetime.date.today()
        if today < datetime.date(today.year, 3, 1):
            expected_age -= 1
        
        assert age >= expected_age - 1 and age <= expected_age


class TestInputSanitization:
    """Test user input sanitization."""
    
    def test_html_removal(self):
        """Test HTML tag removal."""
        test_cases = [
            ("<script>alert('xss')</script>Hello", "Hello"),
            ("<b>Bold</b> text", "Bold text"),
            ("Normal text", "Normal text"),
            ("<img src='x' onerror='alert(1)'>", "")
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_user_input(input_text)
            assert result == expected
    
    def test_length_limiting(self):
        """Test input length limiting."""
        long_text = "a" * 300
        result = sanitize_user_input(long_text, max_length=10)
        assert len(result) == 10
        assert result == "aaaaaaaaaa"


class TestPasswordValidation:
    """Test password strength validation."""
    
    def test_strong_password(self):
        """Test validation of strong passwords."""
        strong_passwords = [
            "MyStr0ng!Pass",
            "C0mpl3x@Password123",
            "Secure#2024$"
        ]
        
        for password in strong_passwords:
            result = validate_password_strength(password)
            assert result["valid"] == True
            assert result["score"] >= 75
    
    def test_weak_password(self):
        """Test validation of weak passwords."""
        weak_passwords = [
            "weak",
            "password123",
            "PASSWORD",
            "12345678"
        ]
        
        for password in weak_passwords:
            result = validate_password_strength(password)
            assert result["valid"] == False
            assert result["score"] < 75
            assert len(result["feedback"]) > 0


class TestCSVParsing:
    """Test CSV line parsing functionality."""
    
    def test_simple_csv(self):
        """Test parsing simple CSV lines."""
        line = "field1,field2,field3"
        result = parse_csv_line(line)
        assert result == ["field1", "field2", "field3"]
    
    def test_quoted_fields(self):
        """Test parsing CSV with quoted fields."""
        line = '"field with spaces","field,with,commas","normal"'
        result = parse_csv_line(line)
        assert result == ["field with spaces", "field,with,commas", "normal"]
    
    def test_escaped_quotes(self):
        """Test parsing CSV with escaped quotes."""
        line = '"field with ""escaped"" quotes",normal'
        result = parse_csv_line(line)
        assert result == ['field with "escaped" quotes', "normal"]
    
    def test_empty_line(self):
        """Test parsing empty CSV line."""
        result = parse_csv_line("")
        assert result == []

"""
Tests for user profile validation functionality.
"""

import pytest
import datetime
from src.utils.validation_utils import validate_user_profile


class TestUserProfileValidation:
    """Test cases for user profile validation."""
    
    def test_valid_complete_profile(self):
        """Test validation of a complete, valid user profile."""
        profile_data = {
            'username': 'johndoe123',
            'email': 'john.doe@gmail.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': datetime.date(1990, 5, 15),
            'phone': '555-123-4567',
            'address': '123 Main St, City, State',
            'bio': 'Software developer'
        }
        
        result = validate_user_profile(profile_data)
        assert result['valid'] is True
        assert result['score'] >= 85  # Should have high score
        assert len(result['errors']) == 0
        assert result['completeness_percentage'] > 50
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        profile_data = {
            'username': 'testuser'
            # Missing email, first_name, last_name
        }
        
        result = validate_user_profile(profile_data)
        assert result['valid'] is False
        assert len(result['errors']) >= 3  # Missing required fields
        assert result['score'] < 60  # Should have lower score
    
    def test_invalid_username_patterns(self):
        """Test username validation with various invalid patterns."""
        # Test short username
        profile_data = {
            'username': 'ab',
            'email': 'test@gmail.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        result = validate_user_profile(profile_data)
        assert result['valid'] is False
        assert any('3 characters' in error for error in result['errors'])
        
        # Test restricted pattern
        profile_data['username'] = 'admin_user'
        result = validate_user_profile(profile_data)
        assert any('restricted pattern' in warning for warning in result['warnings'])
        
        # Test special characters
        profile_data['username'] = 'user@name!'
        result = validate_user_profile(profile_data)
        assert result['valid'] is False
        assert any('letters, numbers' in error for error in result['errors'])
    
    def test_email_validation_scenarios(self):
        """Test various email validation scenarios."""
        base_profile = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Invalid email
        profile_data = base_profile.copy()
        profile_data['email'] = 'invalid-email'
        result = validate_user_profile(profile_data)
        assert result['valid'] is False
        assert any('Invalid email' in error for error in result['errors'])
        
        # Suspicious domain
        profile_data['email'] = 'user@tempmail.com'
        result = validate_user_profile(profile_data)
        assert any('Temporary email' in warning for warning in result['warnings'])
    
    def test_age_validation(self):
        """Test age-related validation rules."""
        base_profile = {
            'username': 'testuser',
            'email': 'test@gmail.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Underage user
        profile_data = base_profile.copy()
        profile_data['birth_date'] = datetime.date(2015, 1, 1)  # ~10 years old
        result = validate_user_profile(profile_data)
        assert result['valid'] is False
        assert any('13 years old' in error for error in result['errors'])
        
        # Minor user
        profile_data['birth_date'] = datetime.date(2010, 1, 1)  # ~15 years old
        result = validate_user_profile(profile_data)
        assert result['valid'] is True  # Valid but with warnings
        assert any('under 18' in warning for warning in result['warnings'])
        
        # Unrealistic age
        profile_data['birth_date'] = datetime.date(1900, 1, 1)  # ~125 years old
        result = validate_user_profile(profile_data)
        assert any('verify birth date' in warning for warning in result['warnings'])
    
    def test_name_validation(self):
        """Test first and last name validation."""
        profile_data = {
            'username': 'testuser',
            'email': 'test@gmail.com',
            'first_name': 'J',  # Too short
            'last_name': 'D'    # Too short
        }
        
        result = validate_user_profile(profile_data)
        assert any('2 characters' in warning for warning in result['warnings'])
        
        # Names with numbers
        profile_data['first_name'] = 'John123'
        profile_data['last_name'] = 'Doe456'
        result = validate_user_profile(profile_data)
        assert any('not contain numbers' in warning for warning in result['warnings'])
    
    def test_phone_validation(self):
        """Test phone number validation."""
        profile_data = {
            'username': 'testuser',
            'email': 'test@gmail.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '555-123-4567'  # Valid phone
        }
        
        result = validate_user_profile(profile_data)
        assert any('successfully formatted' in suggestion for suggestion in result['suggestions'])
        
        # Invalid phone
        profile_data['phone'] = '123'  # Too short
        result = validate_user_profile(profile_data)
        assert any('could not be validated' in warning for warning in result['warnings'])
    
    def test_profile_completeness_scoring(self):
        """Test profile completeness percentage calculation."""
        # Minimal profile
        minimal_profile = {
            'username': 'testuser',
            'email': 'test@gmail.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        result = validate_user_profile(minimal_profile)
        assert result['completeness_percentage'] == 0  # No optional fields
        assert any('Complete more profile fields' in suggestion for suggestion in result['suggestions'])
        
        # Complete profile
        complete_profile = minimal_profile.copy()
        complete_profile.update({
            'phone': '555-123-4567',
            'address': '123 Main St',
            'birth_date': datetime.date(1990, 1, 1),
            'bio': 'Test bio',
            'website': 'https://example.com'
        })
        
        result = validate_user_profile(complete_profile)
        assert result['completeness_percentage'] == 100

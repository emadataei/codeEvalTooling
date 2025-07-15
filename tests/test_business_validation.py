"""
Tests for business rule validation functions.
"""

import pytest
import datetime
from src.utils.validation_utils import validate_business_rules, validate_payment_method


class TestBusinessRulesValidation:
    """Test cases for complex business rule validation."""
    
    def test_valid_adult_user(self):
        """Test validation of a valid adult user."""
        user_data = {
            'birth_date': datetime.date(1990, 1, 1),
            'country': 'US',
            'subscription_tier': 'basic',
            'email': 'user@example.com'
        }
        
        result = validate_business_rules(user_data)
        assert result['valid'] is True
        assert result['risk_score'] == 0
        assert len(result['errors']) == 0
    
    def test_minor_user_validation(self):
        """Test validation of minor users."""
        user_data = {
            'birth_date': datetime.date(2010, 1, 1),  # 15 years old
            'country': 'US'
        }
        
        result = validate_business_rules(user_data)
        assert result['valid'] is True  # No errors, just warnings
        assert result['risk_score'] == 20
        assert 'request_parental_consent' in result['required_actions']
        assert any('parental consent' in w for w in result['warnings'])
    
    def test_underage_user_rejection(self):
        """Test rejection of users under 13."""
        user_data = {
            'birth_date': datetime.date(2015, 1, 1),  # 10 years old
            'country': 'US'
        }
        
        result = validate_business_rules(user_data)
        assert result['valid'] is False
        assert result['risk_score'] >= 50
        assert any('13 years old' in e for e in result['errors'])
    
    def test_restricted_country(self):
        """Test validation for restricted countries."""
        user_data = {
            'birth_date': datetime.date(1990, 1, 1),
            'country': 'XX'  # Restricted country
        }
        
        result = validate_business_rules(user_data)
        assert result['valid'] is False
        assert result['risk_score'] >= 100
        assert any('not available' in e for e in result['errors'])
    
    def test_gdpr_compliance(self):
        """Test GDPR compliance for EU users."""
        user_data = {
            'birth_date': datetime.date(1990, 1, 1),
            'country': 'DE',  # Germany (EU)
            'gdpr_consent': False
        }
        
        result = validate_business_rules(user_data)
        assert result['valid'] is False
        assert 'require_gdpr_consent' in result['required_actions']
        assert any('GDPR consent' in e for e in result['errors'])
    
    def test_premium_subscription_validation(self):
        """Test premium subscription validation."""
        user_data = {
            'birth_date': datetime.date(1990, 1, 1),
            'country': 'US',
            'subscription_tier': 'premium'
        }
        
        result = validate_business_rules(user_data)
        assert result['valid'] is False
        assert any('payment method' in e for e in result['errors'])


class TestPaymentMethodValidation:
    """Test cases for payment method validation."""
    
    def test_valid_credit_card(self):
        """Test valid credit card validation."""
        payment_data = {
            'type': 'credit_card',
            'number': '4111111111111111',
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvv': '123'
        }
        
        assert validate_payment_method(payment_data) is True
    
    def test_invalid_credit_card_missing_fields(self):
        """Test credit card validation with missing fields."""
        payment_data = {
            'type': 'credit_card',
            'number': '4111111111111111'
            # Missing other required fields
        }
        
        assert validate_payment_method(payment_data) is False
    
    def test_invalid_credit_card_number(self):
        """Test credit card validation with invalid number."""
        payment_data = {
            'type': 'credit_card',
            'number': '123',  # Too short
            'expiry_month': '12',
            'expiry_year': '2025',
            'cvv': '123'
        }
        
        assert validate_payment_method(payment_data) is False
    
    def test_valid_paypal(self):
        """Test valid PayPal validation."""
        payment_data = {
            'type': 'paypal',
            'email': 'user@example.com'
        }
        
        assert validate_payment_method(payment_data) is True
    
    def test_invalid_paypal_email(self):
        """Test PayPal validation with invalid email."""
        payment_data = {
            'type': 'paypal',
            'email': 'invalid-email'
        }
        
        assert validate_payment_method(payment_data) is False
    
    def test_valid_bank_transfer(self):
        """Test valid bank transfer validation."""
        payment_data = {
            'type': 'bank_transfer',
            'account_number': '123456789',
            'routing_number': '021000021',
            'account_type': 'checking'
        }
        
        assert validate_payment_method(payment_data) is True
    
    def test_unsupported_payment_type(self):
        """Test validation with unsupported payment type."""
        payment_data = {
            'type': 'cryptocurrency',
            'wallet_address': 'some_address'
        }
        
        assert validate_payment_method(payment_data) is False

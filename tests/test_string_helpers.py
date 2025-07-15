"""
Tests for string helper utilities.
"""

import pytest
from src.utils.string_helpers import capitalize_words, truncate_string


def test_capitalize_words():
    """Test the capitalize_words function."""
    assert capitalize_words("hello world") == "Hello World"
    assert capitalize_words("") == ""
    assert capitalize_words("python") == "Python"


def test_truncate_string():
    """Test the truncate_string function."""
    short_text = "Hello"
    assert truncate_string(short_text) == "Hello"
    
    long_text = "This is a very long string that should be truncated"
    result = truncate_string(long_text, 20)
    assert len(result) == 20
    assert result.endswith("...")

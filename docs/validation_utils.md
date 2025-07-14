# Validation Utils Module

This module provides common validation and formatting utilities for the application.

## Functions

### `validate_email(email: str) -> bool`
Validates email address format using regex pattern matching.

**Parameters:**
- `email`: Email address string to validate

**Returns:**
- `bool`: True if email format is valid, False otherwise

**Example:**
```python
valid = validate_email("user@example.com")  # Returns True
invalid = validate_email("not-an-email")    # Returns False
```

### `format_phone_number(phone: str) -> Optional[str]`
Formats phone numbers to standard (XXX) XXX-XXXX format.

**Parameters:**
- `phone`: Raw phone number string (accepts various formats)

**Returns:**
- `str`: Formatted phone number or None if invalid

**Example:**
```python
formatted = format_phone_number("1234567890")      # Returns "(123) 456-7890"
formatted = format_phone_number("123-456-7890")   # Returns "(123) 456-7890"
invalid = format_phone_number("123")              # Returns None
```

### `calculate_age(birth_date: datetime.date) -> int`
Calculates age in years from birth date, accounting for whether birthday has occurred this year.

**Parameters:**
- `birth_date`: Date of birth as datetime.date object

**Returns:**
- `int`: Age in complete years

### `sanitize_user_input(user_input: str, max_length: int = 255) -> str`
Sanitizes user input by removing potentially dangerous HTML/script content and limiting length.

**Parameters:**
- `user_input`: Raw user input string
- `max_length`: Maximum allowed length (default: 255)

**Returns:**
- `str`: Sanitized and length-limited string

### `validate_password_strength(password: str) -> Dict[str, Any]`
Validates password strength against multiple criteria and provides detailed feedback.

**Criteria:**
- Minimum 8 characters (25 points)
- Contains uppercase letter (25 points)
- Contains lowercase letter (25 points)  
- Contains number (15 points)
- Contains special character (10 points)

**Returns:**
- `dict`: Contains `valid` (bool), `score` (int), and `feedback` (list) keys

### `parse_csv_line(line: str, delimiter: str = ',') -> List[str]`
Parses CSV line with proper handling of quoted fields and escaped characters.

**Parameters:**
- `line`: CSV line string to parse
- `delimiter`: Field delimiter character (default: comma)

**Returns:**
- `List[str]`: List of parsed field values

## Usage Examples

```python
from src.utils.validation_utils import validate_email, format_phone_number

# Email validation
if validate_email(user_email):
    print("Valid email provided")

# Phone formatting
formatted_phone = format_phone_number(raw_phone_input)
if formatted_phone:
    print(f"Phone: {formatted_phone}")
```

## Testing

Comprehensive test suite available in `tests/test_validation_utils.py` covering:
- Valid and invalid inputs for all functions
- Edge cases and error conditions
- Various input formats and special characters

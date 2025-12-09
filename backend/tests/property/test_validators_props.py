"""Property-based tests for InputValidator.

**Feature: system-optimization, Property 5: 输入长度验证**

This module tests that the InputValidator correctly validates input lengths
to protect against malicious input attacks.
"""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hypothesis import given, settings, strategies as st

from app.utils.validators import InputValidator, ValidationLimits


# ============================================================================
# Strategies for generating test data
# ============================================================================

# Get the limits for reference
LIMITS = ValidationLimits()

# Strategy for generating strings within phone length limit
valid_phone_length_strategy = st.text(min_size=0, max_size=LIMITS.MAX_PHONE_LENGTH)

# Strategy for generating strings exceeding phone length limit
invalid_phone_length_strategy = st.text(
    min_size=LIMITS.MAX_PHONE_LENGTH + 1,
    max_size=LIMITS.MAX_PHONE_LENGTH + 100
)

# Strategy for generating strings within email length limit
valid_email_length_strategy = st.text(min_size=0, max_size=LIMITS.MAX_EMAIL_LENGTH)

# Strategy for generating strings exceeding email length limit
invalid_email_length_strategy = st.text(
    min_size=LIMITS.MAX_EMAIL_LENGTH + 1,
    max_size=LIMITS.MAX_EMAIL_LENGTH + 100
)

# Strategy for generating strings within password length limit
valid_password_length_strategy = st.text(min_size=0, max_size=LIMITS.MAX_PASSWORD_LENGTH)

# Strategy for generating strings exceeding password length limit
invalid_password_length_strategy = st.text(
    min_size=LIMITS.MAX_PASSWORD_LENGTH + 1,
    max_size=LIMITS.MAX_PASSWORD_LENGTH + 100
)

# Strategy for generating strings within content length limit
# Note: Hypothesis has a limit on text generation size, so we use a smaller max
# but still test the boundary behavior
valid_content_length_strategy = st.text(min_size=0, max_size=min(LIMITS.MAX_CONTENT_LENGTH, 5000))

# Strategy for generating strings exceeding content length limit
# We use st.binary() and decode to generate large strings that exceed the limit
def _generate_long_content() -> st.SearchStrategy[str]:
    """Generate content strings that exceed MAX_CONTENT_LENGTH."""
    # Generate a base string and repeat it to exceed the limit
    return st.text(min_size=100, max_size=500).map(
        lambda s: s * ((LIMITS.MAX_CONTENT_LENGTH // max(len(s), 1)) + 2)
    ).filter(lambda s: len(s) > LIMITS.MAX_CONTENT_LENGTH)

invalid_content_length_strategy = _generate_long_content()


# ============================================================================
# Property 5: 输入长度验证
# **Feature: system-optimization, Property 5: 输入长度验证**
# **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
#
# For any input string and corresponding length limit, when the input length
# exceeds the limit, validation should return False.
# ============================================================================


# ----------------------------------------------------------------------------
# Phone Length Validation (Requirement 3.1)
# ----------------------------------------------------------------------------

@settings(max_examples=100)
@given(phone=valid_phone_length_strategy)
def test_phone_within_limit_passes_validation(phone: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.1**
    
    Property: For any phone string with length <= MAX_PHONE_LENGTH (20),
    validation should return True.
    """
    # Act
    result = InputValidator.validate_phone_length(phone)
    
    # Assert
    assert result is True, (
        f"Phone within limit should pass validation. "
        f"Phone length: {len(phone)}, Limit: {LIMITS.MAX_PHONE_LENGTH}, Result: {result}"
    )


@settings(max_examples=100)
@given(phone=invalid_phone_length_strategy)
def test_phone_exceeding_limit_fails_validation(phone: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.1**
    
    Property: For any phone string with length > MAX_PHONE_LENGTH (20),
    validation should return False.
    """
    # Act
    result = InputValidator.validate_phone_length(phone)
    
    # Assert
    assert result is False, (
        f"Phone exceeding limit should fail validation. "
        f"Phone length: {len(phone)}, Limit: {LIMITS.MAX_PHONE_LENGTH}, Result: {result}"
    )


# ----------------------------------------------------------------------------
# Email Length Validation (Requirement 3.2)
# ----------------------------------------------------------------------------

@settings(max_examples=100)
@given(email=valid_email_length_strategy)
def test_email_within_limit_passes_validation(email: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.2**
    
    Property: For any email string with length <= MAX_EMAIL_LENGTH (255),
    validation should return True.
    """
    # Act
    result = InputValidator.validate_email_length(email)
    
    # Assert
    assert result is True, (
        f"Email within limit should pass validation. "
        f"Email length: {len(email)}, Limit: {LIMITS.MAX_EMAIL_LENGTH}, Result: {result}"
    )


@settings(max_examples=100)
@given(email=invalid_email_length_strategy)
def test_email_exceeding_limit_fails_validation(email: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.2**
    
    Property: For any email string with length > MAX_EMAIL_LENGTH (255),
    validation should return False.
    """
    # Act
    result = InputValidator.validate_email_length(email)
    
    # Assert
    assert result is False, (
        f"Email exceeding limit should fail validation. "
        f"Email length: {len(email)}, Limit: {LIMITS.MAX_EMAIL_LENGTH}, Result: {result}"
    )


# ----------------------------------------------------------------------------
# Password Length Validation (Requirement 3.3)
# ----------------------------------------------------------------------------

@settings(max_examples=100)
@given(password=valid_password_length_strategy)
def test_password_within_limit_passes_validation(password: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.3**
    
    Property: For any password string with length <= MAX_PASSWORD_LENGTH (128),
    validation should return True.
    """
    # Act
    result = InputValidator.validate_password_length(password)
    
    # Assert
    assert result is True, (
        f"Password within limit should pass validation. "
        f"Password length: {len(password)}, Limit: {LIMITS.MAX_PASSWORD_LENGTH}, Result: {result}"
    )


@settings(max_examples=100)
@given(password=invalid_password_length_strategy)
def test_password_exceeding_limit_fails_validation(password: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.3**
    
    Property: For any password string with length > MAX_PASSWORD_LENGTH (128),
    validation should return False.
    """
    # Act
    result = InputValidator.validate_password_length(password)
    
    # Assert
    assert result is False, (
        f"Password exceeding limit should fail validation. "
        f"Password length: {len(password)}, Limit: {LIMITS.MAX_PASSWORD_LENGTH}, Result: {result}"
    )


# ----------------------------------------------------------------------------
# Content Length Validation (Requirement 3.4)
# ----------------------------------------------------------------------------

@settings(max_examples=100)
@given(content=valid_content_length_strategy)
def test_content_within_limit_passes_validation(content: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.4**
    
    Property: For any content string with length <= MAX_CONTENT_LENGTH (10000),
    validation should return True.
    """
    # Act
    result = InputValidator.validate_content_length(content)
    
    # Assert
    assert result is True, (
        f"Content within limit should pass validation. "
        f"Content length: {len(content)}, Limit: {LIMITS.MAX_CONTENT_LENGTH}, Result: {result}"
    )


@settings(max_examples=100)
@given(content=invalid_content_length_strategy)
def test_content_exceeding_limit_fails_validation(content: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.4**
    
    Property: For any content string with length > MAX_CONTENT_LENGTH (10000),
    validation should return False.
    """
    # Act
    result = InputValidator.validate_content_length(content)
    
    # Assert
    assert result is False, (
        f"Content exceeding limit should fail validation. "
        f"Content length: {len(content)}, Limit: {LIMITS.MAX_CONTENT_LENGTH}, Result: {result}"
    )


# ----------------------------------------------------------------------------
# Boundary Tests - Exact Limit Values
# ----------------------------------------------------------------------------

@settings(max_examples=100)
@given(st.data())
def test_phone_at_exact_limit_passes(data: st.DataObject) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.1**
    
    Property: For any phone string with length exactly equal to MAX_PHONE_LENGTH,
    validation should return True.
    """
    # Generate string of exact limit length
    phone = data.draw(st.text(min_size=LIMITS.MAX_PHONE_LENGTH, max_size=LIMITS.MAX_PHONE_LENGTH))
    
    # Act
    result = InputValidator.validate_phone_length(phone)
    
    # Assert
    assert result is True, (
        f"Phone at exact limit should pass validation. "
        f"Phone length: {len(phone)}, Limit: {LIMITS.MAX_PHONE_LENGTH}"
    )


@settings(max_examples=100)
@given(st.data())
def test_email_at_exact_limit_passes(data: st.DataObject) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.2**
    
    Property: For any email string with length exactly equal to MAX_EMAIL_LENGTH,
    validation should return True.
    """
    # Generate string of exact limit length
    email = data.draw(st.text(min_size=LIMITS.MAX_EMAIL_LENGTH, max_size=LIMITS.MAX_EMAIL_LENGTH))
    
    # Act
    result = InputValidator.validate_email_length(email)
    
    # Assert
    assert result is True, (
        f"Email at exact limit should pass validation. "
        f"Email length: {len(email)}, Limit: {LIMITS.MAX_EMAIL_LENGTH}"
    )


@settings(max_examples=100)
@given(st.data())
def test_password_at_exact_limit_passes(data: st.DataObject) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.3**
    
    Property: For any password string with length exactly equal to MAX_PASSWORD_LENGTH,
    validation should return True.
    """
    # Generate string of exact limit length
    password = data.draw(st.text(min_size=LIMITS.MAX_PASSWORD_LENGTH, max_size=LIMITS.MAX_PASSWORD_LENGTH))
    
    # Act
    result = InputValidator.validate_password_length(password)
    
    # Assert
    assert result is True, (
        f"Password at exact limit should pass validation. "
        f"Password length: {len(password)}, Limit: {LIMITS.MAX_PASSWORD_LENGTH}"
    )


@settings(max_examples=100)
@given(st.text(min_size=100, max_size=500))
def test_content_at_exact_limit_passes(base_content: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.4**
    
    Property: For any content string with length exactly equal to MAX_CONTENT_LENGTH,
    validation should return True.
    """
    # Generate string of exact limit length by repeating and truncating
    if len(base_content) == 0:
        base_content = "a"
    repeat_count = (LIMITS.MAX_CONTENT_LENGTH // len(base_content)) + 1
    content = (base_content * repeat_count)[:LIMITS.MAX_CONTENT_LENGTH]
    
    # Act
    result = InputValidator.validate_content_length(content)
    
    # Assert
    assert len(content) == LIMITS.MAX_CONTENT_LENGTH
    assert result is True, (
        f"Content at exact limit should pass validation. "
        f"Content length: {len(content)}, Limit: {LIMITS.MAX_CONTENT_LENGTH}"
    )


# ----------------------------------------------------------------------------
# Validate with Error Message Tests
# ----------------------------------------------------------------------------

@settings(max_examples=100)
@given(phone=invalid_phone_length_strategy)
def test_validate_phone_returns_error_message(phone: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.1, 3.5**
    
    Property: For any phone string exceeding the limit, validate_phone
    should return (False, error_message) with a clear error message.
    """
    # Act
    is_valid, error_msg = InputValidator.validate_phone(phone)
    
    # Assert
    assert is_valid is False
    assert str(LIMITS.MAX_PHONE_LENGTH) in error_msg, (
        f"Error message should contain the limit value. "
        f"Error: '{error_msg}'"
    )


@settings(max_examples=100)
@given(email=invalid_email_length_strategy)
def test_validate_email_returns_error_message(email: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.2, 3.5**
    
    Property: For any email string exceeding the limit, validate_email
    should return (False, error_message) with a clear error message.
    """
    # Act
    is_valid, error_msg = InputValidator.validate_email(email)
    
    # Assert
    assert is_valid is False
    assert str(LIMITS.MAX_EMAIL_LENGTH) in error_msg, (
        f"Error message should contain the limit value. "
        f"Error: '{error_msg}'"
    )


@settings(max_examples=100)
@given(password=invalid_password_length_strategy)
def test_validate_password_returns_error_message(password: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.3, 3.5**
    
    Property: For any password string exceeding the limit, validate_password
    should return (False, error_message) with a clear error message.
    """
    # Act
    is_valid, error_msg = InputValidator.validate_password(password)
    
    # Assert
    assert is_valid is False
    assert str(LIMITS.MAX_PASSWORD_LENGTH) in error_msg, (
        f"Error message should contain the limit value. "
        f"Error: '{error_msg}'"
    )


@settings(max_examples=100)
@given(content=invalid_content_length_strategy)
def test_validate_content_returns_error_message(content: str) -> None:
    """
    **Feature: system-optimization, Property 5: 输入长度验证**
    **Validates: Requirements 3.4, 3.5**
    
    Property: For any content string exceeding the limit, validate_content
    should return (False, error_message) with a clear error message.
    """
    # Act
    is_valid, error_msg = InputValidator.validate_content(content)
    
    # Assert
    assert is_valid is False
    assert str(LIMITS.MAX_CONTENT_LENGTH) in error_msg, (
        f"Error message should contain the limit value. "
        f"Error: '{error_msg}'"
    )

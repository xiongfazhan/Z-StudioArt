"""Property-based tests for LogMasker.

**Feature: system-optimization, Properties 2, 3, 4: 日志脱敏格式**

This module tests that the LogMasker correctly masks sensitive information
(phone numbers, emails, user IDs) in logs to protect PII.
"""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hypothesis import given, settings, strategies as st, assume

from app.utils.log_masker import LogMasker


# ============================================================================
# Strategies for generating test data
# ============================================================================

# Strategy for generating valid phone numbers (length >= 7)
valid_phone_strategy = st.text(
    alphabet="0123456789",
    min_size=7,
    max_size=20,
)

# Strategy for generating short phone numbers (length < 7)
short_phone_strategy = st.text(
    alphabet="0123456789",
    min_size=0,
    max_size=6,
)

# Strategy for generating valid email local parts (non-empty, no @)
email_local_part = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._+-",
    min_size=1,
    max_size=30,
)

# Strategy for generating valid email domains (e.g., "example.com")
# Use composite strategy to ensure domain always has a dot
email_domain = st.builds(
    lambda name, tld: f"{name}.{tld}",
    name=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        min_size=1,
        max_size=15,
    ),
    tld=st.sampled_from(["com", "org", "net", "io", "co", "cn", "edu", "gov"]),
)

# Strategy for generating valid user IDs (length > 6)
valid_user_id_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
    min_size=7,
    max_size=50,
)

# Strategy for generating short user IDs (length <= 6)
short_user_id_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
    min_size=0,
    max_size=6,
)


# ============================================================================
# Property 2: 手机号脱敏格式
# **Feature: system-optimization, Property 2: 手机号脱敏格式**
# **Validates: Requirements 2.1**
#
# For any valid phone number (length >= 7), the masked result should
# preserve the first 3 digits and last 4 digits, with "****" in between.
# ============================================================================


@settings(max_examples=100)
@given(phone=valid_phone_strategy)
def test_phone_masking_preserves_first_three_digits(phone: str) -> None:
    """
    **Feature: system-optimization, Property 2: 手机号脱敏格式**
    **Validates: Requirements 2.1**
    
    Property: For any phone number with length >= 7, the masked result
    should start with the first 3 digits of the original phone.
    """
    # Act
    masked = LogMasker.mask_phone(phone)
    
    # Assert: First 3 characters should be preserved
    assert masked.startswith(phone[:3]), (
        f"Masked phone should start with first 3 digits. "
        f"Original: '{phone}', Masked: '{masked}', Expected prefix: '{phone[:3]}'"
    )


@settings(max_examples=100)
@given(phone=valid_phone_strategy)
def test_phone_masking_preserves_last_four_digits(phone: str) -> None:
    """
    **Feature: system-optimization, Property 2: 手机号脱敏格式**
    **Validates: Requirements 2.1**
    
    Property: For any phone number with length >= 7, the masked result
    should end with the last 4 digits of the original phone.
    """
    # Act
    masked = LogMasker.mask_phone(phone)
    
    # Assert: Last 4 characters should be preserved
    assert masked.endswith(phone[-4:]), (
        f"Masked phone should end with last 4 digits. "
        f"Original: '{phone}', Masked: '{masked}', Expected suffix: '{phone[-4:]}'"
    )


@settings(max_examples=100)
@given(phone=valid_phone_strategy)
def test_phone_masking_contains_four_asterisks(phone: str) -> None:
    """
    **Feature: system-optimization, Property 2: 手机号脱敏格式**
    **Validates: Requirements 2.1**
    
    Property: For any phone number with length >= 7, the masked result
    should contain "****" in the middle.
    """
    # Act
    masked = LogMasker.mask_phone(phone)
    
    # Assert: Should contain "****"
    assert "****" in masked, (
        f"Masked phone should contain '****'. "
        f"Original: '{phone}', Masked: '{masked}'"
    )


@settings(max_examples=100)
@given(phone=valid_phone_strategy)
def test_phone_masking_has_correct_format(phone: str) -> None:
    """
    **Feature: system-optimization, Property 2: 手机号脱敏格式**
    **Validates: Requirements 2.1**
    
    Property: For any phone number with length >= 7, the masked result
    should have exactly the format: first3 + "****" + last4 (11 chars total).
    """
    # Act
    masked = LogMasker.mask_phone(phone)
    
    # Assert: Format should be exactly "XXX****XXXX"
    expected = f"{phone[:3]}****{phone[-4:]}"
    assert masked == expected, (
        f"Masked phone format incorrect. "
        f"Original: '{phone}', Got: '{masked}', Expected: '{expected}'"
    )
    assert len(masked) == 11, (
        f"Masked phone should be 11 characters. "
        f"Got length: {len(masked)}, Masked: '{masked}'"
    )


@settings(max_examples=100)
@given(phone=short_phone_strategy)
def test_short_phone_returns_asterisks(phone: str) -> None:
    """
    **Feature: system-optimization, Property 2: 手机号脱敏格式**
    **Validates: Requirements 2.1**
    
    Property: For any phone number with length < 7, the masked result
    should be "***".
    """
    # Act
    masked = LogMasker.mask_phone(phone)
    
    # Assert: Should return "***" for short phones
    assert masked == "***", (
        f"Short phone should be masked as '***'. "
        f"Original: '{phone}' (len={len(phone)}), Got: '{masked}'"
    )


# ============================================================================
# Property 3: 邮箱脱敏格式
# **Feature: system-optimization, Property 3: 邮箱脱敏格式**
# **Validates: Requirements 2.2**
#
# For any valid email (containing @), the masked result should preserve
# the first character of local part and the complete domain.
# ============================================================================


@settings(max_examples=100)
@given(local=email_local_part, domain=email_domain)
def test_email_masking_preserves_first_char(local: str, domain: str) -> None:
    """
    **Feature: system-optimization, Property 3: 邮箱脱敏格式**
    **Validates: Requirements 2.2**
    
    Property: For any valid email, the masked result should start with
    the first character of the local part.
    """
    # Arrange
    email = f"{local}@{domain}"
    
    # Act
    masked = LogMasker.mask_email(email)
    
    # Assert: Should start with first character of local part
    assert masked.startswith(local[0]), (
        f"Masked email should start with first char of local part. "
        f"Original: '{email}', Masked: '{masked}', Expected first char: '{local[0]}'"
    )


@settings(max_examples=100)
@given(local=email_local_part, domain=email_domain)
def test_email_masking_preserves_domain(local: str, domain: str) -> None:
    """
    **Feature: system-optimization, Property 3: 邮箱脱敏格式**
    **Validates: Requirements 2.2**
    
    Property: For any valid email, the masked result should preserve
    the complete domain after @.
    """
    # Arrange
    email = f"{local}@{domain}"
    
    # Act
    masked = LogMasker.mask_email(email)
    
    # Assert: Should end with @domain
    assert masked.endswith(f"@{domain}"), (
        f"Masked email should preserve domain. "
        f"Original: '{email}', Masked: '{masked}', Expected suffix: '@{domain}'"
    )


@settings(max_examples=100)
@given(local=email_local_part, domain=email_domain)
def test_email_masking_contains_asterisks(local: str, domain: str) -> None:
    """
    **Feature: system-optimization, Property 3: 邮箱脱敏格式**
    **Validates: Requirements 2.2**
    
    Property: For any valid email, the masked result should contain "***"
    to replace the local part (except first char).
    """
    # Arrange
    email = f"{local}@{domain}"
    
    # Act
    masked = LogMasker.mask_email(email)
    
    # Assert: Should contain "***"
    assert "***" in masked, (
        f"Masked email should contain '***'. "
        f"Original: '{email}', Masked: '{masked}'"
    )


@settings(max_examples=100)
@given(local=email_local_part, domain=email_domain)
def test_email_masking_has_correct_format(local: str, domain: str) -> None:
    """
    **Feature: system-optimization, Property 3: 邮箱脱敏格式**
    **Validates: Requirements 2.2**
    
    Property: For any valid email, the masked result should have exactly
    the format: first_char + "***" + "@" + domain.
    """
    # Arrange
    email = f"{local}@{domain}"
    
    # Act
    masked = LogMasker.mask_email(email)
    
    # Assert: Format should be exactly "X***@domain"
    expected = f"{local[0]}***@{domain}"
    assert masked == expected, (
        f"Masked email format incorrect. "
        f"Original: '{email}', Got: '{masked}', Expected: '{expected}'"
    )


@settings(max_examples=100)
@given(text=st.text(min_size=0, max_size=50).filter(lambda x: "@" not in x))
def test_invalid_email_returns_asterisks(text: str) -> None:
    """
    **Feature: system-optimization, Property 3: 邮箱脱敏格式**
    **Validates: Requirements 2.2**
    
    Property: For any string without @, the masked result should be "***".
    """
    # Act
    masked = LogMasker.mask_email(text)
    
    # Assert: Should return "***" for invalid emails
    assert masked == "***", (
        f"Invalid email (no @) should be masked as '***'. "
        f"Original: '{text}', Got: '{masked}'"
    )


# ============================================================================
# Property 4: 用户ID脱敏格式
# **Feature: system-optimization, Property 4: 用户ID脱敏格式**
# **Validates: Requirements 2.3**
#
# For any user ID with length > 6, the masked result should preserve
# the first 3 characters and last 3 characters, with "***" in between.
# ============================================================================


@settings(max_examples=100)
@given(user_id=valid_user_id_strategy)
def test_user_id_masking_preserves_first_three_chars(user_id: str) -> None:
    """
    **Feature: system-optimization, Property 4: 用户ID脱敏格式**
    **Validates: Requirements 2.3**
    
    Property: For any user ID with length > 6, the masked result should
    start with the first 3 characters of the original ID.
    """
    # Act
    masked = LogMasker.mask_user_id(user_id)
    
    # Assert: First 3 characters should be preserved
    assert masked.startswith(user_id[:3]), (
        f"Masked user ID should start with first 3 chars. "
        f"Original: '{user_id}', Masked: '{masked}', Expected prefix: '{user_id[:3]}'"
    )


@settings(max_examples=100)
@given(user_id=valid_user_id_strategy)
def test_user_id_masking_preserves_last_three_chars(user_id: str) -> None:
    """
    **Feature: system-optimization, Property 4: 用户ID脱敏格式**
    **Validates: Requirements 2.3**
    
    Property: For any user ID with length > 6, the masked result should
    end with the last 3 characters of the original ID.
    """
    # Act
    masked = LogMasker.mask_user_id(user_id)
    
    # Assert: Last 3 characters should be preserved
    assert masked.endswith(user_id[-3:]), (
        f"Masked user ID should end with last 3 chars. "
        f"Original: '{user_id}', Masked: '{masked}', Expected suffix: '{user_id[-3:]}'"
    )


@settings(max_examples=100)
@given(user_id=valid_user_id_strategy)
def test_user_id_masking_contains_three_asterisks(user_id: str) -> None:
    """
    **Feature: system-optimization, Property 4: 用户ID脱敏格式**
    **Validates: Requirements 2.3**
    
    Property: For any user ID with length > 6, the masked result should
    contain "***" in the middle.
    """
    # Act
    masked = LogMasker.mask_user_id(user_id)
    
    # Assert: Should contain "***"
    assert "***" in masked, (
        f"Masked user ID should contain '***'. "
        f"Original: '{user_id}', Masked: '{masked}'"
    )


@settings(max_examples=100)
@given(user_id=valid_user_id_strategy)
def test_user_id_masking_has_correct_format(user_id: str) -> None:
    """
    **Feature: system-optimization, Property 4: 用户ID脱敏格式**
    **Validates: Requirements 2.3**
    
    Property: For any user ID with length > 6, the masked result should
    have exactly the format: first3 + "***" + last3 (9 chars total).
    """
    # Act
    masked = LogMasker.mask_user_id(user_id)
    
    # Assert: Format should be exactly "XXX***XXX"
    expected = f"{user_id[:3]}***{user_id[-3:]}"
    assert masked == expected, (
        f"Masked user ID format incorrect. "
        f"Original: '{user_id}', Got: '{masked}', Expected: '{expected}'"
    )
    assert len(masked) == 9, (
        f"Masked user ID should be 9 characters. "
        f"Got length: {len(masked)}, Masked: '{masked}'"
    )


@settings(max_examples=100)
@given(user_id=short_user_id_strategy)
def test_short_user_id_returns_asterisks(user_id: str) -> None:
    """
    **Feature: system-optimization, Property 4: 用户ID脱敏格式**
    **Validates: Requirements 2.3**
    
    Property: For any user ID with length <= 6, the masked result
    should be "***".
    """
    # Act
    masked = LogMasker.mask_user_id(user_id)
    
    # Assert: Should return "***" for short user IDs
    assert masked == "***", (
        f"Short user ID should be masked as '***'. "
        f"Original: '{user_id}' (len={len(user_id)}), Got: '{masked}'"
    )

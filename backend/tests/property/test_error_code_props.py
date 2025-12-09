"""Property-based tests for ErrorCode enum serialization.

**Feature: system-optimization, Property 10: ErrorCode 序列化**

This module tests that ErrorCode enum values serialize correctly to JSON.

Requirements:
- 10.1: WHEN 定义 API 错误码时 THEN PopGraph SHALL 使用继承自 str 和 Enum 的 ErrorCode 类
- 10.2: WHEN 返回错误响应时 THEN PopGraph SHALL 使用 ErrorCode 枚举值而非字符串字面量
- 10.3: WHEN 序列化错误码到 JSON 时 THEN PopGraph SHALL 输出枚举的字符串值
"""

import json
import sys
from pathlib import Path
from enum import Enum

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from hypothesis import given, settings, strategies as st

from app.api.auth import ErrorCode


# ============================================================================
# Property 10: ErrorCode 序列化
# **Feature: system-optimization, Property 10: ErrorCode 序列化**
# **Validates: Requirements 10.3**
#
# For any ErrorCode enum value, JSON serialization SHALL output its string value
# ============================================================================


# Strategy for selecting any ErrorCode enum member
error_code_strategy = st.sampled_from(list(ErrorCode))


@settings(max_examples=100)
@given(error_code=error_code_strategy)
def test_error_code_json_serialization_outputs_string_value(
    error_code: ErrorCode,
) -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.3**
    
    Property: For any ErrorCode enum value, JSON serialization SHALL output
    its string value (not the enum representation).
    """
    # Arrange: Create a dict with the error code
    data = {"code": error_code}
    
    # Act: Serialize to JSON
    json_str = json.dumps(data)
    
    # Assert: The JSON should contain the string value, not enum representation
    parsed = json.loads(json_str)
    assert parsed["code"] == error_code.value, (
        f"JSON serialization should output string value '{error_code.value}', "
        f"got '{parsed['code']}'"
    )


@settings(max_examples=100)
@given(error_code=error_code_strategy)
def test_error_code_is_str_subclass(
    error_code: ErrorCode,
) -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.1**
    
    Property: For any ErrorCode enum value, it SHALL be an instance of str.
    """
    # Assert: ErrorCode should be a str subclass
    assert isinstance(error_code, str), (
        f"ErrorCode should be a str subclass, got {type(error_code)}"
    )


@settings(max_examples=100)
@given(error_code=error_code_strategy)
def test_error_code_is_enum_subclass(
    error_code: ErrorCode,
) -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.1**
    
    Property: For any ErrorCode enum value, it SHALL be an instance of Enum.
    """
    # Assert: ErrorCode should be an Enum subclass
    assert isinstance(error_code, Enum), (
        f"ErrorCode should be an Enum subclass, got {type(error_code)}"
    )


@settings(max_examples=100)
@given(error_code=error_code_strategy)
def test_error_code_value_equals_name(
    error_code: ErrorCode,
) -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.2**
    
    Property: For any ErrorCode enum value, the value SHALL equal the name
    (ensuring consistent string representation).
    """
    # Assert: Value should equal name for consistent serialization
    assert error_code.value == error_code.name, (
        f"ErrorCode value '{error_code.value}' should equal name '{error_code.name}'"
    )


@settings(max_examples=100)
@given(error_code=error_code_strategy)
def test_error_code_direct_string_comparison(
    error_code: ErrorCode,
) -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.2**
    
    Property: For any ErrorCode enum value, direct string comparison with
    its value SHALL return True (due to str inheritance).
    """
    # Assert: Direct comparison with string value should work
    assert error_code == error_code.value, (
        f"ErrorCode '{error_code}' should equal its value '{error_code.value}'"
    )


@settings(max_examples=100)
@given(error_code=error_code_strategy)
def test_error_code_in_dict_serializes_correctly(
    error_code: ErrorCode,
) -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.3**
    
    Property: For any ErrorCode in a nested dict structure, JSON serialization
    SHALL output the string value at all levels.
    """
    # Arrange: Create a nested dict structure (like API error response)
    data = {
        "detail": {
            "code": error_code,
            "message": "Test error message",
        }
    }
    
    # Act: Serialize to JSON
    json_str = json.dumps(data)
    
    # Assert: The nested code should be the string value
    parsed = json.loads(json_str)
    assert parsed["detail"]["code"] == error_code.value, (
        f"Nested ErrorCode should serialize to '{error_code.value}', "
        f"got '{parsed['detail']['code']}'"
    )


@settings(max_examples=100)
@given(error_code=error_code_strategy)
def test_error_code_in_list_serializes_correctly(
    error_code: ErrorCode,
) -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.3**
    
    Property: For any ErrorCode in a list, JSON serialization SHALL output
    the string value.
    """
    # Arrange: Create a list with error codes
    data = {"codes": [error_code]}
    
    # Act: Serialize to JSON
    json_str = json.dumps(data)
    
    # Assert: The list element should be the string value
    parsed = json.loads(json_str)
    assert parsed["codes"][0] == error_code.value, (
        f"ErrorCode in list should serialize to '{error_code.value}', "
        f"got '{parsed['codes'][0]}'"
    )


def test_error_code_class_inherits_from_str_and_enum() -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.1**
    
    Verify that ErrorCode class properly inherits from both str and Enum.
    """
    # Assert: ErrorCode should inherit from both str and Enum
    assert issubclass(ErrorCode, str), "ErrorCode should inherit from str"
    assert issubclass(ErrorCode, Enum), "ErrorCode should inherit from Enum"


def test_error_code_has_expected_members() -> None:
    """
    **Feature: system-optimization, Property 10: ErrorCode 序列化**
    **Validates: Requirements 10.1**
    
    Verify that ErrorCode has all expected error code members.
    """
    # Expected error codes based on design document
    expected_codes = {
        "INVALID_PHONE",
        "INVALID_EMAIL",
        "INVALID_CODE",
        "WEAK_PASSWORD",
        "INPUT_TOO_LONG",
        "INVALID_CREDENTIALS",
        "UNAUTHORIZED",
        "PHONE_EXISTS",
        "EMAIL_EXISTS",
        "USER_NOT_FOUND",
        "TOKEN_EXPIRED",
        "TOKEN_INVALID",
        "TOKEN_REVOKED",
        "RATE_LIMITED",
    }
    
    actual_codes = {member.name for member in ErrorCode}
    
    # Assert: All expected codes should be present
    assert expected_codes.issubset(actual_codes), (
        f"Missing error codes: {expected_codes - actual_codes}"
    )

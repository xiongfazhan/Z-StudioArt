"""Input validation utilities for PopGraph system.

This module provides input validation and length limiting functionality
to protect against malicious input attacks.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ValidationLimits:
    """Validation limit constants for various input types.
    
    Attributes:
        MAX_PHONE_LENGTH: Maximum allowed length for phone numbers (20 chars)
        MAX_EMAIL_LENGTH: Maximum allowed length for email addresses (255 chars)
        MAX_PASSWORD_LENGTH: Maximum allowed length for passwords (128 chars)
        MAX_CONTENT_LENGTH: Maximum allowed length for content filter text (10000 chars)
    """
    MAX_PHONE_LENGTH: int = 20
    MAX_EMAIL_LENGTH: int = 255
    MAX_PASSWORD_LENGTH: int = 128
    MAX_CONTENT_LENGTH: int = 10000


class InputValidator:
    """Input validator for validating user inputs.
    
    Provides methods to validate various input types against length limits
    to prevent malicious input attacks.
    """
    
    LIMITS = ValidationLimits()
    
    @classmethod
    def validate_phone_length(cls, phone: str) -> bool:
        """Validate phone number length.
        
        Args:
            phone: Phone number string to validate
            
        Returns:
            True if phone length is within limit, False otherwise
        """
        return len(phone) <= cls.LIMITS.MAX_PHONE_LENGTH
    
    @classmethod
    def validate_email_length(cls, email: str) -> bool:
        """Validate email address length.
        
        Args:
            email: Email address string to validate
            
        Returns:
            True if email length is within limit, False otherwise
        """
        return len(email) <= cls.LIMITS.MAX_EMAIL_LENGTH
    
    @classmethod
    def validate_password_length(cls, password: str) -> bool:
        """Validate password length.
        
        Args:
            password: Password string to validate
            
        Returns:
            True if password length is within limit, False otherwise
        """
        return len(password) <= cls.LIMITS.MAX_PASSWORD_LENGTH
    
    @classmethod
    def validate_content_length(cls, content: str) -> bool:
        """Validate content filter text length.
        
        Args:
            content: Content text string to validate
            
        Returns:
            True if content length is within limit, False otherwise
        """
        return len(content) <= cls.LIMITS.MAX_CONTENT_LENGTH
    
    @classmethod
    def validate_phone(cls, phone: str) -> Tuple[bool, str]:
        """Validate phone number with error message.
        
        Args:
            phone: Phone number string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.validate_phone_length(phone):
            return False, f"Phone number exceeds maximum length of {cls.LIMITS.MAX_PHONE_LENGTH} characters"
        return True, ""
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, str]:
        """Validate email address with error message.
        
        Args:
            email: Email address string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.validate_email_length(email):
            return False, f"Email address exceeds maximum length of {cls.LIMITS.MAX_EMAIL_LENGTH} characters"
        return True, ""
    
    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, str]:
        """Validate password with error message.
        
        Args:
            password: Password string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.validate_password_length(password):
            return False, f"Password exceeds maximum length of {cls.LIMITS.MAX_PASSWORD_LENGTH} characters"
        return True, ""
    
    @classmethod
    def validate_content(cls, content: str) -> Tuple[bool, str]:
        """Validate content filter text with error message.
        
        Args:
            content: Content text string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.validate_content_length(content):
            return False, f"Content exceeds maximum length of {cls.LIMITS.MAX_CONTENT_LENGTH} characters"
        return True, ""

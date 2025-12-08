"""
日志脱敏工具模块

提供对敏感信息（手机号、邮箱、用户ID）的脱敏处理功能，
确保日志中不会泄露用户的个人身份信息（PII）。

Requirements: 2.1, 2.2, 2.3
"""


class LogMasker:
    """日志脱敏工具类
    
    提供静态方法对各类敏感信息进行脱敏处理：
    - 手机号：138****1234 格式
    - 邮箱：u***@example.com 格式
    - 用户ID：abc***xyz 格式
    """
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """脱敏手机号
        
        将手机号脱敏为 "138****1234" 格式，保留前3位和后4位。
        
        Args:
            phone: 原始手机号字符串
            
        Returns:
            脱敏后的手机号字符串。如果手机号长度小于7，返回 "***"
            
        Examples:
            >>> LogMasker.mask_phone("13812345678")
            '138****5678'
            >>> LogMasker.mask_phone("123")
            '***'
        """
        if len(phone) >= 7:
            return f"{phone[:3]}****{phone[-4:]}"
        return "***"
    
    @staticmethod
    def mask_email(email: str) -> str:
        """脱敏邮箱
        
        将邮箱脱敏为 "u***@example.com" 格式，保留首字母和完整域名。
        
        Args:
            email: 原始邮箱字符串
            
        Returns:
            脱敏后的邮箱字符串。如果邮箱不包含 @，返回 "***"
            
        Examples:
            >>> LogMasker.mask_email("user@example.com")
            'u***@example.com'
            >>> LogMasker.mask_email("invalid")
            '***'
        """
        if "@" in email:
            local, domain = email.split("@", 1)
            masked_local = f"{local[0]}***" if local else "***"
            return f"{masked_local}@{domain}"
        return "***"
    
    @staticmethod
    def mask_user_id(user_id: str) -> str:
        """脱敏用户ID
        
        将用户ID脱敏为 "abc***xyz" 格式，保留前3位和后3位。
        
        Args:
            user_id: 原始用户ID字符串
            
        Returns:
            脱敏后的用户ID字符串。如果用户ID长度不超过6，返回 "***"
            
        Examples:
            >>> LogMasker.mask_user_id("abcdefghij")
            'abc***hij'
            >>> LogMasker.mask_user_id("abc")
            '***'
        """
        if len(user_id) > 6:
            return f"{user_id[:3]}***{user_id[-3:]}"
        return "***"

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
    
    # 脱敏配置常量
    PHONE_MIN_LENGTH = 7
    PHONE_PREFIX_LENGTH = 3
    PHONE_SUFFIX_LENGTH = 4
    PHONE_MASK = "****"
    
    USER_ID_MIN_LENGTH = 7  # > 6 等价于 >= 7
    USER_ID_PREFIX_LENGTH = 3
    USER_ID_SUFFIX_LENGTH = 3
    USER_ID_MASK = "***"
    
    DEFAULT_MASK = "***"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """脱敏手机号
        
        将手机号脱敏为 "138****1234" 格式，保留前3位和后4位。
        
        Args:
            phone: 原始手机号字符串
            
        Returns:
            脱敏后的手机号字符串。如果手机号长度小于7或输入无效，返回 "***"
            
        Examples:
            >>> LogMasker.mask_phone("13812345678")
            '138****5678'
            >>> LogMasker.mask_phone("123")
            '***'
        """
        if not isinstance(phone, str) or not phone:
            return LogMasker.DEFAULT_MASK
        if len(phone) >= LogMasker.PHONE_MIN_LENGTH:
            return (
                f"{phone[:LogMasker.PHONE_PREFIX_LENGTH]}"
                f"{LogMasker.PHONE_MASK}"
                f"{phone[-LogMasker.PHONE_SUFFIX_LENGTH:]}"
            )
        return LogMasker.DEFAULT_MASK
    
    @staticmethod
    def mask_email(email: str) -> str:
        """脱敏邮箱
        
        将邮箱脱敏为 "u***@example.com" 格式，保留首字母和完整域名。
        
        Args:
            email: 原始邮箱字符串
            
        Returns:
            脱敏后的邮箱字符串。如果邮箱不包含 @ 或输入无效，返回 "***"
            
        Examples:
            >>> LogMasker.mask_email("user@example.com")
            'u***@example.com'
            >>> LogMasker.mask_email("invalid")
            '***'
        """
        if not isinstance(email, str) or "@" not in email:
            return LogMasker.DEFAULT_MASK
        
        local, domain = email.split("@", 1)
        if not local:
            return f"{LogMasker.DEFAULT_MASK}@{domain}"
        
        return f"{local[0]}***@{domain}"
    
    @staticmethod
    def mask_user_id(user_id: str) -> str:
        """脱敏用户ID
        
        将用户ID脱敏为 "abc***xyz" 格式，保留前3位和后3位。
        
        Args:
            user_id: 原始用户ID字符串
            
        Returns:
            脱敏后的用户ID字符串。如果用户ID长度不超过6或输入无效，返回 "***"
            
        Examples:
            >>> LogMasker.mask_user_id("abcdefghij")
            'abc***hij'
            >>> LogMasker.mask_user_id("abc")
            '***'
        """
        if not isinstance(user_id, str) or not user_id:
            return LogMasker.DEFAULT_MASK
        if len(user_id) >= LogMasker.USER_ID_MIN_LENGTH:
            return (
                f"{user_id[:LogMasker.USER_ID_PREFIX_LENGTH]}"
                f"{LogMasker.USER_ID_MASK}"
                f"{user_id[-LogMasker.USER_ID_SUFFIX_LENGTH:]}"
            )
        return LogMasker.DEFAULT_MASK
    
    @staticmethod
    def mask_log_message(
        message: str,
        phone: str | None = None,
        email: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """批量脱敏日志消息中的敏感信息
        
        Args:
            message: 日志消息模板，使用 {phone}、{email}、{user_id} 占位符
            phone: 需要脱敏的手机号
            email: 需要脱敏的邮箱
            user_id: 需要脱敏的用户ID
            
        Returns:
            脱敏后的日志消息
            
        Examples:
            >>> LogMasker.mask_log_message(
            ...     "用户 {user_id} 使用手机 {phone} 登录",
            ...     phone="13812345678",
            ...     user_id="user123456789"
            ... )
            '用户 use***789 使用手机 138****5678 登录'
        """
        if not isinstance(message, str):
            return ""
        
        result = message
        if phone is not None:
            result = result.replace("{phone}", LogMasker.mask_phone(phone))
        if email is not None:
            result = result.replace("{email}", LogMasker.mask_email(email))
        if user_id is not None:
            result = result.replace("{user_id}", LogMasker.mask_user_id(user_id))
        return result

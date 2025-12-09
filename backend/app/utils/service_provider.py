"""Thread-safe Service Provider for PopGraph.

This module implements a generic, thread-safe singleton provider using
double-checked locking pattern.

Requirements:
- 5.1: WHEN 多线程同时调用 get_auth_service() 时 THEN PopGraph SHALL 返回同一个 AuthService 实例
- 5.2: WHEN 多线程同时调用 get_payment_service() 时 THEN PopGraph SHALL 返回同一个 PaymentService 实例
- 5.3: WHEN 多线程同时调用 get_template_service() 时 THEN PopGraph SHALL 返回同一个 TemplateService 实例
- 5.4: WHEN 多线程同时调用 get_zimage_client() 时 THEN PopGraph SHALL 返回同一个 ZImageTurboClient 实例
- 5.5: WHEN 测试需要重置单例时 THEN PopGraph SHALL 提供 reset() 方法清除实例
"""

import threading
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar('T')


class ServiceProvider(Generic[T]):
    """Thread-safe service provider using double-checked locking.
    
    This class provides a generic way to create singleton instances
    in a thread-safe manner. It uses the double-checked locking pattern
    to minimize lock contention while ensuring thread safety.
    
    Attributes:
        _factory: Callable that creates the service instance
        _instance: The singleton instance (or None if not created)
        _lock: Threading lock for synchronization
    
    Example:
        >>> def create_my_service():
        ...     return MyService()
        >>> provider = ServiceProvider(create_my_service)
        >>> service1 = provider.get_instance()
        >>> service2 = provider.get_instance()
        >>> assert service1 is service2  # Same instance
    """
    
    def __init__(self, factory: Callable[[], T]) -> None:
        """Initialize the service provider.
        
        Args:
            factory: A callable that creates the service instance.
                     This will be called at most once (lazily).
        """
        self._factory = factory
        self._instance: Optional[T] = None
        self._lock = threading.Lock()
    
    def get_instance(self) -> T:
        """Get the singleton service instance.
        
        Uses double-checked locking pattern:
        1. First check without lock (fast path for already-initialized case)
        2. Acquire lock and check again (ensures thread safety)
        3. Create instance if still None
        
        Returns:
            The singleton service instance
            
        Requirements:
            - 5.1, 5.2, 5.3, 5.4: Return same instance for concurrent calls
        """
        # First check (without lock) - fast path
        if self._instance is None:
            # Acquire lock for thread safety
            with self._lock:
                # Second check (with lock) - ensures only one creation
                if self._instance is None:
                    self._instance = self._factory()
        return self._instance
    
    def reset(self) -> None:
        """Reset the singleton instance.
        
        This method is primarily intended for testing purposes,
        allowing tests to start with a fresh instance.
        
        Thread-safe: acquires lock before clearing instance.
        
        Requirements:
            - 5.5: Provide reset() method for testing
        """
        with self._lock:
            self._instance = None
    
    def is_initialized(self) -> bool:
        """Check if the service instance has been created.
        
        Returns:
            True if instance exists, False otherwise
        """
        return self._instance is not None

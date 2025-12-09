"""Property-based tests for ServiceProvider.

**Feature: system-optimization, Property 1: 单例一致性**

This module tests that the ServiceProvider correctly maintains singleton
instances across concurrent access from multiple threads.

Property 1 validates Requirements 5.1, 5.2, 5.3, 5.4:
- WHEN 多线程同时调用 get_instance() 时 THEN PopGraph SHALL 返回同一个实例
"""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import pytest
from hypothesis import given, settings, strategies as st

from app.utils.service_provider import ServiceProvider


# ============================================================================
# Test Service Classes
# ============================================================================

class DummyService:
    """A simple service class for testing singleton behavior."""
    
    _creation_count = 0
    _lock = threading.Lock()
    
    def __init__(self):
        with DummyService._lock:
            DummyService._creation_count += 1
        self.instance_id = id(self)
    
    @classmethod
    def reset_creation_count(cls):
        with cls._lock:
            cls._creation_count = 0
    
    @classmethod
    def get_creation_count(cls) -> int:
        with cls._lock:
            return cls._creation_count


class SlowInitService:
    """A service with slow initialization to test race conditions."""
    
    def __init__(self, delay: float = 0.01):
        import time
        time.sleep(delay)  # Simulate slow initialization
        self.instance_id = id(self)


# ============================================================================
# Strategies for generating test data
# ============================================================================

# Strategy for number of concurrent threads
thread_count_strategy = st.integers(min_value=2, max_value=20)

# Strategy for number of calls per thread
calls_per_thread_strategy = st.integers(min_value=1, max_value=10)


# ============================================================================
# Property 1: 单例一致性
# **Feature: system-optimization, Property 1: 单例一致性**
# **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
#
# For any ServiceProvider and any number of concurrent calls,
# all calls SHALL return the same service instance.
# ============================================================================


@settings(max_examples=100)
@given(
    num_threads=thread_count_strategy,
    calls_per_thread=calls_per_thread_strategy,
)
def test_property1_singleton_consistency(
    num_threads: int,
    calls_per_thread: int,
) -> None:
    """
    **Feature: system-optimization, Property 1: 单例一致性**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    
    Property: For any ServiceProvider and any number of concurrent calls,
    all calls must return the exact same instance.
    
    This validates that the double-checked locking pattern correctly
    ensures singleton behavior under concurrent access.
    """
    # Arrange
    DummyService.reset_creation_count()
    provider = ServiceProvider(DummyService)
    instances: List[DummyService] = []
    instances_lock = threading.Lock()
    
    def get_instance_task():
        """Task that gets instance multiple times and records them."""
        local_instances = []
        for _ in range(calls_per_thread):
            instance = provider.get_instance()
            local_instances.append(instance)
        
        with instances_lock:
            instances.extend(local_instances)
    
    # Act: Run concurrent threads
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(get_instance_task) for _ in range(num_threads)]
        for future in as_completed(futures):
            future.result()  # Raise any exceptions
    
    # Assert: All instances should be the same object
    assert len(instances) == num_threads * calls_per_thread, (
        f"Expected {num_threads * calls_per_thread} instances, got {len(instances)}"
    )
    
    first_instance = instances[0]
    for i, instance in enumerate(instances):
        assert instance is first_instance, (
            f"Instance at index {i} is different from first instance. "
            f"Expected id={id(first_instance)}, got id={id(instance)}"
        )
    
    # Assert: Factory should only be called once
    creation_count = DummyService.get_creation_count()
    assert creation_count == 1, (
        f"Factory should be called exactly once, but was called {creation_count} times"
    )


@settings(max_examples=100)
@given(
    num_threads=st.integers(min_value=5, max_value=15),
)
def test_property1_singleton_with_slow_init(
    num_threads: int,
) -> None:
    """
    **Feature: system-optimization, Property 1: 单例一致性**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    
    Property: Even with slow initialization, all concurrent calls
    must return the same instance.
    
    This tests the race condition scenario where multiple threads
    try to initialize the service simultaneously.
    """
    # Arrange
    provider = ServiceProvider(lambda: SlowInitService(delay=0.01))
    instances: List[SlowInitService] = []
    instances_lock = threading.Lock()
    barrier = threading.Barrier(num_threads)
    
    def get_instance_task():
        """Task that waits at barrier then gets instance."""
        barrier.wait()  # Synchronize all threads to start together
        instance = provider.get_instance()
        with instances_lock:
            instances.append(instance)
    
    # Act: Run concurrent threads
    threads = [threading.Thread(target=get_instance_task) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Assert: All instances should be the same object
    assert len(instances) == num_threads, (
        f"Expected {num_threads} instances, got {len(instances)}"
    )
    
    first_instance = instances[0]
    for i, instance in enumerate(instances):
        assert instance is first_instance, (
            f"Instance at index {i} is different from first instance"
        )


@settings(max_examples=100)
@given(
    num_resets=st.integers(min_value=1, max_value=5),
)
def test_property1_reset_creates_new_instance(
    num_resets: int,
) -> None:
    """
    **Feature: system-optimization, Property 1: 单例一致性**
    **Validates: Requirements 5.5**
    
    Property: After reset(), the next get_instance() call must
    create a new instance.
    
    This validates the reset functionality for testing purposes.
    """
    # Arrange
    DummyService.reset_creation_count()
    provider = ServiceProvider(DummyService)
    
    previous_instances = []
    
    # Act & Assert: Each reset should create a new instance
    for i in range(num_resets):
        instance = provider.get_instance()
        
        # Verify this is a new instance (not in previous list)
        for prev in previous_instances:
            assert instance is not prev, (
                f"After reset {i}, got same instance as before"
            )
        
        previous_instances.append(instance)
        provider.reset()
    
    # Assert: Factory should be called once per reset cycle
    creation_count = DummyService.get_creation_count()
    assert creation_count == num_resets, (
        f"Factory should be called {num_resets} times, "
        f"but was called {creation_count} times"
    )


@settings(max_examples=100)
@given(
    num_threads=st.integers(min_value=2, max_value=10),
)
def test_property1_reset_thread_safety(
    num_threads: int,
) -> None:
    """
    **Feature: system-optimization, Property 1: 单例一致性**
    **Validates: Requirements 5.5**
    
    Property: reset() should be thread-safe and not cause
    data corruption when called concurrently with get_instance().
    
    This tests that reset doesn't cause issues when called
    while other threads are accessing the instance.
    """
    # Arrange
    provider = ServiceProvider(DummyService)
    errors: List[Exception] = []
    errors_lock = threading.Lock()
    
    def getter_task():
        """Task that repeatedly gets instances."""
        try:
            for _ in range(10):
                instance = provider.get_instance()
                assert instance is not None, "get_instance returned None"
        except Exception as e:
            with errors_lock:
                errors.append(e)
    
    def resetter_task():
        """Task that periodically resets the provider."""
        try:
            for _ in range(3):
                provider.reset()
        except Exception as e:
            with errors_lock:
                errors.append(e)
    
    # Act: Run getters and resetters concurrently
    threads = []
    for _ in range(num_threads - 1):
        threads.append(threading.Thread(target=getter_task))
    threads.append(threading.Thread(target=resetter_task))
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Assert: No errors should occur
    assert len(errors) == 0, (
        f"Concurrent access caused errors: {errors}"
    )


@settings(max_examples=100)
@given(
    num_calls=st.integers(min_value=1, max_value=50),
)
def test_property1_is_initialized_consistency(
    num_calls: int,
) -> None:
    """
    **Feature: system-optimization, Property 1: 单例一致性**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    
    Property: is_initialized() should return False before first
    get_instance() call and True after.
    """
    # Arrange
    provider = ServiceProvider(DummyService)
    
    # Assert: Not initialized before first call
    assert provider.is_initialized() is False, (
        "Provider should not be initialized before get_instance()"
    )
    
    # Act: Call get_instance multiple times
    for _ in range(num_calls):
        provider.get_instance()
    
    # Assert: Should be initialized after calls
    assert provider.is_initialized() is True, (
        "Provider should be initialized after get_instance()"
    )
    
    # Act: Reset
    provider.reset()
    
    # Assert: Not initialized after reset
    assert provider.is_initialized() is False, (
        "Provider should not be initialized after reset()"
    )

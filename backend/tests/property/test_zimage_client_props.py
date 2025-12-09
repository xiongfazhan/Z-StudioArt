"""Property-based tests for Z-Image-Turbo Client.

**Feature: popgraph, Property 6: 输出尺寸正确性**
**Feature: popgraph, Property 3: 批量生成数量一致性**

This module tests that the AspectRatioCalculator correctly calculates
image dimensions based on the requested aspect ratio, and that batch
generation returns the correct number of images.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hypothesis import given, settings, strategies as st

from app.clients.zimage_client import (
    AspectRatioCalculator,
    ZImageTurboClient,
    calculate_image_dimensions,
    validate_image_dimensions,
    DEFAULT_BASE_SIZE,
)
from app.models.schemas import GeneratedImageData, GenerationOptions


# ============================================================================
# Strategies for generating test data
# ============================================================================

# Aspect ratio strategy - all supported ratios
aspect_ratio = st.sampled_from(["1:1", "9:16", "16:9"])

# Base size strategy - reasonable range for image generation
# Using powers of 2 and common sizes for AI image generation
base_size = st.integers(min_value=256, max_value=2048)


# ============================================================================
# Property 6: 输出尺寸正确性
# **Feature: popgraph, Property 6: 输出尺寸正确性**
# **Validates: Requirements 5.1, 5.2, 5.3**
#
# For any poster generation request with a specified aspect ratio, the
# generated image dimensions SHALL match the requested ratio:
# - 1:1 → width equals height
# - 9:16 → width/height equals 9/16 (±1px tolerance)
# - 16:9 → width/height equals 16/9 (±1px tolerance)
# ============================================================================


@settings(max_examples=100)
@given(
    base=base_size,
)
def test_square_ratio_produces_equal_dimensions(base: int) -> None:
    """
    **Feature: popgraph, Property 6: 输出尺寸正确性**
    **Validates: Requirements 5.1**
    
    Property: For any 1:1 aspect ratio request, the generated dimensions
    must have width equal to height (suitable for WeChat Moments).
    """
    # Act
    width, height = calculate_image_dimensions("1:1", base)
    
    # Assert: Width must equal height for 1:1 ratio
    assert width == height, (
        f"1:1 ratio should produce equal dimensions, got width={width}, height={height}"
    )


@settings(max_examples=100)
@given(
    base=base_size,
)
def test_mobile_poster_ratio_produces_correct_proportions(base: int) -> None:
    """
    **Feature: popgraph, Property 6: 输出尺寸正确性**
    **Validates: Requirements 5.2**
    
    Property: For any 9:16 aspect ratio request, the generated dimensions
    must satisfy width/height ≈ 9/16 (suitable for phone screens).
    The ±1px tolerance means the actual ratio can deviate by up to 1 pixel
    in either dimension.
    """
    # Act
    width, height = calculate_image_dimensions("9:16", base)
    
    # Assert: Ratio must be approximately 9/16 with ±1px tolerance
    # ±1px tolerance means: (width±1)/(height±1) should be able to match 9/16
    # This translates to checking if the ratio is within acceptable bounds
    expected_ratio = 9 / 16
    actual_ratio = width / height
    
    # Calculate tolerance based on ±1px in both dimensions
    # Worst case: (width+1)/(height-1) or (width-1)/(height+1)
    max_ratio = (width + 1) / max(height - 1, 1)
    min_ratio = max(width - 1, 1) / (height + 1)
    
    # The expected ratio should fall within the tolerance range
    # OR the actual ratio should be close enough to expected
    ratio_in_range = min_ratio <= expected_ratio <= max_ratio
    
    assert ratio_in_range, (
        f"9:16 ratio should produce width/height ≈ {expected_ratio}, "
        f"got {actual_ratio} (width={width}, height={height}), "
        f"acceptable range: [{min_ratio}, {max_ratio}]"
    )


@settings(max_examples=100)
@given(
    base=base_size,
)
def test_video_cover_ratio_produces_correct_proportions(base: int) -> None:
    """
    **Feature: popgraph, Property 6: 输出尺寸正确性**
    **Validates: Requirements 5.3**
    
    Property: For any 16:9 aspect ratio request, the generated dimensions
    must satisfy width/height ≈ 16/9 (suitable for video thumbnails).
    The ±1px tolerance means the actual ratio can deviate by up to 1 pixel
    in either dimension.
    """
    # Act
    width, height = calculate_image_dimensions("16:9", base)
    
    # Assert: Ratio must be approximately 16/9 with ±1px tolerance
    expected_ratio = 16 / 9
    actual_ratio = width / height
    
    # Calculate tolerance based on ±1px in both dimensions
    max_ratio = (width + 1) / max(height - 1, 1)
    min_ratio = max(width - 1, 1) / (height + 1)
    
    ratio_in_range = min_ratio <= expected_ratio <= max_ratio
    
    assert ratio_in_range, (
        f"16:9 ratio should produce width/height ≈ {expected_ratio}, "
        f"got {actual_ratio} (width={width}, height={height}), "
        f"acceptable range: [{min_ratio}, {max_ratio}]"
    )


@settings(max_examples=100)
@given(
    ratio=aspect_ratio,
    base=base_size,
)
def test_calculated_dimensions_pass_validation(ratio: str, base: int) -> None:
    """
    **Feature: popgraph, Property 6: 输出尺寸正确性**
    **Validates: Requirements 5.1, 5.2, 5.3**
    
    Property: For any aspect ratio and base size, the dimensions calculated
    by calculate_image_dimensions must pass validation by validate_image_dimensions.
    This is a round-trip consistency property.
    """
    # Act
    width, height = calculate_image_dimensions(ratio, base)
    is_valid = validate_image_dimensions(width, height, ratio)
    
    # Assert: Calculated dimensions must always be valid
    assert is_valid, (
        f"Calculated dimensions (width={width}, height={height}) for ratio {ratio} "
        f"failed validation"
    )


@settings(max_examples=100)
@given(
    ratio=aspect_ratio,
    base=base_size,
)
def test_dimensions_are_positive_integers(ratio: str, base: int) -> None:
    """
    **Feature: popgraph, Property 6: 输出尺寸正确性**
    **Validates: Requirements 5.1, 5.2, 5.3**
    
    Property: For any aspect ratio request, the generated dimensions
    must be positive integers (valid pixel dimensions).
    """
    # Act
    width, height = calculate_image_dimensions(ratio, base)
    
    # Assert: Both dimensions must be positive integers
    assert isinstance(width, int), f"Width must be an integer, got {type(width)}"
    assert isinstance(height, int), f"Height must be an integer, got {type(height)}"
    assert width > 0, f"Width must be positive, got {width}"
    assert height > 0, f"Height must be positive, got {height}"


@settings(max_examples=100)
@given(
    ratio=aspect_ratio,
    base=base_size,
)
def test_max_dimension_equals_base_size(ratio: str, base: int) -> None:
    """
    **Feature: popgraph, Property 6: 输出尺寸正确性**
    **Validates: Requirements 5.1, 5.2, 5.3**
    
    Property: For any aspect ratio request, the maximum dimension (width or
    height) should equal the base_size parameter, ensuring consistent output
    quality across different ratios.
    """
    # Act
    width, height = calculate_image_dimensions(ratio, base)
    
    # Assert: Maximum dimension should equal base_size
    max_dim = max(width, height)
    assert max_dim == base, (
        f"Maximum dimension should equal base_size {base}, "
        f"got max({width}, {height}) = {max_dim}"
    )


@settings(max_examples=100)
@given(
    ratio=aspect_ratio,
)
def test_default_base_size_produces_valid_dimensions(ratio: str) -> None:
    """
    **Feature: popgraph, Property 6: 输出尺寸正确性**
    **Validates: Requirements 5.1, 5.2, 5.3**
    
    Property: Using the default base size (1024), all aspect ratios
    should produce valid dimensions that pass validation.
    """
    # Act
    width, height = calculate_image_dimensions(ratio)
    is_valid = validate_image_dimensions(width, height, ratio)
    
    # Assert
    assert is_valid, (
        f"Default dimensions (width={width}, height={height}) for ratio {ratio} "
        f"failed validation"
    )
    assert max(width, height) == DEFAULT_BASE_SIZE, (
        f"Default max dimension should be {DEFAULT_BASE_SIZE}, "
        f"got max({width}, {height})"
    )


# ============================================================================
# Property 3: 批量生成数量一致性
# **Feature: popgraph, Property 3: 批量生成数量一致性**
# **Validates: Requirements 2.2**
#
# For any poster generation request with preview mode enabled (batchSize = 4),
# the response SHALL contain exactly 4 generated images.
# More generally, for any batch_size n, the response should contain exactly n images.
# ============================================================================

# Strategy for batch count - focus on the key value 4 (preview mode) and other valid counts
batch_count = st.integers(min_value=1, max_value=10)

# Strategy for prompt text
prompt_text = st.text(min_size=1, max_size=200).filter(lambda x: x.strip())


def create_mock_image_data(seed: int = 0) -> GeneratedImageData:
    """Create a mock GeneratedImageData for testing."""
    return GeneratedImageData(
        image_buffer=b"mock_image_data_" + str(seed).encode(),
        generation_time_ms=100,
        model_version="z-image-turbo-v1"
    )


@pytest.mark.asyncio
@settings(max_examples=10, deadline=None)
@given(
    count=batch_count,
    prompt=prompt_text,
    base=base_size,
    ratio=aspect_ratio,
)
async def test_batch_generation_returns_exact_count(
    count: int,
    prompt: str,
    base: int,
    ratio: str,
) -> None:
    """
    **Feature: popgraph, Property 3: 批量生成数量一致性**
    **Validates: Requirements 2.2**
    
    Property: For any batch generation request with count n, the response
    SHALL contain exactly n generated images. This specifically validates
    that preview mode (batch_size=4) returns exactly 4 images.
    """
    # Arrange
    width, height = calculate_image_dimensions(ratio, base)
    options = GenerationOptions(
        width=width,
        height=height,
        seed=12345,
        guidance_scale=7.5
    )
    
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Mock the generate_image method to return mock data
    async def mock_generate_image(prompt: str, opts: GenerationOptions) -> GeneratedImageData:
        return create_mock_image_data(opts.seed or 0)
    
    with patch.object(client, 'generate_image', side_effect=mock_generate_image):
        # Act
        results = await client.generate_batch(prompt, count, options)
        
        # Assert: The number of returned images must equal the requested count
        assert len(results) == count, (
            f"Batch generation with count={count} should return exactly {count} images, "
            f"but got {len(results)} images"
        )


@pytest.mark.asyncio
@settings(max_examples=10, deadline=None)
@given(
    prompt=prompt_text,
    base=base_size,
    ratio=aspect_ratio,
)
async def test_preview_mode_returns_exactly_four_images(
    prompt: str,
    base: int,
    ratio: str,
) -> None:
    """
    **Feature: popgraph, Property 3: 批量生成数量一致性**
    **Validates: Requirements 2.2**
    
    Property: For any poster generation request with preview mode enabled
    (batchSize = 4), the response SHALL contain exactly 4 generated images.
    This is the specific case required by Requirements 2.2.
    """
    # Arrange
    PREVIEW_MODE_COUNT = 4  # As specified in Requirements 2.2
    
    width, height = calculate_image_dimensions(ratio, base)
    options = GenerationOptions(
        width=width,
        height=height,
        seed=12345,
        guidance_scale=7.5
    )
    
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Mock the generate_image method
    async def mock_generate_image(prompt: str, opts: GenerationOptions) -> GeneratedImageData:
        return create_mock_image_data(opts.seed or 0)
    
    with patch.object(client, 'generate_image', side_effect=mock_generate_image):
        # Act
        results = await client.generate_batch(prompt, PREVIEW_MODE_COUNT, options)
        
        # Assert: Preview mode must return exactly 4 images
        assert len(results) == PREVIEW_MODE_COUNT, (
            f"Preview mode (batch_size=4) should return exactly 4 images, "
            f"but got {len(results)} images"
        )


@pytest.mark.asyncio
@settings(max_examples=10, deadline=None)
@given(
    prompt=prompt_text,
    base=base_size,
    ratio=aspect_ratio,
)
async def test_batch_generation_returns_unique_variants(
    prompt: str,
    base: int,
    ratio: str,
) -> None:
    """
    **Feature: popgraph, Property 3: 批量生成数量一致性**
    **Validates: Requirements 2.2**
    
    Property: For any batch generation request, each generated image should
    be a unique variant (different seed), ensuring users get diverse options
    in preview mode.
    """
    # Arrange
    PREVIEW_MODE_COUNT = 4
    captured_seeds: list[int] = []
    
    width, height = calculate_image_dimensions(ratio, base)
    options = GenerationOptions(
        width=width,
        height=height,
        seed=12345,
        guidance_scale=7.5
    )
    
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Mock that captures the seeds used for each generation
    async def mock_generate_image(prompt: str, opts: GenerationOptions) -> GeneratedImageData:
        captured_seeds.append(opts.seed)
        return create_mock_image_data(opts.seed or 0)
    
    with patch.object(client, 'generate_image', side_effect=mock_generate_image):
        # Act
        await client.generate_batch(prompt, PREVIEW_MODE_COUNT, options)
        
        # Assert: All seeds should be unique (different variants)
        assert len(captured_seeds) == PREVIEW_MODE_COUNT, (
            f"Should have captured {PREVIEW_MODE_COUNT} seeds, got {len(captured_seeds)}"
        )
        assert len(set(captured_seeds)) == PREVIEW_MODE_COUNT, (
            f"All seeds should be unique for variant generation, "
            f"but got seeds: {captured_seeds}"
        )


@pytest.mark.asyncio
async def test_batch_generation_with_zero_count_returns_empty_list() -> None:
    """
    **Feature: popgraph, Property 3: 批量生成数量一致性**
    **Validates: Requirements 2.2**
    
    Edge case: When count is 0, the batch generation should return an empty list.
    """
    # Arrange
    options = GenerationOptions(
        width=1024,
        height=1024,
        seed=12345,
        guidance_scale=7.5
    )
    
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Act - no mock needed since count=0 should return early
    results = await client.generate_batch("test prompt", 0, options)
    
    # Assert
    assert results == [], (
        f"Batch generation with count=0 should return empty list, got {results}"
    )


# ============================================================================
# Property 8: HTTP 客户端复用
# **Feature: system-optimization, Property 8: HTTP 客户端复用**
# **Validates: Requirements 7.1**
#
# For any ZImageTurboClient instance making multiple requests, the same
# httpx.AsyncClient instance SHALL be reused across all requests.
# ============================================================================


@pytest.mark.asyncio
@settings(max_examples=100, deadline=None)
@given(
    num_calls=st.integers(min_value=2, max_value=10),
)
async def test_http_client_reuse_across_multiple_get_client_calls(num_calls: int) -> None:
    """
    **Feature: system-optimization, Property 8: HTTP 客户端复用**
    **Validates: Requirements 7.1**
    
    Property: For any ZImageTurboClient instance, calling _get_client() multiple
    times should return the same httpx.AsyncClient instance, ensuring connection
    pool reuse.
    """
    # Arrange
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    try:
        # Act: Call _get_client() multiple times
        clients = []
        for _ in range(num_calls):
            http_client = await client._get_client()
            clients.append(http_client)
        
        # Assert: All returned clients should be the same instance
        first_client = clients[0]
        for i, c in enumerate(clients[1:], start=2):
            assert c is first_client, (
                f"Call #{i} returned a different client instance. "
                f"Expected same instance to be reused for connection pooling."
            )
        
        # Verify the client is not closed
        assert not first_client.is_closed, "HTTP client should not be closed while in use"
    finally:
        # Cleanup
        await client.close()


@pytest.mark.asyncio
async def test_http_client_is_none_initially() -> None:
    """
    **Feature: system-optimization, Property 8: HTTP 客户端复用**
    **Validates: Requirements 7.1**
    
    Property: A newly created ZImageTurboClient should have _client as None
    (lazy initialization).
    """
    # Arrange & Act
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Assert: Client should be None before first use
    assert client._client is None, (
        "HTTP client should be None initially (lazy initialization)"
    )


@pytest.mark.asyncio
async def test_http_client_created_on_first_get_client_call() -> None:
    """
    **Feature: system-optimization, Property 8: HTTP 客户端复用**
    **Validates: Requirements 7.1**
    
    Property: The HTTP client should be created on the first call to _get_client()
    and should be a valid httpx.AsyncClient instance.
    """
    # Arrange
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    try:
        # Assert: Client is None before first call
        assert client._client is None
        
        # Act: First call to _get_client()
        http_client = await client._get_client()
        
        # Assert: Client is now created and valid
        assert client._client is not None, "HTTP client should be created after first call"
        assert isinstance(http_client, httpx.AsyncClient), (
            f"Expected httpx.AsyncClient, got {type(http_client)}"
        )
        assert not http_client.is_closed, "HTTP client should not be closed"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_http_client_close_properly_closes_connection() -> None:
    """
    **Feature: system-optimization, Property 8: HTTP 客户端复用**
    **Validates: Requirements 7.4**
    
    Property: Calling close() should properly close the HTTP client connection
    and set _client to None.
    """
    # Arrange
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Create the HTTP client
    http_client = await client._get_client()
    assert http_client is not None
    assert not http_client.is_closed
    
    # Act: Close the client
    await client.close()
    
    # Assert: Client should be closed and _client should be None
    assert client._client is None, "HTTP client reference should be None after close()"
    assert http_client.is_closed, "HTTP client should be closed after close()"


@pytest.mark.asyncio
async def test_http_client_recreated_after_close() -> None:
    """
    **Feature: system-optimization, Property 8: HTTP 客户端复用**
    **Validates: Requirements 7.1, 7.4**
    
    Property: After closing the client, calling _get_client() again should
    create a new HTTP client instance.
    """
    # Arrange
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    try:
        # Get first client
        first_http_client = await client._get_client()
        first_id = id(first_http_client)
        
        # Close the client
        await client.close()
        
        # Get client again
        second_http_client = await client._get_client()
        second_id = id(second_http_client)
        
        # Assert: Should be a new instance
        assert first_id != second_id, (
            "After close(), _get_client() should create a new HTTP client instance"
        )
        assert not second_http_client.is_closed, "New HTTP client should not be closed"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_close_is_idempotent() -> None:
    """
    **Feature: system-optimization, Property 8: HTTP 客户端复用**
    **Validates: Requirements 7.4**
    
    Property: Calling close() multiple times should be safe (idempotent).
    """
    # Arrange
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Create the HTTP client
    await client._get_client()
    
    # Act: Close multiple times - should not raise
    await client.close()
    await client.close()
    await client.close()
    
    # Assert: Client should still be None
    assert client._client is None


@pytest.mark.asyncio
async def test_close_without_initialization_is_safe() -> None:
    """
    **Feature: system-optimization, Property 8: HTTP 客户端复用**
    **Validates: Requirements 7.4**
    
    Property: Calling close() on a client that was never initialized should be safe.
    """
    # Arrange
    client = ZImageTurboClient(api_key="mock-key", base_url="http://mock-api", timeout_ms=5000)
    
    # Assert: Client is None
    assert client._client is None
    
    # Act: Close without ever initializing - should not raise
    await client.close()
    
    # Assert: Client is still None
    assert client._client is None

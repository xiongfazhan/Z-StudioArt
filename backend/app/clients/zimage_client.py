"""Z-Image-Turbo AI 模型客户端 (ModelScope API)

实现与 ModelScope Z-Image-Turbo 模型的交互，支持图像生成和批量生成。

Requirements:
- 2.1: 单张海报生成在 5 秒内返回
- 2.2: 预览模式生成 4 张变体图
- 5.1, 5.2, 5.3: 支持 1:1, 9:16, 16:9 尺寸比例
- 7.1: HTTP 客户端复用连接池
- 7.2: 网络请求失败时自动重试（指数退避）
- 7.3: 请求超时时抛出 ZImageTimeoutError
- 7.4: 应用关闭时正确关闭 HTTP 客户端连接
"""

import asyncio
import time
from typing import Literal, Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.core.config import settings
from app.models.schemas import GeneratedImageData, GenerationOptions


DEFAULT_BASE_SIZE = 1024


# ============================================================================
# Custom Exceptions
# ============================================================================

class ZImageTimeoutError(Exception):
    """Z-Image 请求超时异常
    
    Requirements:
        - 7.3: WHEN 请求超时时 THEN PopGraph SHALL 抛出 ZImageTimeoutError 自定义异常
    """
    def __init__(self, message: str = "Z-Image request timed out", timeout_ms: Optional[int] = None):
        self.timeout_ms = timeout_ms
        super().__init__(message)


class ZImageAPIError(Exception):
    """Z-Image API 错误异常"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class AspectRatioCalculator:
    """图像尺寸计算器"""
    
    ASPECT_RATIOS: dict[str, tuple[int, int]] = {
        "1:1": (1, 1),
        "9:16": (9, 16),
        "16:9": (16, 9),
    }
    
    @classmethod
    def calculate_dimensions(
        cls,
        aspect_ratio: str,
        base_size: int = DEFAULT_BASE_SIZE,
        custom_width: Optional[int] = None,
        custom_height: Optional[int] = None,
    ) -> tuple[int, int]:
        if aspect_ratio == "custom":
            if not custom_width or not custom_height:
                raise ValueError("custom_width and custom_height must be provided when aspect_ratio is 'custom'")
            return (custom_width, custom_height)

        if aspect_ratio not in cls.ASPECT_RATIOS:
            raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")
        
        ratio_w, ratio_h = cls.ASPECT_RATIOS[aspect_ratio]
        
        if ratio_w >= ratio_h:
            width = base_size
            height = int(base_size * ratio_h / ratio_w)
        else:
            height = base_size
            width = int(base_size * ratio_w / ratio_h)
        
        return (width, height)
    
    @classmethod
    def validate_dimensions(
        cls,
        width: int,
        height: int,
        aspect_ratio: Literal["1:1", "9:16", "16:9"],
        tolerance: int = 1
    ) -> bool:
        ratio_w, ratio_h = cls.ASPECT_RATIOS[aspect_ratio]
        expected_ratio = ratio_w / ratio_h
        min_ratio = max(width - tolerance, 1) / (height + tolerance)
        max_ratio = (width + tolerance) / max(height - tolerance, 1)
        return min_ratio <= expected_ratio <= max_ratio


class ZImageTurboClient:
    """Z-Image-Turbo AI 模型客户端 (ModelScope API)
    
    使用 ModelScope 异步 API 进行图像生成。
    支持 HTTP 客户端连接池复用和自动重试机制。
    
    Requirements:
        - 7.1: WHEN ZImageTurboClient 发起多次请求时 THEN PopGraph SHALL 复用同一个 httpx.AsyncClient 实例
        - 7.2: WHEN 网络请求失败时 THEN PopGraph SHALL 自动重试最多 3 次（使用指数退避）
        - 7.3: WHEN 请求超时时 THEN PopGraph SHALL 抛出 ZImageTimeoutError 自定义异常
        - 7.4: WHEN 应用关闭时 THEN PopGraph SHALL 正确关闭 HTTP 客户端连接
    """
    
    MAX_RETRIES = 3
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        poll_interval: float = 1.0
    ):
        self.api_key = api_key or settings.modelscope_api_key
        self.base_url = (base_url or settings.modelscope_base_url).rstrip("/")
        self.timeout_ms = timeout_ms or settings.zimage_timeout
        self.poll_interval = poll_interval
        self._model_version = "Tongyi-MAI/Z-Image-Turbo"
        # HTTP 客户端实例（延迟初始化，复用连接池）
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_timeout(self) -> httpx.Timeout:
        """获取 HTTP 超时配置"""
        return httpx.Timeout(self.timeout_ms / 1000 + 10, connect=10.0)
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端（延迟初始化，复用连接）
        
        Requirements:
            - 7.1: WHEN ZImageTurboClient 发起多次请求时 THEN PopGraph SHALL 复用同一个 httpx.AsyncClient 实例
        
        Returns:
            httpx.AsyncClient: 复用的 HTTP 客户端实例
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self._get_timeout(),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
        return self._client
    
    async def close(self) -> None:
        """关闭 HTTP 客户端连接
        
        Requirements:
            - 7.4: WHEN 应用关闭时 THEN PopGraph SHALL 正确关闭 HTTP 客户端连接
        """
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    def _get_headers(self, async_mode: bool = False) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if async_mode:
            headers["X-ModelScope-Async-Mode"] = "true"
        return headers
    
    def _get_task_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-ModelScope-Task-Type": "image_generation",
        }
    
    async def _submit_task_with_retry(
        self,
        prompt: str,
        options: GenerationOptions,
    ) -> str:
        """提交生成任务（带重试机制），返回 task_id
        
        Requirements:
            - 7.2: WHEN 网络请求失败时 THEN PopGraph SHALL 自动重试最多 3 次（使用指数退避）
        """
        client = await self._get_client()
        
        @retry(
            stop=stop_after_attempt(self.MAX_RETRIES),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout)),
            reraise=True,
        )
        async def _do_submit() -> str:
            payload = {
                "model": self._model_version,
                "prompt": prompt,
            }
            
            # 添加可选参数
            if options.seed is not None:
                payload["seed"] = options.seed
            if options.width and options.height:
                payload["size"] = f"{options.width}x{options.height}"
            
            try:
                response = await client.post(
                    f"{self.base_url}/v1/images/generations",
                    headers=self._get_headers(async_mode=True),
                    json=payload
                )
                response.raise_for_status()
                return response.json()["task_id"]
            except httpx.TimeoutException as e:
                raise ZImageTimeoutError(
                    f"Request timed out while submitting task: {e}",
                    timeout_ms=self.timeout_ms
                ) from e
        
        return await _do_submit()
    
    async def _poll_task_with_retry(
        self,
        task_id: str,
        start_time: float
    ) -> bytes:
        """轮询任务状态（带重试机制），返回图像数据
        
        Requirements:
            - 7.2: WHEN 网络请求失败时 THEN PopGraph SHALL 自动重试最多 3 次（使用指数退避）
            - 7.3: WHEN 请求超时时 THEN PopGraph SHALL 抛出 ZImageTimeoutError 自定义异常
        """
        client = await self._get_client()
        timeout_seconds = self.timeout_ms / 1000
        
        @retry(
            stop=stop_after_attempt(self.MAX_RETRIES),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout)),
            reraise=True,
        )
        async def _do_poll() -> dict:
            response = await client.get(
                f"{self.base_url}/v1/tasks/{task_id}",
                headers=self._get_task_headers()
            )
            response.raise_for_status()
            return response.json()
        
        @retry(
            stop=stop_after_attempt(self.MAX_RETRIES),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout)),
            reraise=True,
        )
        async def _download_image(url: str) -> bytes:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
        
        while True:
            elapsed = time.perf_counter() - start_time
            if elapsed > timeout_seconds:
                raise ZImageTimeoutError(
                    f"Image generation timed out after {self.timeout_ms}ms",
                    timeout_ms=self.timeout_ms
                )
            
            try:
                data = await _do_poll()
            except httpx.TimeoutException as e:
                raise ZImageTimeoutError(
                    f"Request timed out while polling task: {e}",
                    timeout_ms=self.timeout_ms
                ) from e
            
            if data["task_status"] == "SUCCEED":
                image_url = data["output_images"][0]
                try:
                    return await _download_image(image_url)
                except httpx.TimeoutException as e:
                    raise ZImageTimeoutError(
                        f"Request timed out while downloading image: {e}",
                        timeout_ms=self.timeout_ms
                    ) from e
            elif data["task_status"] == "FAILED":
                raise ZImageAPIError(
                    f"Image generation failed: {data.get('message', 'Unknown error')}"
                )
            
            await asyncio.sleep(self.poll_interval)
    
    async def generate_image(
        self,
        prompt: str,
        options: GenerationOptions
    ) -> GeneratedImageData:
        """生成单张图像（使用连接池复用和重试机制）
        
        Requirements:
            - 7.1: 复用 HTTP 客户端连接
            - 7.2: 网络请求失败时自动重试
            - 7.3: 超时时抛出 ZImageTimeoutError
        """
        start_time = time.perf_counter()
        
        task_id = await self._submit_task_with_retry(prompt, options)
        image_buffer = await self._poll_task_with_retry(task_id, start_time)
        
        generation_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        return GeneratedImageData(
            image_buffer=image_buffer,
            generation_time_ms=generation_time_ms,
            model_version=self._model_version
        )
    
    async def generate_batch(
        self,
        prompt: str,
        count: int,
        options: GenerationOptions
    ) -> list[GeneratedImageData]:
        """批量生成图像（串行执行，带延迟避免 API 限流）"""
        if count <= 0:
            return []
        
        base_seed = options.seed or int(time.time() * 1000) % (2**32)
        results = []
        
        for i in range(count):
            variant_options = GenerationOptions(
                width=options.width,
                height=options.height,
                seed=base_seed + i,
                guidance_scale=options.guidance_scale
            )
            result = await self.generate_image(prompt, variant_options)
            results.append(result)
            
            # 添加延迟避免 API 限流
            if i < count - 1:
                await asyncio.sleep(2.0)
        
        return results
    
    async def image_to_image(
        self,
        source_image: bytes,
        prompt: str,
        options: GenerationOptions
    ) -> GeneratedImageData:
        """图生图（场景融合）- 暂不支持，返回文生图结果"""
        # ModelScope Z-Image-Turbo 目前主要支持文生图
        # 场景融合功能可以通过 prompt 描述实现
        return await self.generate_image(prompt, options)



def calculate_image_dimensions(
    aspect_ratio: str,
    base_size: int = DEFAULT_BASE_SIZE,
    custom_width: Optional[int] = None,
    custom_height: Optional[int] = None,
) -> tuple[int, int]:
    """便捷函数：计算图像尺寸"""
    return AspectRatioCalculator.calculate_dimensions(
        aspect_ratio, base_size, custom_width, custom_height
    )


def validate_image_dimensions(
    width: int,
    height: int,
    aspect_ratio: Literal["1:1", "9:16", "16:9"],
    tolerance: int = 1
) -> bool:
    """便捷函数：验证图像尺寸"""
    return AspectRatioCalculator.validate_dimensions(
        width, height, aspect_ratio, tolerance
    )


# ============================================================================
# Global Instance (using ServiceProvider for thread-safe singleton)
# ============================================================================

from app.utils.service_provider import ServiceProvider

_zimage_client_provider: ServiceProvider[ZImageTurboClient] = ServiceProvider(ZImageTurboClient)


def get_zimage_client() -> ZImageTurboClient:
    """Get the default ZImageTurboClient instance (thread-safe singleton).
    
    Uses ServiceProvider with double-checked locking pattern to ensure
    thread safety when multiple threads call this function concurrently.
    
    Returns:
        ZImageTurboClient instance
        
    Requirements:
        - 5.4: WHEN 多线程同时调用 get_zimage_client() 时 THEN PopGraph SHALL 返回同一个 ZImageTurboClient 实例
    """
    return _zimage_client_provider.get_instance()


def reset_zimage_client() -> None:
    """Reset the ZImageTurboClient instance (for testing).
    
    Requirements:
        - 5.5: WHEN 测试需要重置单例时 THEN PopGraph SHALL 提供 reset() 方法清除实例
    """
    _zimage_client_provider.reset()

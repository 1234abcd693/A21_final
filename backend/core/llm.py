"""
llama-server HTTP 客户端封装

流式和非流式生成。
"""

import json
from typing import AsyncGenerator, Optional

import httpx

from core.config import settings

LLAMA_URL = f"{settings.LLAMA_SERVER_URL}/completion"


async def _check_health() -> bool:
    """检查 llama-server 是否可用"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.LLAMA_SERVER_URL}/health")
            return resp.status_code == 200
    except Exception:
        return False


async def generate_stream(
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> AsyncGenerator[str, None]:
    """
    流式生成（SSE）。
    每产出一个 token 就 yield。
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            LLAMA_URL,
            json={
                "prompt": prompt,
                "temperature": temperature,
                "n_predict": max_tokens,
                "stream": True,
                "cache_prompt": True,
            },
        ) as response:
            if response.status_code != 200:
                raise RuntimeError(f"llama-server error: {response.status_code}")
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    content = data.get("content", "")
                    if content:
                        yield content
                    if data.get("stop", False):
                        break


async def generate(
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> str:
    """非流式生成（返回完整结果）"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            LLAMA_URL,
            json={
                "prompt": prompt,
                "temperature": temperature,
                "n_predict": max_tokens,
                "stream": False,
            },
        )
        if response.status_code != 200:
            raise RuntimeError(f"llama-server error: {response.status_code}")
        return response.json().get("content", "")

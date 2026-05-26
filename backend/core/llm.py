"""
llama-server HTTP 客户端封装（OpenAI-compatible API）

流式和非流式生成。

llama.cpp v9310+ 使用 OpenAI-compatible API：
  - 端点: /v1/completions（兼容旧 /completion）
  - 请求参数: max_tokens（替代 n_predict）
  - 响应格式: {"choices": [{"text": "...", "finish_reason": "..."}]}
  - SSE 流: data: {"choices": [{"text": "...", "finish_reason": null}]}\n\n
              data: [DONE]\n\n
"""

import json
import logging
from typing import AsyncGenerator, Optional

import httpx

from core.config import settings

LLAMA_URL = f"{settings.LLAMA_SERVER_URL}/v1/completions"
logger = logging.getLogger(__name__)


async def _check_health() -> bool:
    """检查 llama-server 是否可用"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.LLAMA_SERVER_URL}/health")
            return resp.status_code == 200
    except Exception:
        logger.exception("llama-server health check failed")
        return False


async def generate_stream(
    prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 512,
) -> AsyncGenerator[str, None]:
    """
    流式生成（SSE, OpenAI-compatible）。
    每产出一个 token 就 yield。
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            LLAMA_URL,
            json={
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                "cache_prompt": True,
                "stop": ["<|im_end|>", "<|im_start|>", "\n\n\n"],  # 防止模型自循环
            },
        ) as response:
            if response.status_code != 200:
                raise RuntimeError(f"llama-server error: {response.status_code}")
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                    choices = data.get("choices", [])
                    if choices:
                        text = choices[0].get("text", "")
                        if text:
                            yield text
                        if choices[0].get("finish_reason") is not None:
                            break
                except json.JSONDecodeError:
                    continue


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
                "max_tokens": max_tokens,
                "stream": False,
            },
        )
        if response.status_code != 200:
            raise RuntimeError(f"llama-server error: {response.status_code}")
        data = response.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("text", "")
        return ""

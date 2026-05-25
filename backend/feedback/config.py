"""
RAG 参数配置管理（读写 params.json）
"""

import json
from pathlib import Path
from typing import Any

from core.config import settings


def load() -> dict[str, Any]:
    """加载参数配置"""
    params_path = Path(settings.PARAMS_PATH)
    if params_path.exists():
        return json.loads(params_path.read_text(encoding="utf-8"))
    return _default_params()


def save(params: dict[str, Any]) -> None:
    """保存参数配置"""
    params_path = Path(settings.PARAMS_PATH)
    params_path.parent.mkdir(parents=True, exist_ok=True)
    params_path.write_text(json.dumps(params, indent=2, ensure_ascii=False), encoding="utf-8")


def reset_to_defaults() -> dict[str, Any]:
    """恢复默认参数"""
    defaults = _default_params()
    current = load()
    current["retrieval"] = defaults["retrieval"]
    current["version"] = current.get("version", 0) + 1
    current["updated_by"] = "manual_reset"
    current["updated_at"] = _now()
    save(current)
    return current


def apply_optimized(params: dict[str, Any]) -> dict[str, Any]:
    """应用优化后的参数"""
    current = load()
    current["retrieval"] = {
        "alpha": params.get("alpha", current["retrieval"]["alpha"]),
        "beta": params.get("beta", current["retrieval"]["beta"]),
        "gamma": params.get("gamma", current["retrieval"]["gamma"]),
        "top_k_per_source": params.get("top_k_per_source", current["retrieval"]["top_k_per_source"]),
        "rerank_keep": params.get("rerank_keep", current["retrieval"]["rerank_keep"]),
    }
    current["version"] = current.get("version", 0) + 1
    current["updated_by"] = "grid_search"
    current["updated_at"] = _now()
    save(current)
    return current


def _now() -> str:
    from datetime import datetime
    return datetime.now().isoformat()


def _default_params() -> dict[str, Any]:
    return {
        "version": 1,
        "updated_at": _now(),
        "updated_by": "default",
        "retrieval": {
            "alpha": 0.35,
            "beta": 0.35,
            "gamma": 0.30,
            "top_k_per_source": 5,
            "rerank_keep": 5,
        },
        "generation": {"temperature": 0.1, "max_tokens": 512},
        "defaults": {
            "alpha": 0.35,
            "beta": 0.35,
            "gamma": 0.30,
            "top_k_per_source": 5,
            "rerank_keep": 5,
        },
    }

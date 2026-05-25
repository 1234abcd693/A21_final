"""
优化器抽象基类

所有优化算法必须实现 optimize() 方法。
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseOptimizer(ABC):
    """优化器抽象基类"""

    @abstractmethod
    def optimize(self, feedbacks: list[dict[str, Any]]) -> dict[str, Any]:
        """
        根据反馈数据返回最优参数。

        参数:
            feedbacks: [{"question": ..., "retrieved_chunks": [...], "rating": 1}, ...]
        返回:
            {"alpha": 0.3, "beta": 0.5, "gamma": 0.2, "top_k_per_source": 5, "rerank_keep": 5, "score": 0.82}
        """
        pass

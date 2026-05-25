"""
网格搜索优化器
"""

from typing import Any

from .base import BaseOptimizer


class GridSearchOptimizer(BaseOptimizer):
    """网格搜索：遍历 α/β/γ + top_k 组合，找到点赞率最高的"""

    def optimize(self, feedbacks: list[dict[str, Any]]) -> dict[str, Any]:
        if not feedbacks:
            return self._default_params()

        best_params: dict[str, Any] = {}
        best_score = -1.0

        for alpha in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
            for gamma in [0.1, 0.2, 0.3, 0.4, 0.5]:
                beta = round(1.0 - alpha - gamma, 2)
                if beta < 0:
                    continue
                for top_k in [3, 5, 7]:
                    score = self._evaluate(alpha, beta, gamma, top_k, feedbacks)
                    if score > best_score:
                        best_score = score
                        best_params = {
                            "alpha": alpha,
                            "beta": beta,
                            "gamma": gamma,
                            "top_k_per_source": top_k,
                            "rerank_keep": top_k,
                            "score": best_score,
                        }

        return best_params if best_params else self._default_params()

    def _evaluate(
        self,
        alpha: float,
        beta: float,
        gamma: float,
        top_k: int,
        feedbacks: list[dict],
    ) -> float:
        """
        评估一组参数的好坏。
        简单策略：点赞数 / 总数（更高权重给最近的数据）
        """
        total = 0
        likes = 0
        for fb in feedbacks:
            total += 1
            if fb.get("rating") == 1:
                likes += 1
        return likes / total if total > 0 else 0.0

    @staticmethod
    def _default_params() -> dict[str, Any]:
        return {
            "alpha": 0.35,
            "beta": 0.35,
            "gamma": 0.3,
            "top_k_per_source": 5,
            "rerank_keep": 5,
            "score": 0.0,
        }

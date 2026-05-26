"""
Tests for ``rag/retriever.py`` — BM25 search, RRF fusion, params loading.

All external dependencies (ChromaDB, Neo4j, jieba) are mocked so tests
run without any infrastructure.
"""

import json

import pytest
from unittest.mock import MagicMock, patch

from rag.retriever import bm25_search, rrf_fuse, load_params, hybrid_search


# ======================================================================
# BM25 Search
# ======================================================================


class TestBM25Search:
    """``bm25_search()`` — keyword exact-matching retrieval."""

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _chunk_list(*ids_and_scores):
        """Build ``(_bm25_chunks, mock_index)`` from (chunk_id, text, score) tuples."""
        chunks = []
        scores = []
        for cid, text, score in ids_and_scores:
            chunks.append({"chunk_id": cid, "text": text, "doc_name": "d", "page": "1"})
            scores.append(score)
        mock_index = MagicMock()
        mock_index.get_scores.return_value = scores
        return chunks, mock_index

    # -- tests -------------------------------------------------------------

    @patch("rag.retriever._ensure_bm25_index")
    def test_bm25_search_empty_index(self, mock_ensure):
        """BM25 index is None (empty/disabled) → returns []."""
        with (
            patch("rag.retriever._bm25_index", None),
            patch("rag.retriever._bm25_chunks", []),
        ):
            assert bm25_search("接触器线圈烧毁") == []

    @patch("rag.retriever._ensure_bm25_index")
    def test_bm25_search_with_results(self, mock_ensure):
        """Results are sorted descending by BM25 score; zero-score items filtered."""
        chunks, mock_index = self._chunk_list(
            ("c1", "线圈烧毁原因", 0.5),
            ("c2", "无关内容", 0.0),
            ("c3", "接触器维修方法", 0.8),
        )
        with (
            patch("rag.retriever._bm25_index", mock_index),
            patch("rag.retriever._bm25_chunks", chunks),
            patch("jieba.cut", return_value=["接触器", "线圈"]),
        ):
            result = bm25_search("接触器线圈烧毁", top_k=2)

        assert len(result) == 2
        assert result[0]["chunk_id"] == "c3"  # highest score
        assert result[0]["score"] == 0.8
        assert result[1]["chunk_id"] == "c1"
        assert result[1]["score"] == 0.5

    @patch("rag.retriever._ensure_bm25_index")
    def test_bm25_search_all_zero_scores(self, mock_ensure):
        """All scores are 0 → empty list (no matching content)."""
        chunks, mock_index = self._chunk_list(("c1", "无关内容", 0.0))
        with (
            patch("rag.retriever._bm25_index", mock_index),
            patch("rag.retriever._bm25_chunks", chunks),
            patch("jieba.cut", return_value=["无关"]),
        ):
            assert bm25_search("无关查询", top_k=5) == []

    @patch("rag.retriever._ensure_bm25_index")
    def test_bm25_search_exception_handling(self, mock_ensure):
        """BM25 scoring raises → degrade gracefully with []."""
        chunks, mock_index = self._chunk_list(("c1", "text", 0.5))
        mock_index.get_scores.side_effect = Exception("BM25 crash")
        with (
            patch("rag.retriever._bm25_index", mock_index),
            patch("rag.retriever._bm25_chunks", chunks),
            patch("jieba.cut", return_value=["test"]),
        ):
            assert bm25_search("test") == []


# ======================================================================
# RRF Fusion
# ======================================================================


class TestRRFFusion:
    """``rrf_fuse()`` — reciprocal rank fusion of multi-source results."""

    def test_rrf_fuse_deduplicates(self):
        """Same chunk_id from multiple sources appears only once."""
        bm25 = [{"chunk_id": "a", "text": "doc a"}]
        vector = [{"chunk_id": "a", "text": "doc a"}]
        result = rrf_fuse(bm25, vector, [], top_k=5)
        ids = [r["chunk_id"] for r in result]
        assert ids.count("a") == 1

    def test_rrf_fuse_ranking(self):
        """Chunk appearing in multiple sources ranks higher than single-source."""
        bm25 = [{"chunk_id": "a"}, {"chunk_id": "b"}]
        vector = [{"chunk_id": "a"}]  # 'a' in 2 sources
        result = rrf_fuse(bm25, vector, [], top_k=5)
        a = next(r for r in result if r["chunk_id"] == "a")
        b = next(r for r in result if r["chunk_id"] == "b")
        assert a["fusion_score"] > b["fusion_score"]

    def test_rrf_fuse_empty_lists(self):
        """All three result lists empty → []."""
        assert rrf_fuse([], [], [], top_k=5) == []

    def test_rrf_fuse_single_source(self):
        """Only BM25 has results → ranking preserved, source='bm25'."""
        bm25 = [{"chunk_id": "a", "text": "first"}, {"chunk_id": "b", "text": "second"}]
        result = rrf_fuse(bm25, [], [], top_k=2)
        assert len(result) == 2
        assert result[0]["chunk_id"] == "a"
        assert result[0]["source"] == "bm25"
        assert result[1]["chunk_id"] == "b"

    def test_rrf_fuse_top_k_limit(self):
        """top_k parameter caps the number of fused results."""
        bm25 = [{"chunk_id": str(i)} for i in range(10)]
        assert len(rrf_fuse(bm25, [], [], top_k=3)) == 3

    def test_rrf_fuse_graph_results_source(self):
        """Graph results (no chunk_id) are included with source='graph'."""
        result = rrf_fuse([], [], [{"symptom": "故障A", "causes": []}], top_k=5)
        assert len(result) == 1
        assert result[0]["source"] == "graph"

    def test_rrf_fuse_multiple_sources_same_rank(self):
        """Chunk at rank 0 in BM25 and rank 0 in vector gets RRF boost."""
        bm25 = [{"chunk_id": "a"}]
        vector = [{"chunk_id": "a"}]
        result = rrf_fuse(bm25, vector, [], top_k=5)
        # RRF score for rank 0 (rank index 0): 1/(60+1) = ~0.01639
        # Two hits: 2 * 1/61 ≈ 0.03279
        assert abs(result[0]["fusion_score"] - 2.0 / 61.0) < 1e-5


# ======================================================================
# Params Loading
# ======================================================================


class TestLoadParams:
    """``load_params()`` — RAG configuration loading."""

    def test_load_params_defaults(self):
        """params.json does not exist → return hardcoded defaults."""
        with patch("rag.retriever.settings.PARAMS_PATH", "/nonexistent/path.json"):
            params = load_params()

        assert params["retrieval"]["alpha"] == 0.35
        assert params["retrieval"]["beta"] == 0.35
        assert params["retrieval"]["gamma"] == 0.3
        assert params["retrieval"]["top_k_per_source"] == 5
        assert params["retrieval"]["rerank_keep"] == 5
        assert params["generation"]["temperature"] == 0.1
        assert params["generation"]["max_tokens"] == 512

    def test_load_params_from_file(self, tmp_path):
        """params.json exists → return its contents verbatim."""
        params_file = tmp_path / "params.json"
        custom = {
            "retrieval": {
                "alpha": 0.5, "beta": 0.3, "gamma": 0.2,
                "top_k_per_source": 10, "rerank_keep": 3,
            },
            "generation": {"temperature": 0.2, "max_tokens": 256},
        }
        params_file.write_text(json.dumps(custom), encoding="utf-8")

        with patch("rag.retriever.settings.PARAMS_PATH", str(params_file)):
            params = load_params()

        assert params["retrieval"]["alpha"] == 0.5
        assert params["retrieval"]["rerank_keep"] == 3
        assert params["generation"]["temperature"] == 0.2

    def test_load_params_malformed_json(self, tmp_path):
        """Corrupt params.json → exception propagates (caller handles it)."""
        bad_file = tmp_path / "params.json"
        bad_file.write_text("{bad json", encoding="utf-8")
        with patch("rag.retriever.settings.PARAMS_PATH", str(bad_file)):
            with pytest.raises(json.JSONDecodeError):
                load_params()


# ======================================================================
# Hybrid Search (unified entry point)
# ======================================================================


class TestHybridSearch:
    """``hybrid_search()`` — orchestrates BM25 + vector + graph → RRF fusion."""

    @patch("rag.retriever.cypher_search", return_value=[])
    @patch("rag.retriever.bm25_search", return_value=[])
    @patch("rag.retriever.chroma_search", return_value=[])
    @patch("rag.retriever.load_params")
    def test_hybrid_search_structure(
        self, mock_params, mock_chroma, mock_bm25, mock_graph,
    ):
        """Return dict contains 'chunks', 'graph_results', 'all_results'."""
        mock_params.return_value = {
            "retrieval": {"top_k_per_source": 3, "rerank_keep": 3},
        }
        result = hybrid_search("测试查询")
        assert all(k in result for k in ("chunks", "graph_results", "all_results"))
        assert isinstance(result["chunks"], list)
        assert isinstance(result["graph_results"], list)
        assert isinstance(result["all_results"], list)

    @patch("rag.retriever.cypher_search", return_value=[{"symptom": "故障A"}])
    @patch("rag.retriever.bm25_search", return_value=[{"chunk_id": "c1", "text": "t1"}])
    @patch("rag.retriever.chroma_search", return_value=[{"chunk_id": "c2", "text": "t2"}])
    @patch("rag.retriever.load_params")
    def test_hybrid_search_includes_all_sources(
        self, mock_params, mock_chroma, mock_bm25, mock_graph,
    ):
        """Results from all three retrieval paths appear in output."""
        mock_params.return_value = {
            "retrieval": {"top_k_per_source": 5, "rerank_keep": 5},
        }
        result = hybrid_search("测试")
        assert len(result["graph_results"]) == 1
        # chunks should contain non-graph items
        assert any(c.get("source") != "graph" for c in result["chunks"])

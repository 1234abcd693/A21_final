"""
Shared fixtures for A21 backend tests.

Provides test data (sample_chunks, sample_graph_results, mock_search_results)
and infrastructure mocks (mock_neo4j_session) used across all test modules.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure backend directory is on sys.path so imports like `rag.retriever` work
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_chunks():
    """Sample document chunks for retriever / prompt / validator tests.

    Each entry matches the dict shape produced by BM25/vector retrieval:
    chunk_id, text, doc_name, page.
    """
    return [
        {
            "chunk_id": "chunk_001",
            "text": "接触器线圈烧毁是由于电源电压过低导致的",
            "doc_name": "电气维修手册",
            "page": "P42",
        },
        {
            "chunk_id": "chunk_002",
            "text": "万用表测线圈电压确认是否大于等于85%UN",
            "doc_name": "电气维修手册",
            "page": "P43",
        },
        {
            "chunk_id": "chunk_003",
            "text": "断电挂牌后方可进行线圈更换操作",
            "doc_name": "安全操作规程",
            "page": "P12",
        },
    ]


@pytest.fixture
def sample_graph_results():
    """Sample graph retrieval results for prompt / validation tests.

    Each entry has the structure returned by kg.neo4j_client.graph_search():
    symptom, causes (sorted by priority), steps, tools, precautions, source_doc, source_page.
    """
    return [
        {
            "symptom": "接触器线圈烧毁",
            "causes": [
                {
                    "cause": "电源电压过低",
                    "priority": 1,
                    "check_method": "万用表测量",
                    "check_time": "1分钟",
                    "requires_shutdown": False,
                },
                {
                    "cause": "线圈内部短路",
                    "priority": 2,
                    "check_method": "绝缘电阻测试",
                    "check_time": "3分钟",
                    "requires_shutdown": True,
                },
            ],
            "steps": [
                "万用表测线圈电压确认≥85%UN",
                "检查线圈绝缘电阻",
            ],
            "tools": ["万用表", "绝缘电阻测试仪"],
            "precautions": ["断电挂牌"],
            "source_doc": "船舶电气设备维护与修理",
            "source_page": "第四章第二节",
        },
    ]


@pytest.fixture
def mock_search_results():
    """Mock return value for rag.retriever.hybrid_search()."""
    return {
        "chunks": [
            {
                "chunk_id": "chunk_001",
                "text": "接触器线圈烧毁是由于电源电压过低",
                "doc_name": "电气维修手册",
                "page": "P42",
                "source": "bm25",
            },
            {
                "chunk_id": "chunk_002",
                "text": "万用表测线圈电压确认≥85%UN",
                "doc_name": "电气维修手册",
                "page": "P43",
                "source": "vector",
            },
        ],
        "graph_results": [
            {
                "symptom": "接触器线圈烧毁",
                "causes": [{"cause": "电源电压过低", "priority": 1}],
                "steps": ["测电压"],
                "tools": ["万用表"],
                "precautions": ["断电"],
                "source_doc": "电气维修手册",
                "source_page": "P42",
            }
        ],
        "all_results": [],
    }


# ---------------------------------------------------------------------------
# Infrastructure mocks
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_neo4j_session():
    """Mock Neo4j driver and session to avoid needing a real Neo4j instance.

    Patches ``kg.neo4j_client._get_driver`` so that every function in
    neo4j_client.py that calls ``_get_driver().session()`` receives a
    controlled :class:`unittest.mock.MagicMock` session.

    The yielded *mock_session* can be configured per-test by setting
    ``mock_session.run.return_value`` or ``mock_session.run.side_effect``.
    """
    mock_session = MagicMock()
    mock_driver = MagicMock()
    # Support ``with _get_driver().session() as session:`` context manager
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_driver.session.return_value.__exit__.return_value = None

    with patch("kg.neo4j_client._get_driver", return_value=mock_driver):
        yield mock_session

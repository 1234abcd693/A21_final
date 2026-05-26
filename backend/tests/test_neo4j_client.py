"""
Tests for ``kg/neo4j_client.py`` — Neo4j query functions via mocked sessions.

No real Neo4j instance is required; ``conftest.mock_neo4j_session`` patches
``_get_driver`` so all calls to ``session.run()`` return configurable mocks.
"""

import pytest
from unittest.mock import MagicMock

# Attempt to import ServiceUnavailable for realistic error simulation.
# If the neo4j package is not installed the fallback is Exception, which
# means the connection-failure test becomes broader but still passes.
try:
    from neo4j.exceptions import ServiceUnavailable
except ImportError:  # pragma: no cover
    ServiceUnavailable = Exception

from kg.neo4j_client import (
    check_connection,
    get_symptoms,
    search_entities,
    get_node,
    expand_node,
    graph_search,
)


# ======================================================================
# check_connection
# ======================================================================


class TestCheckConnection:
    """Health check: ``check_connection()``."""

    def test_success(self, mock_neo4j_session):
        """Neo4j responds → True."""
        assert check_connection() is True

    def test_failure(self, mock_neo4j_session):
        """Neo4j raises ServiceUnavailable → False."""
        mock_neo4j_session.run.side_effect = ServiceUnavailable("down")
        assert check_connection() is False


# ======================================================================
# get_symptoms
# ======================================================================


class TestGetSymptoms:
    """``get_symptoms()`` — symptom list with optional keyword filter."""

    def test_with_keyword(self, mock_neo4j_session):
        """Keyword provided → Cypher query uses CONTAINS."""
        mock_neo4j_session.run.return_value = [
            {"uid": "S_CONT_01", "name": "接触器线圈烧毁"},
            {"uid": "S_CONT_02", "name": "接触器触头粘连"},
        ]
        results = get_symptoms(keyword="接触器")
        assert len(results) == 2
        assert results[0]["name"] == "接触器线圈烧毁"
        # CONTAINS param was passed
        assert "kw" in mock_neo4j_session.run.call_args[1]

    def test_without_keyword(self, mock_neo4j_session):
        """Empty keyword → Cypher query omits WHERE CONTAINS."""
        mock_neo4j_session.run.return_value = [{"uid": "S_01", "name": "故障A"}]
        results = get_symptoms(keyword="", limit=5)
        assert len(results) == 1
        query = mock_neo4j_session.run.call_args[0][0]
        assert "CONTAINS" not in query

    def test_limit(self, mock_neo4j_session):
        """limit parameter is forwarded to Cypher."""
        mock_neo4j_session.run.return_value = [{"uid": "S_01", "name": "故障"}]
        get_symptoms(limit=1)
        assert mock_neo4j_session.run.call_args[1]["limit"] == 1


# ======================================================================
# search_entities
# ======================================================================


class TestSearchEntities:
    """``search_entities()`` — cross-label entity keyword search."""

    def test_single_keyword(self, mock_neo4j_session):
        """Single keyword returns matching entities."""
        mock_neo4j_session.run.return_value = [
            {"uid": "E_01", "name": "接触器", "label": "Equipment",
             "source_doc": "手册", "source_page": "P1"},
        ]
        results = search_entities("接触器")
        assert len(results) == 1
        assert results[0]["label"] == "Equipment"

    def test_multiple_keywords_dedup(self, mock_neo4j_session):
        """Multiple keywords → per-keyword search + deduplication."""
        mock_neo4j_session.run.side_effect = [
            [{"uid": "E_01", "name": "电压过低", "label": "Cause",
              "source_doc": "", "source_page": ""}],
            [{"uid": "E_01", "name": "电压过低", "label": "Cause",
              "source_doc": "", "source_page": ""}],
        ]
        results = search_entities("电压 过低")
        assert len(results) == 1  # deduplicated

    def test_no_match(self, mock_neo4j_session):
        """No matching entities → []."""
        mock_neo4j_session.run.return_value = []
        assert search_entities("zzz_nonexistent") == []


# ======================================================================
# get_node
# ======================================================================


class TestGetNode:
    """``get_node()`` — single node with incoming/outgoing relations."""

    def test_found(self, mock_neo4j_session):
        """Existing UID returns full node with filtered relations."""
        mock_neo4j_session.run.return_value.single.return_value = {
            "uid": "S_CONT_01",
            "name": "接触器线圈烧毁",
            "label": "Symptom",
            "properties": {"name": "接触器线圈烧毁", "source_doc": "手册"},
            "incoming": [],
            "outgoing": [
                {"type": "CAUSED_BY", "to_uid": "C_01",
                 "to_name": "电压过低", "priority": 1},
            ],
        }
        node = get_node("S_CONT_01")
        assert node is not None
        assert node["name"] == "接触器线圈烧毁"
        assert len(node["relations"]["outgoing"]) == 1
        # None-typed relations should be filtered out
        assert all(r["type"] is not None for r in node["relations"]["incoming"])

    def test_not_found(self, mock_neo4j_session):
        """Non-existent UID → None."""
        mock_neo4j_session.run.return_value.single.return_value = None
        assert get_node("NONEXISTENT") is None


# ======================================================================
# expand_node
# ======================================================================


class TestExpandNode:
    """``expand_node()`` — center node + neighbors + edges."""

    def test_expand(self, mock_neo4j_session):
        """Returns center, nodes (deduped), and edges."""
        center_mock = MagicMock()
        center_mock.single.return_value = {
            "uid": "S_CONT_01", "name": "接触器线圈烧毁", "label": "Symptom",
        }
        neighbors = [
            {"uid": "C_01", "name": "电压过低", "label": "Cause",
             "relation": "CAUSED_BY", "from_uid": "S_CONT_01",
             "to_uid": "C_01", "priority": 1},
            {"uid": "T_01", "name": "万用表", "label": "Tool",
             "relation": "REQUIRES_TOOL", "from_uid": "S_CONT_01",
             "to_uid": "T_01", "priority": None},
        ]
        mock_neo4j_session.run.side_effect = [center_mock, neighbors]

        result = expand_node("S_CONT_01")
        assert result["center"]["name"] == "接触器线圈烧毁"
        assert len(result["nodes"]) == 3  # center + 2 neighbors
        assert len(result["edges"]) == 2
        # Edge with priority=1 should have it; edge with priority=None should not
        edge_with_priority = [e for e in result["edges"] if "priority" in e]
        assert len(edge_with_priority) == 1

    def test_expand_no_neighbors(self, mock_neo4j_session):
        """Node with no neighbors → single-node result."""
        center_mock = MagicMock()
        center_mock.single.return_value = {
            "uid": "S_ALONE", "name": "孤立节点", "label": "Symptom",
        }
        mock_neo4j_session.run.side_effect = [center_mock, []]
        result = expand_node("S_ALONE")
        assert len(result["nodes"]) == 1
        assert result["edges"] == []


# ======================================================================
# graph_search
# ======================================================================


class TestGraphSearch:
    """``graph_search()`` — Symptom → Cause → Step chain traversal."""

    def test_by_query(self, mock_neo4j_session):
        """Query matches symptom → traverse the KG chain."""
        symptom_result = [{"uid": "S_CONT_01"}]
        traversal_result = [{
            "symptom": "接触器线圈烧毁",
            "causes": [{"cause": "电源电压过低", "priority": 1,
                        "check_method": "measure", "check_time": "1min",
                        "requires_shutdown": False}],
            "steps": ["万用表测电压"],
            "tools": ["万用表"],
            "precautions": ["断电挂牌"],
            "source_doc": "手册",
            "source_page": "P42",
        }]
        mock_neo4j_session.run.side_effect = [symptom_result, traversal_result]

        results = graph_search(query="线圈烧毁")
        assert len(results) == 1
        assert results[0]["symptom"] == "接触器线圈烧毁"
        assert results[0]["tools"] == ["万用表"]

    def test_by_uid(self, mock_neo4j_session):
        """Direct UID skips symptom-matching query."""
        mock_neo4j_session.run.return_value = [{
            "symptom": "接触器线圈烧毁",
            "causes": [], "steps": [], "tools": [], "precautions": [],
            "source_doc": "", "source_page": "",
        }]
        results = graph_search(query="dummy", uid="S_CONT_01")
        assert len(results) == 1

    def test_no_match(self, mock_neo4j_session):
        """No matching symptom → []."""
        mock_neo4j_session.run.return_value = []
        assert graph_search(query="zzz_nonexistent") == []

    def test_multi_symptom(self, mock_neo4j_session):
        """Multiple matching symptoms each trigger a traversal."""
        mock_neo4j_session.run.side_effect = [
            [{"uid": "S_01"}, {"uid": "S_02"}],
            [{"symptom": "故障A", "causes": [], "steps": [], "tools": [],
              "precautions": [], "source_doc": "", "source_page": ""}],
            [{"symptom": "故障B", "causes": [], "steps": [], "tools": [],
              "precautions": [], "source_doc": "", "source_page": ""}],
        ]
        results = graph_search(query="故障")
        assert len(results) == 2

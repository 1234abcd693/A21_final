"""
Neo4j 图数据库客户端

提供知识图谱的增删改查操作。
"""

from typing import Any, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from core.config import settings

_driver: Optional[Any] = None


def _get_driver():
    """惰性初始化 Neo4j 驱动"""
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver


def check_connection() -> bool:
    """检查 Neo4j 是否可用"""
    try:
        with _get_driver().session() as session:
            session.run("RETURN 1")
        return True
    except ServiceUnavailable:
        return False


# ==================== 查询 ====================


def get_symptoms(keyword: str = "", limit: int = 10) -> list[dict[str, Any]]:
    """获取故障现象列表（支持关键词搜索）"""
    with _get_driver().session() as session:
        if keyword:
            result = session.run("""
                MATCH (s:Symptom)
                WHERE s.name CONTAINS $kw
                RETURN s.uid AS uid, s.name AS name
                ORDER BY s.name
                LIMIT $limit
            """, kw=keyword, limit=limit)
        else:
            result = session.run("""
                MATCH (s:Symptom)
                RETURN s.uid AS uid, s.name AS name
                ORDER BY s.name
                LIMIT $limit
            """, limit=limit)
        return [dict(r) for r in result]


def search_entities(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """根据关键词搜索所有类型的实体（图谱搜索）"""
    with _get_driver().session() as session:
        # 空格分隔多词
        keywords = query.strip().split()
        results = []
        for kw in keywords:
            result = session.run("""
                MATCH (n)
                WHERE n.name CONTAINS $kw
                   OR ANY(f IN n.primary_features WHERE f CONTAINS $kw)
                RETURN n.uid AS uid, n.name AS name,
                       labels(n)[0] AS label,
                       n.source_doc AS source_doc,
                       n.source_page AS source_page
                ORDER BY
                    CASE WHEN n.name = $kw THEN 0
                         WHEN n.name STARTS WITH $kw THEN 1
                         ELSE 2
                    END
                LIMIT $limit
            """, kw=kw, limit=limit)
            for r in result:
                d = dict(r)
                if d not in results:
                    results.append(d)
        return results[:limit]


def get_node(uid: str) -> Optional[dict[str, Any]]:
    """获取单个节点的完整信息"""
    with _get_driver().session() as session:
        result = session.run("""
            MATCH (n {uid: $uid})
            OPTIONAL MATCH (prev)-[r_in]->(n)
            OPTIONAL MATCH (n)-[r_out]->(next)
            RETURN n.uid AS uid, n.name AS name,
                   labels(n)[0] AS label,
                   properties(n) AS properties,
                   collect(DISTINCT {
                       type: type(r_in), from_uid: prev.uid, from_name: prev.name,
                       priority: r_in.priority
                   }) AS incoming,
                   collect(DISTINCT {
                       type: type(r_out), to_uid: next.uid, to_name: next.name,
                       priority: r_out.priority
                   }) AS outgoing
        """, uid=uid)
        record = result.single()
        if record is None:
            return None
        d = dict(record)
        d["relations"] = {
            "incoming": [r for r in d["incoming"] if r["type"] is not None],
            "outgoing": [r for r in d["outgoing"] if r["type"] is not None],
        }
        return d


def expand_node(uid: str) -> dict[str, Any]:
    """展开节点的直接邻居（用于图谱交互）"""
    with _get_driver().session() as session:
        # 获取中心节点
        center_result = session.run("""
            MATCH (n {uid: $uid})
            RETURN n.uid AS uid, n.name AS name, labels(n)[0] AS label
        """, uid=uid)
        center = dict(center_result.single())

        # 获取邻居
        neighbor_result = session.run("""
            MATCH (n {uid: $uid})-[r]-(m)
            RETURN DISTINCT m.uid AS uid, m.name AS name, labels(m)[0] AS label,
                   type(r) AS relation, startNode(r).uid AS from_uid, endNode(r).uid AS to_uid,
                   r.priority AS priority
        """, uid=uid)

        nodes = {center["uid"]: center}
        edges = []
        for rec in neighbor_result:
            n = {"uid": rec["uid"], "name": rec["name"], "label": rec["label"]}
            nodes[rec["uid"]] = n
            edge = {
                "from": rec["from_uid"],
                "to": rec["to_uid"],
                "type": rec["relation"],
            }
            if rec["priority"] is not None:
                edge["priority"] = rec["priority"]
            if edge not in edges:
                edges.append(edge)

        return {"center": center, "nodes": list(nodes.values()), "edges": edges}


def get_overview() -> dict[str, Any]:
    """获取图谱全貌（L2/L3 设备 + 顶级 Symptom）"""
    with _get_driver().session() as session:
        result = session.run("""
            MATCH (e:Equipment)
            RETURN e.uid AS uid, e.name AS name, 'Equipment' AS label, e.level AS level
            UNION
            MATCH (s:Symptom)
            RETURN s.uid AS uid, s.name AS name, 'Symptom' AS label, 0 AS level
        """)
        nodes = [dict(r) for r in result]

        result = session.run("""
            MATCH (a)-[r:SUBCLASS_OF|BELONGS_TO]->(b)
            RETURN a.uid AS `from`, b.uid AS `to`, type(r) AS type
            LIMIT 50
        """)
        edges = [dict(r) for r in result]

        return {"nodes": nodes, "edges": edges}


def graph_search(query: str, uid: Optional[str] = None) -> list[dict[str, Any]]:
    """
    图检索：从 Symptom 出发，沿 CAUSED_BY → FIXED_BY → NEXT_STEP 遍历。
    如果提供 uid，直接查该 Symptom；否则按名称模糊匹配。
    """
    with _get_driver().session() as session:
        if uid:
            symptoms = [{"uid": uid}]
        else:
            result = session.run("""
                MATCH (s:Symptom)
                WHERE s.name CONTAINS $query
                   OR ANY(f IN s.primary_features WHERE f CONTAINS $query)
                RETURN s.uid AS uid
                LIMIT 3
            """, parameters={"query": query})
            symptoms = [dict(r) for r in result]

        all_results = []
        for sym in symptoms:
            result = session.run("""
                MATCH (s:Symptom {uid: $uid})
                MATCH (s)-[r:CAUSED_BY]->(c:Cause)
                OPTIONAL MATCH (c)-[:FIXED_BY]->(first:Step)
                OPTIONAL MATCH (first)-[:NEXT_STEP*0..3]->(next:Step)
                OPTIONAL MATCH (first)-[:REQUIRES_TOOL]->(tool:Tool)
                OPTIONAL MATCH (first)-[:HAS_PRECAUTION]->(prec:Precaution)
                RETURN s.name AS symptom,
                       collect(DISTINCT {
                           cause: c.name, priority: r.priority,
                           check_method: c.check_method, check_time: c.check_time,
                           requires_shutdown: c.requires_shutdown
                       }) AS causes,
                       collect(DISTINCT first.name) AS steps,
                       collect(DISTINCT tool.name) AS tools,
                       collect(DISTINCT prec.name) AS precautions,
                       s.source_doc AS source_doc,
                       s.source_page AS source_page
                ORDER BY r.priority
            """, uid=sym["uid"])
            for rec in result:
                all_results.append(dict(rec))

        return all_results

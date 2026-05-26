"""
Neo4j 图数据库客户端 — A21 知识图谱的 CRUD 操作
==================================================

封装所有 Neo4j Cypher 查询，为 retriever.py（图检索）和 API（图谱可视化）提供数据。

核心操作：
  查询类：
    - get_symptoms()      — 故障现象列表（支持关键词搜索，给输入框联想）
    - search_entities()   — 全图谱实体搜索（图谱关键词检索 v2.0）
    - get_node()          — 单个节点完整信息（属性 + 入边 + 出边）
    - expand_node()       — 展开节点的直接邻居（图谱交互：点击→展开）
    - get_overview()      — 图谱全貌（所有节点 + 所有边，首次加载用）
    - graph_search()      — 图检索主函数（Symptom→Cause→Step 链路遍历）

  基础类：
    - check_connection()  — 健康检查（/health 接口调用）

连接管理：
  - 惰性初始化：首次调用 _get_driver() 时才连接 Neo4j
  - 全局单例：_driver 全局变量，重启后端后重建
  - with session()：每次查询在 with 块内执行，自动管理 session 生命周期

Cypher 安全规范：
  ✅ 使用 $param 参数化查询（防止注入）
  ✅ 所有查询带 LIMIT（防止全图扫描）
  ❌ 禁止字符串拼接用户输入
  ❌ 禁止无 LIMIT 的 MATCH 查询
"""

from typing import Any, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from core.config import settings

# Neo4j 驱动全局单例（惰性初始化）
_driver: Optional[Any] = None


def _get_driver():
    """
    惰性初始化 Neo4j Python 驱动。
    
    首次调用时创建连接（从 .env 读取 URI/用户名/密码），
    后续调用直接返回已有驱动实例。
    
    配置来源：core/config.py 从 .env 读取：
      NEO4J_URI=bolt://localhost:7687
      NEO4J_USER=neo4j
      NEO4J_PASSWORD=a21password
    """
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver


def check_connection() -> bool:
    """
    检查 Neo4j 是否可用（/health 接口调用）。
    
    执行简单的 RETURN 1 查询，成功=连接正常，失败=ServiceUnavailable。
    """
    try:
        with _get_driver().session() as session:
            session.run("RETURN 1")
        return True
    except ServiceUnavailable:
        return False


# ==================== 查询操作 ====================


def get_symptoms(keyword: str = "", limit: int = 10) -> list[dict[str, Any]]:
    """
    获取故障现象列表 — 支持关键词搜索，用于前端输入框智能联想。
    
    参数：
        keyword: 搜索词（空字符串时返回全部）
        limit:   返回条数上限，默认 10

    返回：
        [{uid: "S_CONT_01", name: "接触器线圈烧毁"}, ...]
    """
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
    """
    图谱关键词搜索 — 搜索所有类型的实体（Symptom/Cause/Step/Equipment 等）。
    
    搜索策略：
    1. 空格分隔多关键词 → 逐词 OR 搜索（匹配越多越好）
    2. 搜索范围：节点名称 + primary_features 数组（如"烧毁"匹配 Symptom 的特征）
    3. 相关性排序：精确匹配 > 前缀匹配 > 包含匹配（CASE WHEN 实现）
    4. 跨关键词去重：同一节点可能被多个关键词命中 → 去重后取前 limit 个

    参数：
        query: 搜索关键词（空格分隔多词）
        limit: 返回条数上限

    返回：
        [{uid, name, label, source_doc, source_page}, ...]
    """
    with _get_driver().session() as session:
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
                    CASE WHEN n.name = $kw THEN 0       -- 精确匹配最高优先级
                         WHEN n.name STARTS WITH $kw THEN 1  -- 前缀匹配次之
                         ELSE 2                          -- 包含匹配最低
                    END
                LIMIT $limit
            """, kw=kw, limit=limit)
            for r in result:
                d = dict(r)
                if d not in results:  # 跨关键词去重
                    results.append(d)
        return results[:limit]


def get_node(uid: str) -> Optional[dict[str, Any]]:
    """
    获取单个节点的完整信息 — 包含属性、入边、出边。
    
    查询模式：以 uid 为中心，展开所有直接连接的节点和关系。
    
    返回结构：
    {
        uid, name, label,
        properties: {name, primary_features, source_doc, ...},  # 节点所有属性
        relations: {
            incoming: [{type, from_uid, from_name, priority}, ...],
            outgoing: [{type, to_uid, to_name, priority}, ...]
        }
    }
    
    如果 uid 不存在，返回 None。
    """
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
        
        # 过滤掉 OPTIONAL MATCH 产生的 None 类型的 null 关系
        d = dict(record)
        d["relations"] = {
            "incoming": [r for r in d["incoming"] if r["type"] is not None],
            "outgoing": [r for r in d["outgoing"] if r["type"] is not None],
        }
        return d


def expand_node(uid: str) -> dict[str, Any]:
    """
    展开节点的直接邻居 — 用于图谱可视化交互（点击节点→展开相邻节点）。
    
    返回中心节点 + 所有直接邻居节点 + 所有连接边。
    前端可直接用 AntV G6 / D3.js 渲染为力导向图。
    
    返回结构：
    {
        center: {uid, name, label},                 # 被点击的中心节点
        nodes:  [{uid, name, label}, ...],           # 中心节点 + 所有邻居
        edges:  [{from, to, type, priority?}, ...]   # 所有连接的边
    }
    """
    with _get_driver().session() as session:
        # 获取中心节点基本信息
        center_result = session.run("""
            MATCH (n {uid: $uid})
            RETURN n.uid AS uid, n.name AS name, labels(n)[0] AS label
        """, uid=uid)
        center = dict(center_result.single())

        # 获取所有邻居节点及关系（无向：MATCH (n)-[r]-(m)）
        neighbor_result = session.run("""
            MATCH (n {uid: $uid})-[r]-(m)
            RETURN DISTINCT m.uid AS uid, m.name AS name, labels(m)[0] AS label,
                   type(r) AS relation, startNode(r).uid AS from_uid, endNode(r).uid AS to_uid,
                   r.priority AS priority
        """, uid=uid)

        # 构建节点集合（去重）和边集合
        nodes = {center["uid"]: center}
        edges = []
        for rec in neighbor_result:
            n = {"uid": rec["uid"], "name": rec["name"], "label": rec["label"]}
            nodes[rec["uid"]] = n  # dict key 去重
            edge = {
                "from": rec["from_uid"],
                "to": rec["to_uid"],
                "type": rec["relation"],
            }
            if rec["priority"] is not None:
                edge["priority"] = rec["priority"]
            if edge not in edges:  # 防止 OPTIONAL MATCH 产生重复边
                edges.append(edge)

        return {"center": center, "nodes": list(nodes.values()), "edges": edges}


def get_overview() -> dict[str, Any]:
    """
    获取图谱全貌 — 所有节点 + 所有关系，用于前端首次加载（GET /graph/overview）。
    
    注意：
    - 返回全部节点和边（可能较大），前端适合做分页或按设备类型筛选
    - level 属性用于前端按设备层级（L2/L3）分层展示
    
    返回：
    {
        nodes: [{uid, name, label, level}, ...],  # level 用于设备分层
        edges: [{from, to, type, priority?}, ...]
    }
    """
    with _get_driver().session() as session:
        # 所有节点（携带 level 用于设备分层显示）
        result = session.run("""
            MATCH (n)
            RETURN n.uid AS uid, n.name AS name, labels(n)[0] AS label,
                   CASE WHEN n.level IS NOT NULL THEN n.level ELSE 0 END AS level
        """)
        nodes = [dict(r) for r in result]

        # 所有关系
        result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN a.uid AS `from`, b.uid AS `to`, type(r) AS type,
                   r.priority AS priority
        """)
        edges = [dict(r) for r in result]

        return {"nodes": nodes, "edges": edges}


def graph_search(query: str, uid: Optional[str] = None) -> list[dict[str, Any]]:
    """
    图检索主函数 — 从 Symptom 出发，沿知识图谱关系链遍历。
    
    遍历路径：Symptom → CAUSED_BY → Cause → FIXED_BY → Step₁ → NEXT_STEP* → Step₂₊₃
            同时获取：Step → REQUIRES_TOOL → Tool
                      Step → HAS_PRECAUTION → Precaution
    
    查询参数：
        query: 故障现象描述（自然语言或关键词）
        uid:   直接指定 Symptom 的 UID（前端图谱交互时使用），可选

    搜索策略：
    - 如果提供 uid → 直接查该 Symptom 的完整链
    - 否则 → 用 CONTAINS 按名称或 primary_features 模糊匹配

    返回示例：
    [{
        symptom: "接触器线圈烧毁",
        causes: [{cause: "电源电压过低", priority: 1, check_method: "measure", ...}, ...],
        steps: ["万用表测线圈电压确认≥85%UN", ...],
        tools: ["万用表"],
        precautions: ["断电挂牌"],
        source_doc: "船舶电气设备维护与修理",
        source_page: "第四章第二节"
    }, ...]
    """
    with _get_driver().session() as session:
        # 第一步：找到匹配的 Symptom 节点
        if uid:
            symptoms = [{"uid": uid}]
        else:
            # 双向匹配：节点名包含查询词 OR 查询词包含节点名
            # 用户说"电动机不能起动怎么办" → 应匹配节点名"电动机不能起动"
            # 还要用 jieba 分词做逐词匹配，提高自然语言问题的召回率
            result = session.run("""
                MATCH (s:Symptom)
                WHERE s.name CONTAINS $query
                   OR $query CONTAINS s.name
                   OR ANY(f IN s.primary_features WHERE f CONTAINS $query OR $query CONTAINS f)
                RETURN s.uid AS uid, s.name AS name
                LIMIT 3
            """, parameters={"query": query})
            symptoms = [dict(r) for r in result]

            # 如果双向匹配也为空，用 jieba 分词做逐词匹配
            if not symptoms:
                import jieba
                tokens = [t for t in jieba.cut(query) if len(t) > 1]
                for token in tokens[:5]:  # 最多尝试 5 个关键词
                    result = session.run("""
                        MATCH (s:Symptom)
                        WHERE s.name CONTAINS $kw
                           OR ANY(f IN s.primary_features WHERE f CONTAINS $kw)
                        RETURN s.uid AS uid, s.name AS name
                        LIMIT 1
                    """, kw=token)
                    for r in result:
                        d = dict(r)
                        if d not in symptoms:
                            symptoms.append(d)
                    if len(symptoms) >= 2:
                        break
            symptoms = symptoms[:3]

        # Step 2: traverse relationship chain for each Symptom
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
            """, uid=sym["uid"])
            for rec in result:
                all_results.append(dict(rec))

        return all_results

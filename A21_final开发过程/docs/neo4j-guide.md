# Neo4j 环境检查与配置指南

> 检查日期: 2026-05-25 | 版本: Community 2026.02.3

---

## 一、环境状态 ✅

| 检查项 | 状态 | 详情 |
|--------|:--:|------|
| Neo4j 版本 | ✅ | Community 2026.02.3（最新） |
| 安装路径 | ✅ | `neo4j/neo4j-community-2026.02.3/` |
| Java 环境 | ✅ | Java 26（JDK 26 已安装） |
| APOC 插件 | ✅ | `apoc-2026.02.3-core.jar` 已就绪 |
| GenAI 插件 | ✅ | `neo4j-genai-plugin-2026.02.3.jar`（GraphRAG 辅助，备选） |
| Cypher Shell | ✅ | `cypher-shell.bat` 可用 |
| 启动脚本 | ✅ | `neo4j.bat` 可用 |

## 二、需要做的配置

### 2.1 允许 APOC 导出

编辑 `neo4j/neo4j-community-2026.02.3/conf/neo4j.conf`，找到或添加：

```ini
# 允许 APOC 过程（U盘同步导出需要）
dbms.security.procedures.unrestricted=apoc.*
```

搜索 `dbms.security.procedures.unrestricted` 这一行，把注释 `#` 去掉，值改成 `apoc.*`。

### 2.2 设置初始密码

首次启动后，浏览器打开 `http://localhost:7474`：
- 用户名: `neo4j`
- 初始密码: `neo4j`
- 系统会强制要求改密码 → 设为 `a21password`

### 2.3 创建环境变量文件

在 `backend/.env` 中创建：

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=a21password
```

Python 代码中这样用：
```python
import os
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)
```

## 三、导入知识图谱数据

```powershell
# 1. 启动 Neo4j
cd neo4j\neo4j-community-2026.02.3
.\bin\neo4j.bat start

# 2. 等待启动（~10 秒），检查状态
.\bin\neo4j.bat status

# 3. 导入数据
.\bin\cypher-shell.bat -u neo4j -p a21password -f ..\..\import.cypher

# 4. 验证
.\bin\cypher-shell.bat -u neo4j -p a21password
# 然后在 cypher-shell 里输入：
# MATCH (n) RETURN labels(n), count(n);
```

## 四、启动与停止

```powershell
# 启动（后台服务）
bin\neo4j.bat start

# 停止
bin\neo4j.bat stop

# 查看状态
bin\neo4j.bat status

# 前台运行（看日志，调试用）
bin\neo4j.bat console
```

## 五、Web 管理界面

- 地址: `http://localhost:7474`
- 可以在这里写 Cypher 查询、可视化图谱、查看数据

## 六、GenAI 插件说明

`neo4j-genai-plugin` 是 Neo4j 官方的 GraphRAG 插件，提供了**图增强检索**能力（向量检索 + 图遍历结合）。

**我们暂不使用它**。原因：
- 我们的三路检索（Cypher + BM25 + Chroma 向量）已经覆盖了它的功能
- 引入额外插件增加复杂度和依赖
- 如果后续发现检索质量不足，回来看它作为备选

## 七、Community 版是否够用？

| 功能 | 社区版 | 企业版 | 我们需要 |
|------|:--:|:--:|:--:|
| Cypher 查询 | ✅ | ✅ | ✅ |
| APOC 过程 | ✅ | ✅ | ✅（导出用） |
| 实体/关系上限 | 无限制 | 无限制 | 500/80，远超 |
| 集群/高可用 | ❌ | ✅ | ❌（不需要） |
| 在线备份 | ❌ | ✅ | 用 Cypher 导出替代 |
| 多数据库 | ❌ | ✅ | ❌（单库够用） |

**社区版完全够用**，我们没有任何需要企业版的功能。

# A21 数据模型设计

> 版本: v1.0 | Neo4j 本体已有（知识图谱设计文档.md），本文聚焦 Chroma + SQLite + 配置文件

---

## 零、安装说明

**不需要额外安装。** Chrome 和 SQLite 都已在 `requirements.txt` 中覆盖：

| 组件 | 安装方式 | 说明 |
|------|----------|------|
| Chroma | `pip install chromadb` | 已在 requirements.txt，纯 Python，启动即用 |
| SQLite | Python 标准库 `import sqlite3` | Python 自带，零安装零配置 |

```powershell
conda activate a21
pip install -r backend/requirements.txt   # 一次性装好全部
```

---

## 一、Chroma 向量库

### 1.1 存储结构

```
data/chroma_db/            ← 本地目录，gitignored
├── chroma.sqlite3         ← 元数据（自动生成）
└── 向量索引文件             ← embedding 向量（自动生成）
```

### 1.2 Collection 设计

**只有一个 Collection：`knowledge_chunks`**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | str | 唯一 chunk ID | `chunk_motor_001` |
| `document` | str | 文本内容 | `"电动机不能起动时，首先应检查电源电压..."` |
| `embedding` | float[] | bge-base-zh-v1.5 计算的 768 维向量 | 自动生成 |

**Metadata（每条 chunk 的附加信息）**:

```json
{
  "doc_name": "船舶电气设备维护与修理",
  "doc_type": "maintenance_manual",
  "page": "第五章第三节",
  "page_number": 142,
  "chunk_index": 3,
  "total_chunks": 15,
  "source_file_hash": "a1b2c3d4",
  "graph_entities": ["S_MOTOR_01", "E_ASYNCH_MOTOR"],
  "created_at": "2026-05-25T14:30:00",
  "keywords": ["电动机", "不能起动", "电源电压"]
}
```

| 元数据字段 | 类型 | 必填 | 说明 |
|-----------|------|:--:|------|
| doc_name | str | ✅ | 来源文档名 |
| doc_type | str | ✅ | maintenance_manual / fault_case / repair_plan / uploaded |
| page | str | ✅ | 章节页码（人类可读） |
| page_number | int | ❌ | 数字页码（用于排序） |
| chunk_index | int | ✅ | 在该文档中是第几块 |
| total_chunks | int | ✅ | 该文档共几块 |
| source_file_hash | str | ✅ | 源文件 SHA256（用于去重） |
| graph_entities | str[] | ❌ | 关联的 Neo4j 节点 UID |
| keywords | str[] | ❌ | jieba 提取的关键词（用于 BM25） |
| created_at | str | ✅ | 创建时间 |

### 1.3 分块策略

```
原始文档: "第五章第三节 电动机故障分析\n电动机不能起动时..."
    │
    ▼
分块参数:
  chunk_size = 512 tokens（约 350 中文字）
  chunk_overlap = 64 tokens（约 40 中文字）
    │
    ▼
chunk_1: "第五章第三节 电动机故障分析\n电动机不能起动时，首先应检查..."
chunk_2: "...应检查电源电压是否正常。若电压正常，则进一步检查..."  ← 重叠部分
chunk_3: "...检查定子绕组绝缘电阻。用绝缘电阻表测量..."
```

**为什么重叠**: 防止关键信息正好落在分块边界被切断。

### 1.4 Python 操作示例

```python
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="data/chroma_db")

# 获取或创建 collection
collection = client.get_or_create_collection(
    name="knowledge_chunks",
    metadata={"description": "船舶故障诊断知识库", "embedding_model": "bge-base-zh-v1.5"}
)

# 添加文档
collection.add(
    ids=["chunk_motor_001"],
    documents=["电动机不能起动时，首先应检查电源电压是否正常..."],
    metadatas=[{
        "doc_name": "船舶电气设备维护与修理",
        "page": "第五章第三节",
        "chunk_index": 0,
        "graph_entities": ["S_MOTOR_01"]
    }]
)

# 语义检索
results = collection.query(
    query_texts=["电动机打不着火"],
    n_results=5,
    where={"doc_type": "maintenance_manual"}  # 可选：元数据过滤
)
```

### 1.5 索引与性能

- Chroma 默认使用 HNSW 索引（分层可导航小世界图）
- 500 条 chunk → 检索耗时 <50ms
- 5000 条 chunk → 检索耗时 <200ms
- 不需要额外配置，开箱即用

---

## 二、SQLite 数据库

### 2.1 存储位置

```
data/feedbacks.db          ← 本地文件，gitignored
```

### 2.2 表结构

#### 表 1: feedbacks（用户反馈）

```sql
CREATE TABLE feedbacks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id  TEXT NOT NULL UNIQUE,       -- 来自 /ask metadata 的 message_id
    question    TEXT NOT NULL,              -- 用户问题
    answer_text TEXT NOT NULL,              -- AI 完整回答
    rating      INTEGER NOT NULL CHECK(rating IN (-1, 0, 1)),  -- -1👎 0取消 1👍
    comment     TEXT,                       -- 用户文字评价（可选）
    retrieved_chunks TEXT NOT NULL,         -- JSON: [{chunk_id, doc_name, page}]
    traceability TEXT,                      -- JSON: {confidence, keywords_matched, ...}
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_feedbacks_rating ON feedbacks(rating);
CREATE INDEX idx_feedbacks_created ON feedbacks(created_at);
```

示例数据:
```json
{
  "id": 1,
  "message_id": "msg_042",
  "question": "接触器线圈烧毁怎么修？",
  "answer_text": "根据资料显示...",
  "rating": 1,
  "retrieved_chunks": "[{\"chunk_id\":\"doc_042\",\"doc_name\":\"船舶电气设备维护与修理\",\"page\":\"P42\"}]",
  "traceability": "{\"confidence\":\"green\",\"keywords_matched\":5,\"keywords_total\":5}",
  "created_at": "2026-05-25T14:30:05"
}
```

#### 表 2: conversations（对话会话）

```sql
CREATE TABLE conversations (
    session_id  TEXT PRIMARY KEY,           -- UUID
    title       TEXT NOT NULL,              -- 会话标题（取第一条问题的前 20 字）
    message_count INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
```

#### 表 3: messages（对话消息）

```sql
CREATE TABLE messages (
    message_id  TEXT PRIMARY KEY,           -- UUID
    session_id  TEXT NOT NULL REFERENCES conversations(session_id),
    role        TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content     TEXT NOT NULL,              -- 消息文本
    citations   TEXT,                       -- JSON: [{num, chunk_id, doc_name, page, graph_nodes}]
    traceability TEXT,                      -- JSON: {confidence, ...}
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_messages_session ON messages(session_id);
```

#### 表 4: sync_log（同步日志）

```sql
CREATE TABLE sync_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    direction   TEXT NOT NULL CHECK(direction IN ('export', 'import')),
    file_path   TEXT,                       -- 导出/导入的文件路径
    stats       TEXT NOT NULL,              -- JSON: {entities, relationships, chunks, feedbacks}
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### 2.3 Python 操作示例

```python
import sqlite3
import json

conn = sqlite3.connect("data/feedbacks.db")

# 插入反馈
conn.execute("""
    INSERT OR REPLACE INTO feedbacks (message_id, question, answer_text, rating, retrieved_chunks, traceability)
    VALUES (?, ?, ?, ?, ?, ?)
""", [
    "msg_042",
    "接触器线圈烧毁怎么修？",
    "根据资料显示...",
    1,
    json.dumps([{"chunk_id": "doc_042", "doc_name": "维护手册", "page": "P42"}]),
    json.dumps({"confidence": "green", "keywords_matched": 5, "keywords_total": 5})
])
conn.commit()

# 查询最近 30 条点赞的反馈（供优化器使用）
rows = conn.execute("""
    SELECT question, answer_text, retrieved_chunks, rating
    FROM feedbacks
    WHERE rating != 0
    ORDER BY created_at DESC
    LIMIT 30
""").fetchall()
```

### 2.4 注意

- SQLite 不支持并发写入。FastAPI 的异步特性不影响——每个请求串行写 SQLite 即可，写入耗时 <1ms。
- 不需要 ORM（如 SQLAlchemy）。两张表 + 几条简单查询，原生 sqlite3 足够。
- 数据库文件自动创建：`sqlite3.connect("data/feedbacks.db")` 如果文件不存在会自动创建。

---

## 三、RAG 参数配置

### 3.1 存储位置

```
backend/rag/params.json
```

### 3.2 结构

```json
{
  "version": 1,
  "updated_at": "2026-05-25T14:30:00",
  "updated_by": "grid_search",
  "retrieval": {
    "alpha": 0.3,
    "beta": 0.5,
    "gamma": 0.2,
    "top_k_per_source": 5,
    "rerank_keep": 5
  },
  "chunking": {
    "chunk_size": 512,
    "chunk_overlap": 64
  },
  "generation": {
    "temperature": 0.1,
    "max_tokens": 512,
    "system_prompt": "你是船舶电气设备维修专家..."
  },
  "defaults": {
    "alpha": 0.35,
    "beta": 0.35,
    "gamma": 0.3,
    "top_k_per_source": 5,
    "rerank_keep": 5
  }
}
```

| 字段 | 说明 |
|------|------|
| version | 配置版本号（调优后递增） |
| updated_by | 谁更新的："manual" / "grid_search" / "default" |
| retrieval.alpha | BM25 权重 |
| retrieval.beta | 向量检索权重 |
| retrieval.gamma | 图检索权重（α+β+γ=1） |
| retrieval.top_k_per_source | 每路检索返回数 |
| retrieval.rerank_keep | 融合后保留数 |
| generation.temperature | LLM 温度参数 |
| defaults | 初始默认值（用于"恢复默认"按钮） |

### 3.3 读写方式

```python
import json

class ParamsManager:
    PATH = "rag/params.json"

    @classmethod
    def load(cls) -> dict:
        with open(cls.PATH) as f:
            return json.load(f)

    @classmethod
    def save(cls, params: dict):
        with open(cls.PATH, "w") as f:
            json.dump(params, f, indent=2, ensure_ascii=False)

    @classmethod
    def reset_to_defaults(cls):
        params = cls.load()
        params["retrieval"] = params["defaults"].copy()
        params["version"] += 1
        params["updated_by"] = "manual_reset"
        cls.save(params)
```

---

## 四、数据存储总览

```
A21_final/
├── data/                     ← 本地数据目录 (gitignored)
│   ├── chroma_db/            ← Chroma 向量库
│   │   └── knowledge_chunks  ← 唯一 collection
│   └── feedbacks.db          ← SQLite（4 张表）
│
├── backend/rag/
│   └── params.json           ← RAG 参数配置
│
├── neo4j/.../data/           ← Neo4j 图数据 (gitignored)
│   └── databases/neo4j/      ← 7 节点 8 关系
│
└── import.cypher             ← KG 初始数据（版本控制）
```

| 存储 | 格式 | 内容 | 大小估算 |
|------|------|------|------|
| Neo4j | 图数据库 | 实体 + 关系 | ~50 MB |
| Chroma | 向量库 | 文档切片 + embedding | ~10 MB |
| SQLite | 关系数据库 | 反馈 + 对话 + 日志 | ~1 MB |
| params.json | 文本文件 | RAG 参数 | <1 KB |

---

## 五、版本记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-25 | v1.0 | 初始数据模型：Chroma 1 collection + SQLite 4 表 + params.json |

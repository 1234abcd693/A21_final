# U盘跨设备数据同步

## 一句话解释

把一台电脑上的知识图谱、向量库、反馈数据**打包导出到 U 盘**，插到另一台电脑上**导入合并**。

## 典型场景

```
船 A 的电脑：
  积累了 3 个月的故障案例和维修记录
       ↓ 导出到 U 盘
       ↓
     [U盘]
       ↓ 插入船 B 的电脑
       ↓ 导入合并
船 B 的电脑：
  现在也有船 A 的知识了
```

## 同步哪些数据？

```
同步包 (U盘上的一个文件夹或 zip)
├── neo4j_dump.cypher      ← 知识图谱（Cypher 语句）
├── chroma_db/             ← 向量库原始文件
├── feedbacks.db           ← 用户反馈记录
├── params.json            ← RAG 调优参数
└── sync_info.json         ← 元信息（时间、来源、模型名等）
```

**不同步的**：对话历史（存在本机就行，换设备没意义）。

---

## Neo4j 知识图谱怎么迁移？

### 我们的方案：Cypher 导出/导入

**原理**：把图谱转成 Cypher 语句文本文件，目标设备执行这些语句重建整个图谱。

**导出**（设备 A）：
```sql
-- 在 Neo4j 中执行这条 Cypher（需要 APOC 插件）
CALL apoc.export.cypher.all(
  'neo4j_dump.cypher',
  {format: 'cypher-shell'}
)
```

导出文件内容示例：
```sql
CREATE (:设备 {name: '发动机', source: '维修手册.pdf', page: 3});
CREATE (:零件 {name: '燃油泵', source: '维修手册.pdf', page: 5});
CREATE (:故障 {name: '漏油', severity: '高'});
CREATE (:原因 {name: '密封圈老化', probability: '常见'});
CREATE (:步骤 {name: '更换密封圈', tool: '扳手'});
-- 创建关系
MATCH (a:零件 {name: '燃油泵'}), (b:故障 {name: '漏油'})
CREATE (a)-[:HAS_FAILURE]->(b);
```

**导入**（设备 B）：
```bash
# 执行 Cypher 文件
cat neo4j_dump.cypher | cypher-shell -u neo4j -p password
```

注意：实际代码里不用 `cat`，用 `MERGE` 替代 `CREATE` 避免重复创建已存在的实体。见下文"冲突处理"。

### 为什么不用停服拷贝目录？

| 方式 | 需要停服？ | 能增量合并？ | 跨版本兼容？ | 我们 500 实体够不够快？ |
|------|:---:|:---:|:---:|:---:|
| Cypher 导出 ✅ | 否 | 能 | 能 | 瞬间 |
| 停服拷贝目录 ❌ | 是 | 否（只能覆盖） | 否（版本要一致） | — |
| neo4j-admin dump ❌ | 是 | 否（只能覆盖） | 否 | — |

Cypher 方式：不停服、可增量合并、跨版本兼容。500 实体导出就几百行文本，导入不到 1 秒。

---

## Chroma 向量库怎么迁移？

### 直接拷贝目录

Chroma 的数据在一个文件夹里：
```
chroma_db/
├── chroma.sqlite3        ← 元数据
└── 向量数据文件
```

**导出**：确保没有正在写入的进程，直接复制整个文件夹。

**导入**：复制到目标位置，Chroma 重新加载。

### ⚠️ 坑：embedding 模型必须一致

设备 A 用 MiniLM 算的向量，设备 B 也得用 MiniLM 才能正确查询。

`sync_info.json` 里记录：
```json
{
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
  "total_chunks": 350
}
```

导入时自动检查：模型不一致 → 提示用户安装对应模型，或重新计算全部向量。

---

## 完整操作流程

### 导出

```
用户点击"导出知识包"
        │
        ▼
┌──────────────────────────┐
│ 1. 弹出文件夹选择器       │  Electron IPC → 系统对话框
│    用户选 U 盘路径        │  例如 E:\sync\
├──────────────────────────┤
│ 2. 导出 Neo4j           │
│    Cypher: apoc.export   │  → neo4j_dump.cypher
├──────────────────────────┤
│ 3. 导出 Chroma          │
│    复制 chroma_db/       │  → chroma_db/
├──────────────────────────┤
│ 4. 导出 SQLite          │
│    复制 feedbacks.db     │  → feedbacks.db
├──────────────────────────┤
│ 5. 导出参数              │
│    复制 params.json      │  → params.json
├──────────────────────────┤
│ 6. 生成 sync_info.json  │  → 记录导出时间、统计信息
├──────────────────────────┤
│ 7. 可选：打包成 zip      │  → A21_sync_20260522.zip
└──────────────────────────┘
```

### 导入

```
用户点击"导入知识包"，选择 zip 或目录
        │
        ▼
┌──────────────────────────┐
│ 1. 校验 sync_info.json   │
│    · 版本是否兼容？       │
│    · embedding 模型一致？ │
│    → 不一致：警告，选择继续/取消│
├──────────────────────────┤
│ 2. 合并 Neo4j           │
│    逐条执行 Cypher       │
│    用 MERGE 避免重复     │
│    新实体创建，旧实体跳过 │
├──────────────────────────┤
│ 3. 合并 Chroma          │
│    检查文档 hash         │
│    相同 → 跳过           │
│    新的 → 插入           │
├──────────────────────────┤
│ 4. 合并反馈              │
│    INSERT OR IGNORE      │
├──────────────────────────┤
│ 5. 合并参数              │
│    提示用户选择：         │
│    保留当前 / 替换为导入的 │
└──────────────────────────┘
```

---

## 冲突策略

| 数据类型 | 冲突判定 | 策略 |
|----------|---------|------|
| Neo4j 实体 | 同名实体已存在 | **MERGE**：旧属性保留，新属性补充 |
| Chroma 文档 | 内容 hash 相同 | **跳过** |
| 反馈数据 | 同一 ID 已存在 | **跳过**（INSERT OR IGNORE） |
| 调优参数 | 参数不同 | **用户选择**：保留 / 替换 |

---

## 同步信息文件格式

```json
{
  "version": "1.0",
  "export_time": "2026-05-22T14:30:00",
  "source_device": "ENGINE-ROOM-PC-01",
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
  "statistics": {
    "neo4j_entities": 520,
    "neo4j_relationships": 95,
    "chroma_chunks": 350,
    "feedbacks": 42
  }
}
```

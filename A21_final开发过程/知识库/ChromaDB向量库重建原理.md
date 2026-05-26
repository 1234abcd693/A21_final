# ChromaDB 向量库重建技术文档

> 版本: v2.0 | 日期: 2026-05-26

---

## 一、原理概述

ChromaDB 是 A21 系统的语义检索层。用户问题 → bge-base-zh-v1.5 编码 → 在向量空间中找最相似的文档片段 → 注入 LLM Prompt。

### 为什么需要重建

| 维度 | v1.0（旧） | v2.0（新） | 改进 |
|------|-----------|-----------|------|
| **分块策略** | 固定512字符 | 滑动窗口300字 + 句边界感知 | 避免句子截断 |
| **噪音清洗** | 无 | 去图片标记/目录/表格 | 减少无用内容 |
| **KG关联** | 无 | 每条chunk标记关联的Neo4j实体UID | 检索可溯源 |
| **Chunk数** | 658 | 1920 | 更密集覆盖 |
| **内容来源** | 全文本无差别切分 | KG引导提取 + 全文本补充 | 故障知识优先 |

### 数据流

```
源文本 (293K chars)
    │
    ├─→ KG引导提取 ──→ Neo4j 127 Symptom节点驱动搜索上下文
    │                   367个KG相关上下文
    │
    └─→ 全文滑动窗口 ──→ 1251个通用知识窗口
    │
    ▼
噪音清洗 + 去重 → 1920 chunks
    │
    ▼
bge-base-zh-v1.5 编码 (768维)
    │
    ▼
ChromaDB knowledge_chunks collection
  metadata: entity_uid, entity_name, entity_label, source_page
```

### 与 Neo4j 的联动

每条 ChromaDB chunk 的 metadata 中包含：
- `entity_uid`: 对应的 Neo4j 实体 UID（如 `S_CONT_01`）
- `entity_name`: 实体名称（如 `接触器线圈烧毁`）
- `entity_label`: 实体类型（`Symptom`/`Cause`/`Step`）

检索命中某条 chunk 后，可通过 `entity_uid` 追溯到 Neo4j 中的完整图谱链。

---

## 二、实现细节

### 2.1 滑动窗口分块

```python
def sliding_window_chunks(text, window=300, overlap=50):
    # 1. 按句号、换行等边界切句子
    sentences = re.split(r'(?<=[。！？\n])\s*', text)
    # 2. 累积句子直到达到 window 大小
    # 3. 保留最后 overlap 字符作为与下一块的上下文重叠
```

**参数选择**：
- `window=300`: 约200中文字，适合 Qwen2.5-1.5B 的 2048 token 上下文窗口
- `overlap=50`: 约35中文字，保证关键信息不落在边界

### 2.2 KG引导提取

```python
for symptom in Neo4j.all_symptoms:
    在源文本中搜索 symptom.name
    提取匹配位置前后各300字符的上下文
    清洗后加入 chunk 候选
```

### 2.3 噪音清洗

```python
clean_text():
    - 移除 [Image:xxx] 图片标记
    - 移除 [目录] 行
    - 移除纯表格线(|---|)
    - 移除页码标记(*p.42*)
    - 合并多余空白和空行
```

---

## 三、使用方式

### 重建命令

```powershell
cd backend
python tools/rebuild_chroma.py
```

### 验证

```python
from rag.vector_store import search, get_collection_count
print(get_collection_count())  # 应为 1920
search("接触器线圈烧毁", n_results=3)  # 应返回 KG 标记的 chunk
```

### 数据库位置

- 旧数据：自动删除
- 新数据：`backend/data/chroma_db/`
- 后端启动时自动加载

---

## 四、版本记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-26 | v2.0 | 滑动窗口分块 + KG引导提取 + 噪音清洗 + KG元数据关联 |
| 2026-05-26 | v1.0 | 初始版本，固定512字符分块，658 chunks |

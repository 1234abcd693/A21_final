# A21 开发规范与路线图

> 版本: v1.0 | Agent 协同开发的操作手册

---

## 一、开发核心原则

### 1.1 模块独立

每个模块**只依赖抽象接口，不依赖具体实现**。Agent 开发模块 A 时，不需要知道模块 B 内部怎么写的，只需要知道模块 B 的接口签名。

### 1.2 接口先行

开发任何模块前，**先定义接口（抽象基类 + 方法签名 + 类型注解）**。接口确认后才写实现。

### 1.3 小步提交

一个逻辑改动 = 一次 commit。不做"攒了一天一起提交"的事。

---

## 二、Agent 任务分配规范

### 2.1 如何拆分工作给 Agent

把功能拆分到**单个 Agent 能在一次会话中完成**的粒度：

| ✅ 好的拆分 | ❌ 差的拆分 |
|------------|------------|
| "在 backend/rag/retriever.py 实现 BM25 检索器" | "实现整个 RAG 检索模块" |
| "在 backend/api/symptoms.py 实现 GET /symptoms 路由" | "实现所有 API" |
| "在 frontend/src/components/InputBox.vue 实现输入框" | "做一个聊天界面" |

### 2.2 Agent 任务模板

每次给 Agent 派活时，提供以下信息：

```markdown
## 任务: [一句话描述]

### 参考文档
- API 契约: docs/api-contract.md (第 X 节)
- 数据模型: docs/data-model.md (第 Y 节)
- 架构设计: docs/architecture.md (第 Z 节)

### 输入
- 接收什么参数？什么格式？

### 输出
- 返回什么？什么格式？
- 成功返回示例
- 错误返回示例

### 约束
- 必须: [列表]
- 禁止: [列表]
- 文件路径: [精确到文件]

### 验证
- 写完后的验证命令
```

### 2.3 可并行开发的任务组

以下任务组之间**没有依赖**，可以同时派给多个 Agent：

```
组 A: backend/core/config.py + backend/core/llm.py    (配置 + LLM 封装)
组 B: backend/kg/neo4j_client.py                       (Neo4j 操作)
组 C: backend/rag/retriever.py (BM25 部分)             (关键词检索)
组 D: backend/rag/retriever.py (Chroma 部分)           (向量检索，依赖组A的embedding配置)
组 E: frontend/ 基础骨架                                 (Vue + Vite + Electron 搭建)
```

---

## 三、代码标准（Agent 必须遵守）

### 3.1 Python

```python
# ✅ 必须
from abc import ABC, abstractmethod

class BaseRetriever(ABC):
    """检索器抽象基类"""

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict[str, str]]:
        """搜索文档，返回 [{chunk_id, doc_name, page, text, score}]"""
        pass

# ✅ 必须：类型注解 + docstring
def fuse_results(
    bm25_results: list[dict],
    vector_results: list[dict],
    graph_results: list[dict],
    top_k: int = 5
) -> list[dict]:
    """RRF 融合排序，返回 Top-K 结果"""
    ...
```

```python
# ❌ 禁止
def search(x): ...           # 无类型注解、无docstring
password = "hardcoded123"    # 硬编码密码
import *                     # 星号导入
session = driver.session()   # 未用 with 管理 Neo4j session
```

### 3.2 Cypher

```cypher
// ✅ 必须：$param 参数化、LIMIT、MERGE 幂等
MATCH (s:Symptom {name: $name})-[r:CAUSED_BY]->(c:Cause)
RETURN r.priority, c.name
ORDER BY r.priority
LIMIT $limit

// ❌ 禁止：字符串拼接、无 LIMIT
"MATCH (s:Symptom {name: '" + user_input + "'}) RETURN s"
MATCH (n) RETURN n   // 无 LIMIT
```

### 3.3 Vue 3

```vue
<!-- ✅ 必须 -->
<script setup>
defineProps({
  question: { type: String, required: true },
  loading: { type: Boolean, default: false }
})
const emit = defineEmits(['send', 'clear'])
</script>
```

### 3.4 提交信息格式

```
模块: 做了什么

如:
rag: 实现 BM25 检索器，支持 jieba 中文分词
backend: 添加 /api/v1/ask SSE 流式路由
frontend: 完成 InputBox.vue 组件，含智能联想
```

---

## 四、开发路线图

### 第 1 步：基础设施（1-2 天）← 从这里开始

| 任务 | 文件 | 依赖 | 可并行？ |
|------|------|:--:|:--:|
| FastAPI 应用骨架 | `backend/main.py` | 无 | ✅ |
| 配置文件 | `backend/core/config.py`, `.env` | 无 | ✅ |
| Neo4j 客户端 | `backend/kg/neo4j_client.py` | config | ✅ |
| Chroma 初始化 | `backend/rag/vector_store.py` | config | ✅ |
| SQLite 建表 | `backend/data/database.py` | 无 | ✅ |
| 健康检查路由 | `backend/api/health.py` | main.py | ❌（需 main.py 先完成） |
| 前端骨架 | `frontend/` (Vite + Vue + Electron) | 无 | ✅ |
| params.json 初始值 | `backend/rag/params.json` | 无 | ✅ |

**启动方式**：同时派 5-6 个 Agent，各自负责以上任务。都完成后集成到 `main.py`。

### 第 2 步：RAG 核心（2-3 天）

| 任务 | 文件 | 依赖 |
|------|------|------|
| 实体识别 | `backend/rag/entity_extractor.py` | jieba |
| BM25 检索器 | `backend/rag/bm25_retriever.py` | entity_extractor |
| 向量检索器 | `backend/rag/vector_retriever.py` | vector_store |
| 图检索器 | `backend/rag/graph_retriever.py` | neo4j_client, entity_extractor |
| RRF 融合 | `backend/rag/fusion.py` | 三个检索器 |
| LLM 生成器 | `backend/rag/generator.py` | core/llm |
| 答案验证 | `backend/rag/validator.py` | jieba |

### 第 3 步：API 路由（1-2 天）

| 任务 | 文件 |
|------|------|
| /api/v1/ask (SSE) | `backend/api/ask.py` |
| /api/v1/symptoms | `backend/api/symptoms.py` |
| /api/v1/graph/* | `backend/api/graph.py` |
| 路由注册 | `backend/api/__init__.py` |

### 第 4 步：辅助功能（2-3 天）

| 任务 | 文件 |
|------|------|
| 反馈系统 | `backend/feedback/storage.py`, `optimizer/*` |
| 知识抽取 | `backend/tools/extractor.py`, `parser.py` |
| U盘同步 | `backend/tools/sync.py` |
| 历史管理 | `backend/api/history.py` |
| 用户系统 | `backend/api/auth.py`, `user.py` |
| 语音转写 | `backend/api/transcribe.py` |
| 报告导出 | `backend/tools/report.py` |

### 第 5 步：前端（3-4 天）

| 任务 | 文件 |
|------|------|
| 登录页面 | `LoginPage.vue` |
| 图谱主视图 | `GraphPanel.vue`, `GraphCanvas.vue` |
| 详情面板 | `DetailPanel.vue`, `NodeInfo.vue`, `RelationList.vue` |
| 问答面板 | `ChatPanel.vue`, `MessageBubble.vue`, `InputBox.vue` |
| 溯源卡片 | `TraceCard.vue`, `TraceabilityChain.vue` |
| 历史面板 | `HistoryPanel.vue` |
| 个人中心 | `ProfilePage.vue` |
| 管理页面 | `AdminPage.vue` |
| 反馈按钮 | `FeedbackButtons.vue` |
| 语音按钮 | `VoiceButton.vue` |
| 侧边栏 | `SideMenu.vue` |
| 搜索栏 | `TopBar.vue`, `SearchInput.vue` |

### 第 6 步：集成测试（2 天）

按 `docs/testing-plan.md` 执行单元/集成/验收测试。

### 第 7 步：打包（1 天）

按 `docs/packaging-guide.md` 生成 Setup.exe。

---

## 五、版本记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-25 | v1.0 | 初始开发规范与路线图 |

# A21 API 契约文档

> 版本: v1.0 | 前后端接口合同，双方严格按此文档开发

---

## 零、通用约定

### 基础信息
```
Base URL: http://localhost:8000
Content-Type: application/json（除文件上传外）
```

### 错误响应格式

所有错误返回统一格式，HTTP 状态码区分错误类型：

```json
{
  "error": "人类可读的错误描述",
  "code": 400
}
```

| HTTP 状态码 | 含义 |
|:--:|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 数据校验失败（Pydantic 自动返回） |
| 500 | 服务器内部错误 |
| 503 | 依赖服务不可用（Neo4j/llama-server 挂了） |

### 字段命名
- 全小写 + 下划线 (snake_case)
- 时间格式: ISO 8601 (`"2026-05-25T14:30:00"`)

---

## 一、系统健康

### GET /health

Electron 主进程轮询此接口，确认后端已就绪。

**请求**: 无

**响应**:
```json
{
  "status": "ok",
  "neo4j": "connected",
  "llama": "connected",
  "chroma": "connected",
  "uptime": 1234
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | "ok" 或 "degraded" |
| neo4j | string | "connected" / "disconnected" |
| llama | string | "connected" / "disconnected" |
| chroma | string | "connected" / "disconnected" |
| uptime | int | 后端运行秒数 |

---

## 二、问答核心

### POST /api/v1/ask

**核心问答接口。SSE 流式返回。**

**请求**:
```json
{
  "question": "接触器线圈烧毁怎么修？",
  "mode": "chat",
  "session_id": "sess_abc123",
  "context_nodes": ["S_CONT_02"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| question | string | ✅ | 用户问题 |
| mode | string | ❌ | "chat"(默认) 或 "keyword" |
| session_id | string | ❌ | 会话 ID，多轮对话时传入 |
| context_nodes | string[] | ❌ | 从图谱传入的上下文节点 UID |

**响应**: SSE 流 (Content-Type: text/event-stream)

```
event: token
data: {"token": "根据", "index": 0}

event: token
data: {"token": "资料", "index": 1}

event: token
data: {"token": "显示", "index": 2}

...

event: metadata
data: {"message_id": "msg_042", "citations": [...], "traceability": {...}}

event: done
data: {}
```

**token 事件** (每个生成 token):
```json
{
  "token": "根据",
  "index": 0
}
```

**metadata 事件** (生成完成后，一次性发送):
```json
{
  "message_id": "msg_042",
  "citations": [
    {
      "num": 1,
      "chunk_id": "doc_042",
      "doc_name": "船舶电气设备维护与修理",
      "page": "第四章第二节 P42",
      "graph_nodes": ["S_CONT_02", "C_VOLTAGE_LOW"]
    }
  ],
  "traceability": {
    "references_in_range": true,
    "keywords_matched": 5,
    "keywords_total": 5,
    "confidence": "green"
  },
  "answer_text": "根据资料显示，接触器线圈烧毁的可能原因如下：\n[1] 线圈内部短路...",
  "thinking_time_ms": 2050
}
```

**done 事件**: 流结束。

**错误时** (非流式，直接返回 JSON):
```json
{
  "error": "llama-server 未响应",
  "code": 503
}
```

---

### GET /api/v1/symptoms

**故障现象联想。输入框实时搜索。**

**请求**:
```
GET /api/v1/symptoms?keyword=接触器线&limit=5
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| keyword | string | ❌ | 搜索词，空时返回全部 |
| limit | int | ❌ | 返回条数，默认 10 |

**响应**:
```json
{
  "symptoms": [
    {"uid": "S_CONT_01", "name": "接触器线圈烧毁"},
    {"uid": "S_CONT_02", "name": "接触器线圈过热"},
    {"uid": "S_CONT_03", "name": "接触器线间短路"}
  ]
}
```

---

## 三、知识图谱

### GET /api/v1/graph/search

**图谱搜索（v2.0 关键词检索融入图谱）。返回匹配节点列表。**

**请求**:
```
GET /api/v1/graph/search?q=接触器 线圈&limit=10
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| q | string | ✅ | 搜索关键词（空格分隔） |
| limit | int | ❌ | 返回条数，默认 10 |

**响应**:
```json
{
  "query": "接触器 线圈",
  "results": [
    {
      "uid": "S_CONT_01",
      "name": "接触器线圈烧毁",
      "label": "Symptom",
      "score": 0.95,
      "source_doc": "船舶电气设备维护与修理",
      "source_page": "第四章第二节"
    },
    {
      "uid": "C_COIL_SHORT",
      "name": "线圈内部短路",
      "label": "Cause",
      "score": 0.78,
      "source_doc": "船舶电气设备维护与修理",
      "source_page": "第四章第二节"
    }
  ]
}
```

### GET /api/v1/graph/node/{uid}

**获取单个节点的完整信息。**

**请求**:
```
GET /api/v1/graph/node/S_CONT_01
```

**响应**:
```json
{
  "uid": "S_CONT_01",
  "name": "接触器线圈烧毁",
  "label": "Symptom",
  "properties": {
    "primary_features": ["线圈烧毁", "绝缘破坏"],
    "sensory_type": ["目视", "嗅觉"],
    "source_doc": "船舶电气设备维护与修理",
    "source_page": "第四章第二节 P42"
  },
  "relations": {
    "incoming": [
      {"type": "BELONGS_TO", "from_uid": "E_CONTACTOR", "from_name": "接触器"}
    ],
    "outgoing": [
      {"type": "CAUSED_BY", "to_uid": "C_VOLTAGE_LOW", "to_name": "电源电压过低", "priority": 1},
      {"type": "CAUSED_BY", "to_uid": "C_COIL_SHORT", "to_name": "线圈内部短路", "priority": 2}
    ]
  }
}
```

### GET /api/v1/graph/expand/{uid}

**展开节点的直接邻居（用于图谱交互）。**

**请求**:
```
GET /api/v1/graph/expand/S_CONT_01
```

**响应**:
```json
{
  "center": {"uid": "S_CONT_01", "name": "接触器线圈烧毁", "label": "Symptom"},
  "nodes": [
    {"uid": "E_CONTACTOR", "name": "接触器", "label": "Equipment"},
    {"uid": "C_VOLTAGE_LOW", "name": "电源电压过低", "label": "Cause"},
    {"uid": "ST_MEASURE_V", "name": "测量电源电压", "label": "Step"}
  ],
  "edges": [
    {"from": "E_CONTACTOR", "to": "S_CONT_01", "type": "BELONGS_TO"},
    {"from": "S_CONT_01", "to": "C_VOLTAGE_LOW", "type": "CAUSED_BY", "priority": 1},
    {"from": "C_VOLTAGE_LOW", "to": "ST_MEASURE_V", "type": "FIXED_BY"}
  ]
}
```

### GET /api/v1/graph/overview

**获取图谱全貌（所有 L2-L3 设备和顶级 Symptom 节点）。用于首次加载。**

**请求**: 无

**响应**:
```json
{
  "nodes": [
    {"uid": "E_MOTOR_CAT", "name": "船用电机", "label": "Equipment", "level": 2},
    {"uid": "E_APPLIANCE", "name": "船舶电器", "label": "Equipment", "level": 2},
    {"uid": "S_MOTOR_01", "name": "电动机不能起动", "label": "Symptom"}
  ],
  "edges": [
    {"from": "E_MOTOR_CAT", "to": "E_ASYNCH_MOTOR", "type": "SUBCLASS_OF"},
    {"from": "E_ASYNCH_MOTOR", "to": "S_MOTOR_01", "type": "BELONGS_TO"}
  ]
}
```

---

## 四、知识抽取

### POST /api/v1/parse

**上传文档，解析并抽取知识。**

**请求**: multipart/form-data

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| file | File | ✅ | Word(.docx) 或 PDF |

**响应**:
```json
{
  "parse_id": "parse_20260525_001",
  "file_name": "船舶辅机故障案例.docx",
  "extracted_text_length": 3420,
  "candidates": [
    {
      "uid": "CAND_001",
      "type": "Symptom",
      "name": "起货机无法提升重物",
      "source": "regex",
      "confidence": "high",
      "relations": [
        {"type": "CAUSED_BY", "target": "CAND_002"}
      ]
    },
    {
      "uid": "CAND_002",
      "type": "Cause",
      "name": "液压泵磨损",
      "source": "model",
      "confidence": "medium",
      "relations": []
    }
  ],
  "graph_preview": {
    "nodes": [...],
    "edges": [...]
  }
}
```

| 字段 | 说明 |
|------|------|
| source | "regex"(正则命中) 或 "model"(1.5B few-shot 推断) |
| confidence | "high"(正则) / "medium"(模型) / "low"(模型低置信) |
| graph_preview | 前端直接渲染为临时图谱预览 |

---

### POST /api/v1/confirm

**确认导入知识抽取结果。**

**请求**:
```json
{
  "parse_id": "parse_20260525_001",
  "confirmed": ["CAND_001", "CAND_003"],
  "rejected": ["CAND_002"],
  "edits": [
    {"uid": "CAND_001", "name": "起货机无法提升重物（已修正）"}
  ]
}
```

**响应**:
```json
{
  "status": "ok",
  "imported": {
    "entities": 5,
    "relationships": 3
  },
  "chroma_chunks_added": 12
}
```

---

## 五、反馈与优化

### POST /api/v1/feedback

**提交点赞/点踩。**

**请求**:
```json
{
  "message_id": "msg_042",
  "rating": 1,
  "comment": "回答很准确"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| message_id | string | ✅ | 从 /ask 的 metadata 事件获取 |
| rating | int | ✅ | 1(👍) / -1(👎) / 0(取消) |
| comment | string | ❌ | 可选文字评价 |

**响应**:
```json
{
  "status": "ok",
  "total_feedbacks": 37
}
```

---

### POST /api/v1/optimize

**手动触发参数优化。**

**请求**: 无（或 `{}`）

**响应**:
```json
{
  "status": "started",
  "feedbacks_used": 35,
  "search_space": {
    "alpha_range": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
    "gamma_range": [0.1, 0.2, 0.3, 0.4, 0.5],
    "top_k_range": [3, 5, 7]
  },
  "total_combinations": 105,
  "estimated_time_seconds": 30
}
```

**优化完成后** (前端轮询此接口或通过回调):
```json
{
  "status": "completed",
  "best_params": {
    "alpha": 0.3,
    "beta": 0.5,
    "gamma": 0.2,
    "top_k": 5,
    "rerank_keep": 5
  },
  "best_score": 0.82,
  "previous_score": 0.74,
  "improvement": 0.08
}
```

---

## 六、数据同步

### GET /api/v1/export

**导出知识包（zip 下载）。**

**请求**: 无

**响应**: 二进制流 (Content-Type: application/zip)

```
A21_sync_20260525.zip
├── neo4j_dump.cypher
├── chroma_db/
├── feedbacks.db
├── params.json
└── sync_info.json
```

---

### POST /api/v1/import

**导入知识包。**

**请求**: multipart/form-data

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| file | File | ✅ | .zip 知识包 |

**响应**:
```json
{
  "status": "ok",
  "sync_info": {
    "export_time": "2026-05-20T10:00:00",
    "source_device": "ENGINE-ROOM-PC-01",
    "embedding_model": "bge-base-zh-v1.5"
  },
  "imported": {
    "neo4j_entities_added": 12,
    "neo4j_entities_skipped": 508,
    "chroma_chunks_added": 15,
    "feedbacks_added": 5
  },
  "conflicts": [],
  "model_mismatch": false
}
```

---

## 七、历史对话

### GET /api/v1/history

**获取历史对话列表。**

**请求**:
```
GET /api/v1/history?page=1&page_size=20
```

**响应**:
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "sessions": [
    {
      "session_id": "sess_abc123",
      "title": "接触器线圈烧毁相关问答",
      "message_count": 4,
      "created_at": "2026-05-25T14:30:00",
      "updated_at": "2026-05-25T14:35:00"
    }
  ]
}
```

### GET /api/v1/history/{session_id}

**获取某次对话的完整记录。**

**响应**:
```json
{
  "session_id": "sess_abc123",
  "messages": [
    {
      "message_id": "msg_041",
      "role": "user",
      "content": "接触器线圈烧毁怎么修？",
      "timestamp": "2026-05-25T14:30:00"
    },
    {
      "message_id": "msg_042",
      "role": "assistant",
      "content": "根据资料显示...",
      "citations": [...],
      "traceability": {...},
      "timestamp": "2026-05-25T14:30:05"
    }
  ]
}
```

---

## 八、工具接口

### POST /api/v1/transcribe

**语音转文字。**

**请求**: multipart/form-data

| 字段 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| audio | File | ✅ | WAV 音频 (16kHz, mono) |

**响应**:
```json
{
  "text": "接触器线圈烧毁怎么修",
  "duration_ms": 3200,
  "processing_ms": 450
}
```

---

### GET /api/v1/report

**导出问答报告（Word）。**

**请求**:
```
GET /api/v1/report?session_id=sess_abc123
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:--:|------|
| session_id | string | ❌ | 不传则导出最近一次对话 |

**响应**: 二进制流 (Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document)

---

## 九、接口汇总

| # | 方法 | 路径 | 说明 | 响应类型 |
|---|------|------|------|----------|
| 1 | GET | /health | 健康检查 | JSON |
| 2 | POST | /api/v1/ask | 核心问答 | SSE 流 |
| 3 | GET | /api/v1/symptoms | 故障联想 | JSON |
| 4 | GET | /api/v1/graph/search | 图谱搜索 | JSON |
| 5 | GET | /api/v1/graph/node/{uid} | 节点详情 | JSON |
| 6 | GET | /api/v1/graph/expand/{uid} | 展开邻居 | JSON |
| 7 | GET | /api/v1/graph/overview | 图谱全貌 | JSON |
| 8 | POST | /api/v1/parse | 上传文档抽取 | JSON |
| 9 | POST | /api/v1/confirm | 确认入库 | JSON |
| 10 | POST | /api/v1/feedback | 提交反馈 | JSON |
| 11 | POST | /api/v1/optimize | 触发优化 | JSON |
| 12 | GET | /api/v1/export | 导出知识包 | ZIP 流 |
| 13 | POST | /api/v1/import | 导入知识包 | JSON |
| 14 | GET | /api/v1/history | 历史列表 | JSON |
| 15 | GET | /api/v1/history/{sid} | 对话详情 | JSON |
| 16 | POST | /api/v1/transcribe | 语音转文字 | JSON |
| 17 | GET | /api/v1/report | 导出报告 | DOCX 流 |

---

## 十、版本记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-25 | v1.0 | 初始 API 契约，17 个接口完整定义 |

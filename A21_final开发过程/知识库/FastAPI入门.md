# FastAPI 入门

## 一句话解释

FastAPI = 用 Python **写接口**的框架。前端说"给我数据"，后端就把数据返回给它。

## 类比

想象你在餐厅：

| 餐厅 | Web 应用 |
|------|----------|
| 顾客看菜单点菜 | 前端发 HTTP 请求 |
| 服务员接单、传菜 | **FastAPI** ← 就是这个 |
| 厨师做菜 | 你的 RAG/Neo4j/LLM 代码 |
| 上菜 | 后端返回 JSON 数据 |

FastAPI 就是"服务员"——接收请求、找到对应的处理函数、把结果返回给前端。

## 最小例子（5 行代码跑起来）

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")                    # 访问 http://localhost:8000/
def hello():
    return {"message": "你好"}    # 返回 {"message": "你好"}
```

保存为 `main.py`，运行：
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

浏览器打开 `http://localhost:8000/`，看到 `{"message":"你好"}`。

浏览器打开 `http://localhost:8000/docs`，看到自动生成的 API 文档页面。

---

## 核心概念

### 1. 路由（Route）—— URL 和处理函数的对应关系

```python
@app.get("/api/v1/symptoms")     # GET 请求 → 这个 URL
def get_symptoms():
    return ["发动机无法启动", "液压泵漏油", "电气系统短路"]

@app.post("/api/v1/ask")         # POST 请求 → 这个 URL
def ask_question():
    return {"answer": "请检查燃油系统和蓄电池"}
```

| 概念 | 解释 | 类比 |
|------|------|------|
| `@app.get(...)` | 处理 GET 请求（读取数据） | 顾客说"给我看菜单" |
| `@app.post(...)` | 处理 POST 请求（提交数据） | 顾客说"我要点这个菜" |
| URL 路径 | 访问地址 | 桌号：3 号桌 |

### 2. 路径参数（Path Parameter）—— URL 里带数据

```python
@app.get("/api/v1/history/{session_id}")
def get_history(session_id: str):
    # 访问 /api/v1/history/abc123 时
    # session_id = "abc123"
    return {"session": session_id, "messages": [...]}
```

### 3. 查询参数（Query Parameter）—— URL 问号后面带数据

```python
@app.get("/api/v1/symptoms")
def search_symptoms(keyword: str = ""):
    # 访问 /api/v1/symptoms?keyword=发动机
    # keyword = "发动机"
    return [s for s in all_symptoms if keyword in s]
```

### 4. 请求体（Request Body）—— POST 请求带的数据

```python
from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str
    history: list[dict] = []      # 可选，默认空列表

@app.post("/api/v1/ask")
def ask(req: AskRequest):
    # req.question → "发动机打不着火怎么办"
    # req.history  → [{"role": "user", "content": "..."}]
    return {"answer": process(req.question)}
```

前端发送 POST 请求时，请求体是 JSON：
```json
{
  "question": "发动机打不着火怎么办",
  "history": []
}
```

FastAPI 自动把 JSON 转成 `AskRequest` 对象。如果格式不对（比如 `question` 没传），自动返回 422 错误。

---

## 我们项目的 API 路由

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="A21 船舶故障诊断系统")

# 允许前端跨域访问（开发时需要，Electron 打包后不需要）
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

@app.get("/health")
def health():
    """Electron 主进程轮询此接口，判断后端是否就绪"""
    return {"status": "ok"}

@app.get("/api/v1/symptoms")
async def symptoms(keyword: str = ""):
    """故障现象联想：输入框自动补全"""
    # 从 Neo4j 查所有故障现象，按 keyword 过滤
    pass

@app.post("/api/v1/ask")
async def ask(req: AskRequest):
    """核心问答接口：流式返回"""
    # 1. 检索（图文+向量+BM25）
    # 2. 构建 Prompt
    # 3. 调用 llama-server 流式生成
    # 4. 流式返回 SSE
    pass

@app.post("/api/v1/parse")
async def parse_document(file: UploadFile):
    """上传文档 → 解析 → 知识抽取 → 返回候选实体列表"""
    pass

@app.post("/api/v1/confirm")
async def confirm_import(entities: list[Entity]):
    """确认导入抽取结果到 Neo4j + Chroma"""
    pass

@app.post("/api/v1/feedback")
async def submit_feedback(fb: Feedback):
    """提交点赞/点踩"""
    pass

@app.get("/api/v1/history/{session_id}")
async def get_history(session_id: str):
    """获取历史对话"""
    pass

@app.get("/api/v1/export")
async def export_data():
    """导出知识包（zip）"""
    pass

@app.post("/api/v1/import")
async def import_data(file: UploadFile):
    """导入知识包"""
    pass
```

---

## 流式输出（SSE）—— 我们最依赖的功能

```python
from fastapi.responses import StreamingResponse
import asyncio

@app.post("/api/v1/ask")
async def ask(req: AskRequest):
    async def generate():
        # 每产出一个 token，立刻推送给前端
        for token in call_llm_stream(req.question):
            yield f"data: {token}\n\n"    # SSE 格式
            await asyncio.sleep(0)         # 让出控制权，不阻塞
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # 禁用 nginx 缓冲
        }
    )
```

前端 JavaScript 接收：
```javascript
const response = await fetch('/api/v1/ask', { method: 'POST', body: ... })
const reader = response.body.getReader()
while (true) {
    const { done, value } = await reader.read()
    if (done) break
    // value 就是新产生的 token，追加到聊天气泡里
    appendToChat(decoder.decode(value))
}
```

---

## 怎么跑起来

```bash
# 安装
pip install fastapi uvicorn

# 启动（开发模式，代码改动自动重启）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（不自动重启）
uvicorn main:app --host 127.0.0.1 --port 8000
```

---

## 和 Flask 的区别（为什么选 FastAPI）

| | FastAPI | Flask |
|------|---------|-------|
| `async/await` | ✅ 原生支持 | ❌ 需要额外插件 |
| 流式输出 | `StreamingResponse`，一行代码 | 需要折腾 |
| 数据校验 | Pydantic 自动，不写校验代码 | 手写 `if not isinstance(...)` |
| API 文档 | `/docs` 自动生成 | 需要额外装 Flask-RESTX |
| 性能 | 快（异步 ASGI） | 慢（同步 WSGI） |
| 学习难度 | 低 | 低 |

---

## 相关概念（需要先了解）

- [[REST API与HTTP基础]] — GET/POST 是什么、URL 是什么、JSON 是什么

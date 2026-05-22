# REST API 与 HTTP 基础

## 一句话解释

REST API = 前端和后端**约定好的一种说话方式**。前端说"我要什么"，后端给"你要的东西"。

## 这是什么

你在浏览器输入 `https://www.baidu.com` 然后回车——这一瞬间发生了什么？

```
你的浏览器                          百度的服务器
    │                                    │
    │  ──── GET / HTTP/1.1 ────→        │   ← 浏览器说：给我首页
    │                                    │
    │  ←──── 200 OK + HTML ────         │   ← 服务器说：好的，这是首页
    │                                    │
    │  浏览器渲染 HTML，显示百度首页        │
```

这就是一次 HTTP 请求（Request）和 响应（Response）。

前端（浏览器 / Electron / Vue）通过 HTTP 和后端（FastAPI）通信。

---

## HTTP 方法（动词）

| 方法 | 意思 | 类比 | 什么时候用 |
|------|------|------|-----------|
| **GET** | 读取数据 | 说"给我看看菜单" | 查故障列表、查历史对话 |
| **POST** | 创建/提交数据 | 说"我要点这个菜" | 提问、上传文档、提交反馈 |
| PUT | 替换数据 | 说"把这道菜换成那个" | 修改配置、更新参数 |
| DELETE | 删除数据 | 说"退掉这道菜" | 删除对话记录 |

我们项目主要用 GET 和 POST。

---

## URL 是什么

URL = 统一资源定位符 = "互联网上的地址"。

```
http://localhost:8000/api/v1/symptoms?keyword=发动机
│      │               │    │   │        │
│      │               │    │   │        └── 查询参数：搜"发动机"
│      │               │    │   └── 路径：故障现象接口
│      │               │    └── 版本号
│      │               └── 主机：本机的 8000 端口
│      └── 协议：HTTP
└── 省略号前面的东西
```

---

## JSON 是什么

JSON = 前端和后端**交换数据的格式**。人类可读，机器好解析。

```json
{
  "question": "发动机打不着火怎么办",
  "history": [
    {"role": "user", "content": "我的船发动机出问题了"},
    {"role": "assistant", "content": "请描述具体现象"}
  ]
}
```

| JSON | Python |
|------|--------|
| `{"key": "value"}` | `{"key": "value"}`（字典） |
| `[1, 2, 3]` | `[1, 2, 3]`（列表） |
| `"hello"` | `"hello"`（字符串） |
| `123` | `123`（整数） |
| `true` / `false` | `True` / `False` |

---

## 状态码

后端返回的数据前面带一个数字，表示"结果怎么样"：

| 状态码 | 意思 | 例子 |
|--------|------|------|
| **200** | 成功 | 查询成功，返回数据 |
| **201** | 创建成功 | 新建了一条记录 |
| **400** | 请求有误 | 前端传的 JSON 格式不对 |
| **404** | 找不到 | 访问了不存在的 URL |
| **422** | 数据校验失败 | 少传了必填字段（FastAPI 自动返回） |
| **500** | 服务器内部错误 | Python 代码报错了 |

---

## 一次完整的问答流程

```
1. 用户在输入框敲"发动机打不着火"，点发送
        │
2. Vue 前端发送 HTTP 请求：
   POST http://localhost:8000/api/v1/ask
   Body: {"question": "发动机打不着火", "history": []}
        │
3. FastAPI 收到请求 → 路由匹配 @app.post("/api/v1/ask")
   → 调用 ask() 函数
        │
4. ask() 内部：
   ├── 调 Neo4j 查知识图谱
   ├── 调 Chroma 做向量检索
   ├── 调 BM25 做关键词检索
   ├── 融合排序 → 构建 Prompt
   └── 调 llama-server，流式生成
        │
5. FastAPI 流式返回 SSE：
   data: 根据
   data: 资料
   data: 显示
   data: ，
   data: 发动机
   ...
        │
6. Vue 前端逐 token 渲染到聊天气泡
   "根" → "根据" → "根据资" → "根据资料" → ...
```

---

## 前端怎么发请求（两种方式）

### fetch（浏览器原生，我们用它做流式）
```javascript
const response = await fetch('http://localhost:8000/api/v1/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: '发动机打不着火', history: [] })
})
const data = await response.json()  // 非流式
```

### axios（需要 npm install axios，代码更简洁）
```javascript
import axios from 'axios'
const response = await axios.post('http://localhost:8000/api/v1/feedback', {
  message_id: 'msg123',
  rating: 1
})
```

---

## 开发时为什么用 localhost:8000？

`localhost` = "本机"，`8000` = 端口号。

Python FastAPI 跑在 `localhost:8000`，Vue Vite 开发服务器跑在 `localhost:5173`。两个是不同的端口，各自独立——所以前端通过 `http://localhost:8000` 访问后端。

Electron 打包成 exe 后，`localhost:8000` 依然有效——因为 Python 后端就在用户本机上跑。

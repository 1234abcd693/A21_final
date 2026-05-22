# Electron + Python 后端通信架构

## 一句话解释

Electron 窗口（Vue 前端）通过 **HTTP** 和 Python 后端通信，和普通网页完全一样。Python 后端由 Electron 自动启动和关闭。

## 完整启动流程

```
用户双击 A21.exe
    │
    ▼
Electron main.js 启动
    │
    ├── 1. 检查并启动 Neo4j（如果未运行）
    │       neo4j.bat start
    │
    ├── 2. 启动 llama-server
    │       llama-server -m qwen2.5-1.5b-q4_k_m.gguf -c 2048 -t 4
    │       监听 localhost:8080
    │
    ├── 3. 启动 Python FastAPI 后端
    │       python backend/main.py
    │       监听 localhost:8000
    │
    ├── 4. 轮询等待所有服务就绪
    │       GET http://localhost:8000/health → 200 OK
    │       GET http://localhost:8080/health → 200 OK
    │
    ├── 5. 创建窗口，加载 Vue 前端
    │       开发: http://localhost:5173（Vite dev server）
    │       生产: file://dist/index.html
    │
    └── 窗口关闭时:
          ├── 关闭 Python 后端
          ├── 关闭 llama-server
          └── 关闭 Neo4j
```

## 通信方式

### Vue ← HTTP → Python（主要通信）

```javascript
// Vue 前端代码
import axios from 'axios'

const API = 'http://localhost:8000/api/v1'

// 发送问题，流式接收回答
async function ask(question) {
  const response = await fetch(`${API}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history: [] })
  })

  // SSE 流式读取，每收到一个 token 就更新界面
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const text = decoder.decode(value)
    // 追加到消息气泡
  }
}

// 发送反馈
async function feedback(msgId, rating) {
  await axios.post(`${API}/feedback`, { message_id: msgId, rating })
}
```

### Vue ← IPC → Electron 主进程（辅助通信）

只在需要**系统级操作**时用：

```javascript
// Vue 调用主进程打开文件对话框
const result = await window.electronAPI.openFileDialog()
// 主进程代劳打开系统文件选择器，返回路径

// Vue 调用主进程导出数据
await window.electronAPI.exportData()
// 主进程代劳打包 zip 并弹出保存对话框
```

## 为什么不让 Electron 直接导入 Python？

Electron 是 Node.js 环境，不能直接 `import` Python 模块。两种方案：

| 方案 | 做法 | 评价 |
|------|------|------|
| **独立进程** | Python 作为独立子进程跑 FastAPI | ✅ 我们选这个，清晰、好调试 |
| python-shell | Node.js 里调 Python 脚本 | 适合简单脚本，不适合复杂 API |

## 打包成 exe 时怎么处理 Python？

最终交付的 exe 需要包含三个东西：

```
A21_final.exe（Electron 打包的桌面应用）
    │
    └── resources/
        ├── backend.exe        ← PyInstaller 打包的 Python 后端
        ├── llama-server.exe   ← llama.cpp 的 server 可执行文件
        ├── model.gguf         ← 模型文件
        ├── neo4j/             ← Neo4j 绿色版
        ├── chroma_db/         ← 初始向量库
        └── start-services.bat ← 备用：手动启动脚本
```

打包工具：
- 前端：`electron-builder` → 打包成 Electron exe
- 后端：`PyInstaller` → 打包成 backend.exe
- 最终：`electron-builder` 把 backend.exe、llama-server、模型文件等放到 resources 目录

## 开发时的目录结构

```
A21_final/
├── frontend/              ← Vue 3 + Vite + Electron
│   ├── src/               ← Vue 组件
│   ├── electron/          ← Electron 主进程代码
│   │   ├── main.js        ← 启动逻辑
│   │   └── preload.js     ← IPC 桥接
│   └── package.json
│
├── backend/               ← Python FastAPI
│   ├── main.py            ← 入口
│   ├── api/               ← 路由
│   ├── rag/               ← 检索+生成
│   ├── kg/                ← 知识图谱操作
│   ├── tools/             ← 抽取、同步等
│   └── requirements.txt   ← Python 依赖
│
└── A21_final开发过程/      ← Obsidian 文档仓库
```

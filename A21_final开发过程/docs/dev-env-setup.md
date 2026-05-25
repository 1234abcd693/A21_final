# A21 开发环境搭建指南（Windows + Miniconda）

> 版本: v1.0 | 最后更新: 2026-05-22

---

## 一、环境总览

```
┌─────────────────────────────────────────────────┐
│ Miniconda    → Python 3.10 虚拟环境               │
│   fastapi, uvicorn, langchain, chromadb          │
│   neo4j, jieba, sentence-transformers            │
│   python-docx, pdfplumber, rank-bm25             │
├─────────────────────────────────────────────────┤
│ Neo4j        → 图数据库（绿色版，无需安装）         │
│   bolt://localhost:7687                          │
├─────────────────────────────────────────────────┤
│ llama.cpp    → LLM 推理引擎（预编译 exe）           │
│   llama-server.exe → localhost:8080              │
├─────────────────────────────────────────────────┤
│ Node.js      → 前端构建（全局安装）                 │
│   npm → Vue 3 / Vite / Electron                 │
├─────────────────────────────────────────────────┤
│ 项目根        → A21_final/                        │
│   backend/    → Python 代码                       │
│   frontend/   → Vue 代码                          │
│   model/      → .gguf 模型文件                     │
│   data/       → chroma_db/ + feedbacks.db         │
│   neo4j/      → Neo4j 绿色版（gitignored）         │
└─────────────────────────────────────────────────┘
```

---

## 二、Miniconda + Python 环境

### 2.1 检查是否已安装

```powershell
conda --version
# 如果没有，去 https://docs.anaconda.com/miniconda/ 下载 Windows 64-bit 安装包
# 安装时勾选 "Add Miniconda3 to my PATH environment variable"
```

### 2.2 创建项目环境

```powershell
# 创建 Python 3.10 虚拟环境
conda create -n a21 python=3.10 -y

# 激活
conda activate a21

# 验证
python --version
# → Python 3.10.x
```

### 2.3 安装 Python 依赖

在 `A21_final/` 根目录创建 `backend/requirements.txt`：

```txt
# Web 框架
fastapi==0.115.0
uvicorn[standard]==0.30.0

# RAG 核心
langchain==0.3.0
langchain-community==0.3.0
chromadb==0.5.0

# 知识图谱
neo4j==5.25.0

# NLP
jieba==0.42.1
sentence-transformers==3.1.0   # embedding: bge-base-zh-v1.5

# 检索
rank-bm25==0.2.2

# 文档解析
python-docx==1.1.0
pdfplumber==0.11.0

# 工具
python-multipart==0.0.9
httpx==0.27.0
```

```powershell
# 安装
cd A21_final
pip install -r backend/requirements.txt

# 验证
python -c "import fastapi, chromadb, neo4j, jieba; print('OK')"
# → OK
```

---

## 三、Neo4j 图数据库

### 3.1 下载绿色版（无需安装程序）

```
1. 打开 https://neo4j.com/download-center/#community
2. 选择 Windows ZIP 版本（不是 exe 安装包）
3. 解压到 A21_final/neo4j/ 目录
```

目录结构：
```
A21_final/neo4j/
├── bin/
│   ├── neo4j.bat          ← 启动/停止
│   └── cypher-shell.bat   ← 命令行客户端
├── data/
│   └── databases/
│       └── neo4j/          ← 数据库文件
├── conf/
│   └── neo4j.conf          ← 配置文件
└── plugins/
    └── apoc.jar            ← APOC 插件（导出需要）
```

### 3.2 安装 APOC 插件（U盘同步需要）

```
1. 下载 apoc-5.x.x-core.jar
   https://github.com/neo4j/apoc/releases
2. 放到 A21_final/neo4j/plugins/
3. 编辑 A21_final/neo4j/conf/neo4j.conf，末尾加一行：
   dbms.security.procedures.unrestricted=apoc.*
```

### 3.3 配置 Neo4j

编辑 `neo4j/conf/neo4j.conf`，确认这几行：

```ini
# 允许外部连接（本地开发用）
server.default_listen_address=0.0.0.0

# 关闭 HTTPS（本地不需要）
# server.bolt.listen_address=:7687
# server.http.listen_address=:7474

# 初始密码（首次启动后改成自己的）
dbms.security.auth_enabled=true
```

### 3.4 启动和初始化

```powershell
# 首次启动
cd neo4j/bin
.\neo4j.bat console    # 前台启动，方便看日志

# 浏览器打开 http://localhost:7474
# 首次登录: 用户名 neo4j，密码 neo4j
# 系统会要求改密码 → 设为 a21password（或自定义）

# 导入知识图谱初始数据
cd A21_final
.\neo4j\bin\cypher-shell.bat -u neo4j -p a21password -f import.cypher

# 验证
.\neo4j\bin\cypher-shell.bat -u neo4j -p a21password
# MATCH (n) RETURN labels(n), count(n) LIMIT 5;
# → 应该看到 7 类节点的统计
```

### 3.5 后台启动（开发时用）

```powershell
cd neo4j/bin
.\neo4j.bat start    # 启动服务
.\neo4j.bat status   # 检查状态
.\neo4j.bat stop     # 停止服务
```

### 3.6 常用 Cypher Shell 命令

```bash
# 查询故障现象列表
MATCH (s:Symptom) RETURN s.name LIMIT 10;

# 查询某个故障的原因（按优先级）
MATCH (s:Symptom {name: '接触器线圈烧毁'})-[r:CAUSED_BY]->(c:Cause)
RETURN r.priority, c.name ORDER BY r.priority;

# 导出全库（U盘同步用）
CALL apoc.export.cypher.all('neo4j_dump.cypher', {format: 'cypher-shell'});

# 退出
:exit
```

---

## 四、llama.cpp + 模型

### 4.1 下载 llama.cpp 预编译包

```
1. 打开 https://github.com/ggml-org/llama.cpp/releases
2. 下载最新的 bin-win-avx2-x64.zip
3. 解压到 A21_final/llama.cpp/
```

验证：
```powershell
cd llama.cpp
.\llama-cli.exe --version
```

### 4.2 下载模型文件

模型：**Qwen2.5-1.5B-Instruct Q4_K_M GGUF**

```
1. 打开 https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
2. 下载 qwen2.5-1.5b-instruct-q4_k_m.gguf（~1.0 GB）
3. 放到 A21_final/model/
```

### 4.3 测试模型

```powershell
cd A21_final/llama.cpp

.\llama-cli.exe `
  -m ..\model\qwen2.5-1.5b-instruct-q4_k_m.gguf `
  -p "你好，请简单介绍你自己" `
  -n 100 `
  -t 4
```

### 4.4 启动 llama-server（后端调用）

```powershell
.\llama-server.exe `
  -m ..\model\qwen2.5-1.5b-instruct-q4_k_m.gguf `
  -c 2048 `
  -t 4 `
  --host 127.0.0.1 `
  --port 8080 `
  --mlock
```

验证：
```powershell
curl http://localhost:8080/health
# → {"status": "ok"}
```

---

## 五、Node.js + 前端

### 5.1 检查/安装 Node.js

```powershell
node --version
# 如果没有，去 https://nodejs.org/ 下载 LTS 版本（18.x 或 20.x）
# 安装时勾选 "Automatically install the necessary tools"
```

### 5.2 创建前端项目（待代码阶段）

```powershell
cd A21_final
npm create vite@latest frontend -- --template vue
cd frontend
npm install
npm install axios element-plus d3
```

---

## 六、项目目录结构（最终）

```
A21_final/
├── backend/                     ← Python FastAPI
│   ├── main.py                  ← 入口
│   ├── requirements.txt         ← Python 依赖
│   ├── api/                     ← 路由
│   ├── rag/                     ← 检索+生成+验证
│   ├── feedback/                ← 反馈+调优
│   ├── kg/                      ← Neo4j 操作
│   ├── tools/                   ← 抽取/同步
│   └── core/                    ← 配置/LLM封装
├── frontend/                    ← Vue 3 + Vite + Electron
│   ├── src/components/
│   └── package.json
├── neo4j/                       ← Neo4j 绿色版 (gitignored)
├── llama.cpp/                   ← llama.cpp 预编译 (gitignored)
├── model/                       ← .gguf 模型文件 (gitignored)
│   └── qwen2.5-1.5b-instruct-q4_k_m.gguf
├── data/                        ← 本地数据
│   ├── chroma_db/               ← 向量库 (gitignored)
│   └── feedbacks.db             ← 反馈数据库 (gitignored)
├── import.cypher                ← KG 初始数据
├── 知识图谱设计文档.md
├── 赛题.txt
├── .gitignore
├── start_all.bat                ← 一键启动脚本
└── A21_final开发过程/            ← Obsidian 文档仓库
```

---

## 七、一键启动脚本

创建 `A21_final/start_all.bat`：

```batch
@echo off
echo ========================================
echo A21 船舶故障诊断系统 - 开发环境启动
echo ========================================
echo.

REM 激活 conda 环境
call conda activate a21

REM 启动 Neo4j
echo [1/3] 启动 Neo4j...
start "Neo4j" cmd /c "cd neo4j\bin && neo4j.bat console"

REM 启动 llama-server
echo [2/3] 启动 llama-server...
start "llama-server" cmd /c "cd llama.cpp && llama-server.exe -m ..\model\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 2048 -t 4 --host 127.0.0.1 --port 8080 --mlock"

REM 等待服务就绪
echo [*] 等待服务就绪（10秒）...
timeout /t 10 /nobreak >nul

REM 启动 FastAPI 后端
echo [3/3] 启动 FastAPI 后端...
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

echo.
echo 所有服务已启动！
echo   后端 API:   http://localhost:8000/docs
echo   图谱管理:   http://localhost:7474
echo   LLM 服务:   http://localhost:8080
pause
```

---

## 八、验证清单

开发环境搭建完成后，逐项验证：

```powershell
# ✅ 1. Python 环境
conda activate a21
python -c "import fastapi, chromadb, neo4j, jieba; print('Python OK')"

# ✅ 2. Neo4j
cd neo4j\bin
.\neo4j.bat status
# → Neo4j is running

# ✅ 3. KG 数据
.\cypher-shell.bat -u neo4j -p a21password "MATCH (n) RETURN count(n);"
# → > 150（实体数）

# ✅ 4. llama-server
curl http://localhost:8080/health
# → {"status": "ok"}

# ✅ 5. FastAPI 后端（启动后）
curl http://localhost:8000/health
# → {"status": "ok"}

# ✅ 6. Node.js
node --version
npm --version
```

---

## 九、.gitignore 补充

确认 `A21_final/.gitignore` 包含以下内容：

```gitignore
# Neo4j 运行目录
neo4j/

# llama.cpp 可执行文件
llama.cpp/

# 模型文件（太大）
model/
*.gguf

# 本地数据
data/
chroma_db/

# Python 虚拟环境
__pycache__/
*.pyc

# Node.js
node_modules/
dist/

# 环境变量
.env
```

---

## 十、后续待补充

- [ ] `backend/` 实际代码结构
- [ ] `frontend/` 创建 + Electron 集成
- [ ] `.env` 环境变量模板（Neo4j 密码、端口）
- [ ] 打包脚本（PyInstaller + electron-builder）

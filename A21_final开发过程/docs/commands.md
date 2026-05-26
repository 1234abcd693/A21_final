# A21 项目常用命令速查

> 最后更新: 2026-05-26 | feat/main 分支

---

## 环境安装

```powershell
# 创建 conda 环境
conda create -n a21 python=3.10 -y
conda activate a21

# 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

## 启动服务

### 一键启动所有服务
```powershell
.\start_all.bat
```

### 手动逐个启动（调试时用）
```powershell
# 终端1: Neo4j
cd neo4j\neo4j-community-2026.02.3\bin
.\neo4j.bat console

# 终端2: llama-server (端口 8082)
cd llama.cpp
.\llama-server.exe -m ..\model\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 2048 -t 4 --host 127.0.0.1 --port 8082 --mlock

# 终端3: Vosk 语音识别 (端口 8765)
cd backend
python tools\vosk_http.py

# 终端4: FastAPI 后端 (端口 8000)
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 终端5: 前端 (端口 5173)
cd frontend
npm run dev
```

## 数据库操作

```powershell
# Neo4j 导入知识图谱数据
cd neo4j\neo4j-community-2026.02.3\bin
.\cypher-shell.bat -u neo4j -p a21password -f ..\..\..\import.cypher

# Neo4j 查询验证
.\cypher-shell.bat -u neo4j -p a21password
MATCH (n) RETURN labels(n)[0] AS Label, count(n) AS Count;

# 清除并重新导入
MATCH (n) DETACH DELETE n;
# 然后重新执行 import.cypher
```

## 开发工具

```powershell
# 前端开发 (网页预览)
cd frontend && npm run dev

# Electron 桌面预览 (需要先启动后端)
cd frontend
npm run dev:vue    # 终端1
npm run dev:electron  # 终端2

# 后端测试
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Vite 构建检查
cd frontend && npx vite build
```

## Git 分支

```powershell
# 当前分支
git branch --show-current

# 新建功能分支 (从 feat/main 分出)
git checkout feat/main
git checkout -b feat/xxx

# 提交
git add -A
git commit -m "模块: 简述"

# 推送 (需要网络)
git push origin feat/main
```

## 下载清单

| 文件 | 大小 | 链接 |
|------|:--:|------|
| llama.cpp | ~50MB | https://github.com/ggml-org/llama.cpp/releases → bin-win-avx2-x64.zip |
| Qwen2.5-1.5B 模型 | ~1GB | https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF → q4_k_m.gguf |
| Vosk 中文模型 | 42MB | https://alphacephei.com/vosk/models → vosk-model-small-cn-0.22.zip |
| APOC 插件 | ~20MB | https://github.com/neo4j/apoc/releases/tag/2026.02.3 → apoc-core.jar |

## 端口速查

| 端口 | 服务 |
|:--:|------|
| 7474 | Neo4j Web |
| 7687 | Neo4j Bolt |
| 8000 | FastAPI 后端 |
| 8082 | llama-server |
| 8765 | Vosk 语音 |
| 5173 | 前端 Vite |

## 清理

```powershell
# 清理旧进程
taskkill /f /im neo4j* 2>$null
taskkill /f /im llama-server* 2>$null
taskkill /f /im python* 2>$null

# 清理 Neo4j 数据 (完全重置)
rmdir /s /q neo4j\neo4j-community-2026.02.3\data\databases\neo4j
# 然后重新 .\neo4j.bat console 并导入 import.cypher

# 清理前端构建缓存
rmdir /s /q frontend\node_modules\.vite
rmdir /s /q frontend\dist
```

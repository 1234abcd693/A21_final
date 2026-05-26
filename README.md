# A21 船舶装备故障诊断智能问答系统

> **中国大学生服务外包创新创业大赛 A21 赛题 | 大连海事大学命题**  
> RAG（检索增强生成）+ 知识图谱 + 本地小模型 → 离线船舶故障诊断

---

## 项目简介

面向船舶关键装备（发动机、液压系统、电气设备等）的**离线智能故障诊断系统**。一线船员输入故障现象，系统基于知识图谱和向量检索找到相关维修知识，由本地大模型生成结构化维修建议——全程无需联网。

**核心能力**：知识图谱可视化 · 向量+图谱双路检索 · SSE 流式回答 · Markdown 报告级排版 · 答案溯源防幻觉 · 反馈自动调优 · 语音输入 · U盘跨设备同步

---

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│  前端交互层 (Vue 3 + Vite + Electron 桌面壳)          │
│    聊天界面(SSE流式+Markdown) / 图谱可视化(AntV G6)   │
│    反馈按钮(👍👎) / 复制按钮 / 历史对话 / 用户系统      │
├─────────────────────────────────────────────────────┤
│  服务层 (FastAPI + uvicorn)                         │
│    8 个路由模块 / SSE 流式推送 / JSON 编码传输          │
├─────────────┬──────────────┬────────────────────────┤
│  RAG 层      │  反馈层        │  数据层                │
│  向量检索    │  点赞/点踩     │  知识图谱 (Neo4j)      │
│  图检索      │  网格搜索优化   │  向量库 (ChromaDB)     │
│  答案后处理  │  参数持久化    │  对话历史 (SQLite)     │
│  LLM 生成    │               │                       │
│  答案验证    │               │                       │
├─────────────┴──────────────┴────────────────────────┤
│  工具层                                              │
│    文档解析(Word/PDF) / 知识抽取 / U盘同步 / 报告导出  │
└─────────────────────────────────────────────────────┘
```

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + Vite 5 + marked.js + Electron 34 | Windows 桌面应用，Markdown 渲染 |
| **后端** | Python 3.10 + FastAPI | SSE 流式 API |
| **LLM** | Qwen2.5-1.5B-Instruct Q4_K_M + llama.cpp | 本地推理，CPU 可运行 |
| **知识图谱** | Neo4j Community | 7 节点 8 关系，1066 实体 / 958 关系 |
| **向量库** | ChromaDB | bge-base-zh-v1.5 (768维)，658 chunks |
| **检索** | 向量(Chroma) + 图(Neo4j) 双路检索 | 语义相似 + 关系推理 |
| **语音** | Vosk (vosk-model-small-cn-0.22) | 中文离线语音识别 |
| **打包** | PyInstaller + electron-builder (NSIS) | 单文件 Setup.exe |

---

## 快速启动

### 前置条件

- Windows 10/11
- Miniconda (Python 3.10)
- Node.js 18+
- Neo4j Community 绿色版（放在 `neo4j/` 目录）
- llama.cpp 预编译包（放在 `llama.cpp/` 目录）
- 模型文件（放在 `model/` 目录）

### 一键启动

```batch
# 双击或命令行运行
start_all.bat
```

服务端口：
| 服务 | 端口 |
|------|:---:|
| 前端 (Vite) | 5173 |
| 后端 (FastAPI) | 8000 |
| Neo4j (Bolt/HTTP) | 7687 / 7474 |
| llama-server | 8082 |
| Vosk 语音 | 8765 |

### 手动启动

```powershell
# 1. Neo4j
cd neo4j\bin && neo4j.bat console

# 2. LLM 推理
cd llama.cpp && llama-server.exe -m ..\model\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 2048 -t 4 --host 127.0.0.1 --port 8082 --mlock

# 3. 后端
conda activate a21
cd backend && uvicorn main:app --host 127.0.0.1 --port 8000

# 4. 前端
cd frontend && npm run dev
```

---

## 项目结构

```
A21_final/
├── README.md                         ← 项目介绍
├── 赛题.txt                          ← 原始赛题
├── import.cypher                     ← 知识图谱初始数据（224行）
├── start_all.bat                     ← 一键启动脚本
├── .gitignore
│
├── backend/                          ← Python FastAPI 后端
│   ├── main.py                       ← 入口
│   ├── requirements.txt              ← Python 依赖
│   ├── .env / .env.example           ← 环境变量
│   ├── api/                          ← 路由层 (8模块)
│   │   ├── ask.py                    ← 核心问答 SSE
│   │   ├── auth.py                   ← 用户认证
│   │   ├── symptoms.py               ← 图谱接口
│   │   ├── feedback.py               ← 反馈+优化
│   │   ├── history.py                ← 历史对话
│   │   ├── sync.py                   ← 数据同步
│   │   └── transcribe.py             ← 语音/文档/报告
│   ├── rag/                          ← RAG 层
│   │   ├── retriever.py              ← 三路检索+RRF融合
│   │   ├── generator.py              ← LLM流式生成
│   │   ├── vector_store.py           ← Chroma向量库
│   │   ├── entity_extractor.py       ← NER+关键词
│   │   ├── validator.py              ← 答案验证
│   │   └── params.json               ← RAG参数配置
│   ├── kg/                           ← 知识图谱
│   │   └── neo4j_client.py           ← Neo4j操作
│   ├── feedback/                     ← 反馈优化
│   │   ├── storage.py                ← 反馈存储
│   │   ├── config.py                 ← 参数管理
│   │   └── optimizer/                ← 优化算法
│   ├── tools/                        ← 工具层
│   │   ├── parser.py                 ← 文档解析
│   │   ├── extractor.py              ← 知识抽取
│   │   ├── sync.py                   ← U盘同步
│   │   └── vosk_http.py              ← 语音服务
│   ├── core/                         ← 核心模块
│   │   ├── config.py                 ← 全局配置
│   │   └── llm.py                    ← LLM客户端
│   └── data/
│       └── database.py               ← SQLite建表
│
├── frontend/                         ← Vue 3 + Electron 前端
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── src/
│   │   ├── App.vue                   ← 主组件（登录+聊天+侧边栏+语音+设置）
│   │   ├── main.js                   ← 入口
│   │   └── api/index.js              ← API封装+SSE
│   └── electron/
│       ├── main.js                   ← Electron主进程
│       └── preload.js                ← 上下文桥接
│
├── A21_final开发过程/                 ← 设计文档
│   ├── docs/                         ← 16篇设计文档
│   │   ├── architecture.md           ← 架构设计
│   │   ├── api-contract.md           ← API契约(17接口)
│   │   ├── data-model.md             ← 数据模型
│   │   ├── requirements.md           ← 需求规格
│   │   ├── testing-plan.md           ← 测试方案
│   │   ├── development-guide.md      ← 开发规范
│   │   ├── traceability-matrix.md    ← 需求追踪矩阵
│   │   └── ...
│   ├── 知识库/                        ← 25篇技术笔记
│   └── 知识图谱设计文档.md             ← KG本体v4.0
│
├── model/                            ← 模型文件 (gitignored)
│   ├── qwen2.5-1.5b-instruct-q4_k_m.gguf
│   ├── bge-base-zh-v1.5/
│   └── vosk-model-small-cn-0.22/
│
├── neo4j/                            ← Neo4j绿色版 (gitignored)
├── llama.cpp/                        ← llama.cpp预编译 (gitignored)
└── data/                             ← 运行时数据 (gitignored)
    ├── chroma_db/
    └── feedbacks.db
```

---

## 核心特性

### 双路混合检索
用户问题 → jieba分词 → **向量检索**(语义相似) + **图检索**(关系推理) → 直接注入 LLM Prompt

### 报告级答案排版
Qwen2.5 chat 格式 Prompt → 强制输出 `## 故障分析 / 维修建议 / 注意事项` 三段式结构 → marked.js 渲染 → 支持标题层级、有序列表

### 答案溯源防幻觉
两层验证：① 引用完整性 ② 事实一致性 → 🟢🟡🔴 三级可信度（metadata 携带，不污染答案文本）

### 反馈自动调优
用户点评(👍/👎) → SQLite 存储 → 积累≥30条触发网格搜索 → 自动优化 α/β/γ 检索权重 + Top-K

### U盘跨设备同步
导出：Neo4j(Cypher) + Chroma(目录) + SQLite + params.json → zip  
导入：MERGE合并 + hash去重 + 冲突提示 → 知识迁移

---

## 文档

| 文档 | 说明 |
|------|------|
| [架构设计](A21_final开发过程/docs/architecture.md) | 6层架构 + 10项技术决策 |
| [API契约](A21_final开发过程/docs/api-contract.md) | 17个接口完整定义 |
| [数据模型](A21_final开发过程/docs/data-model.md) | Chroma + SQLite + params.json |
| [需求规格](A21_final开发过程/docs/requirements.md) | 赛题硬性指标 |
| [测试方案](A21_final开发过程/docs/testing-plan.md) | 单元/集成/验收三层 |
| [开发环境](A21_final开发过程/docs/dev-env-setup.md) | Windows搭建指南 |
| [开发规范](A21_final开发过程/docs/development-guide.md) | Agent协同+路线图 |
| [打包指南](A21_final开发过程/docs/packaging-guide.md) | PyInstaller + electron-builder |
| [知识图谱设计](A21_final开发过程/知识图谱设计文档.md) | 7节点8关系本体 |
| [需求追踪](A21_final开发过程/docs/traceability-matrix.md) | 需求→功能→模块映射 |

---

## 性能指标

| 指标 | 目标 | 状态 |
|------|------|:--:|
| 知识图谱实体数 | ≥500 | ✅ 1066 |
| 知识图谱关系数 | ≥80 | ✅ 958 |
| Top1 答案准确率 | ≥75% | 🔄 待测试 |
| 单轮问答响应时间 | ≤3秒 | ⚠️ ~7-9s（CPU 1.5B 模型瓶颈） |
| 系统内存占用 | ≤8GB | ✅ Q4_K_M量化(~1GB) |
| 完全离线运行 | 是 | ✅ 全本地组件 |
| 模型参数规模 | ≤7B | ✅ 1.5B |

---

## 版本

当前版本: **v2.2** | 最后更新: 2026-05-26

### 变更记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.2 | 2026-05-26 | SSE 换行符 JSON 编码传输、marked.js 渲染、报告级排版、复制按钮 |
| v2.1 | 2026-05-26 | 即时思考指示器、embedding 模型预热、API 改为 OpenAI-compatible `/v1/completions` |
| v2.0 | 2026-05-26 | 移除 BM25、双路检索、Prompt 重构为 Qwen chat 格式、移除 [N] 引用 |
| v1.0 | 2026-05-25 | 初始版本：三路检索 + 流式 SSE + Electron 桌面壳 |

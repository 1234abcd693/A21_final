# A21 开发日志

> 格式: `日期 时间 | 操作者 | 类型 | 描述`

---

## 2026-05-25

| 时间 | 操作者 | 类型 | 描述 |
|------|:--:|------|------|
| 13:00 | AI | 分支 | 创建 `feat/infra` 分支（从 Plan 分出），用作前期开发 |
| 13:00 | AI | 检查 | Python 依赖全部已装（14 个包） |
| 13:05 | AI | 检查 | Node.js v24 + npm 11 已装 |
| 13:05 | AI | 检查 | Neo4j Community 2026.02.3 已解压 |
| 13:05 | AI | 检查 | llama.cpp 未下载 |
| 13:05 | AI | 检查 | Qwen2.5-1.5B 模型未下载 |
| 13:05 | AI | 检查 | whisper.cpp 未下载 |
| 13:05 | AI | 检查 | 前端项目未创建 |
| 13:10 | User | 操作 | Neo4j 启动失败（service 模式），改用 console 模式 |
| 13:28 | User | 操作 | Neo4j console 模式启动成功（Bolt :7687 + HTTP :7474） |
| 13:29 | User | 操作 | 浏览器登录 Neo4j，密码改为 a21password |
| 13:30 | AI | 修复 | import.cypher 含 UTF-8 BOM，去除后重新导入 |
| 13:30 | AI | 操作 | 导入 KG 数据成功：7 类节点 125 实体 + 98 关系 |
| 13:32 | AI | 提交 | `fix: 修复import.cypher的UTF-8 BOM编码问题` |
| 13:35 | AI | 配置 | 编辑 neo4j.conf，去除 APOC 注释 |
| 13:36 | User | 操作 | 重启 Neo4j 使 APOC 配置生效 |
| 13:38 | AI | 检查 | APOC 未加载，发现 apoc-2026.02.3-core.jar 不在 plugins/ 目录 |
| 13:40 | AI | 建议 | 需下载 APOC jar / llama.cpp / 模型文件（用户暂无法下载） |
| 13:45 | AI | 创建 | 本日志文件 `docs/CHANGELOG.md` |
| 13:46 | AI | 提交 | `infra: 完成Neo4j配置(APOC+数据导入)，创建开发日志` |
| 13:47 | AI | 分支 | 创建 `feat/backend` 分支（从 feat/infra 分出），开始后端开发 |
| 14:00 | AI | 开发 | 完成 `backend/data/database.py` — SQLite 5 表初始化 |
| 14:00 | AI | 开发 | 完成 `backend/kg/neo4j_client.py` — Neo4j 图谱操作（CRUD + 图检索） |
| 14:00 | AI | 开发 | 完成 `backend/core/llm.py` — llama-server HTTP 流式/非流式封装 |
| 14:00 | AI | 开发 | 完成 `backend/rag/vector_store.py` — Chroma 向量库初始化 + 检索 |
| 14:05 | AI | 开发 | 完成 `backend/rag/entity_extractor.py` — jieba NER + 同义词扩展 |
| 14:05 | AI | 开发 | 完成 `backend/rag/retriever.py` — BM25 + 向量 + 图检索 + RRF 融合 |
| 14:05 | AI | 开发 | 完成 `backend/rag/generator.py` — Prompt 构建 + SSE 流式生成 |
| 14:05 | AI | 开发 | 完成 `backend/rag/validator.py` — 两层防幻觉验证 |
| 14:10 | AI | 开发 | 完成 `backend/feedback/` — 存储、BaseOptimizer、GridSearch、config |
| 14:10 | AI | 开发 | 完成 `backend/tools/parser.py` — Word/PDF 文档解析 |
| 14:10 | AI | 开发 | 完成 `backend/tools/extractor.py` — 正则知识抽取 |
| 14:10 | AI | 开发 | 完成 `backend/tools/sync.py` — U盘导出/导入 |
| 14:15 | AI | 开发 | 完成 `backend/api/` — 8 个路由模块 + 注册中心 |
| 14:15 | AI | 开发 | 更新 `backend/main.py` — lifespan 初始化数据库 |
| 14:15 | AI | 提交 | `backend: 完成后端全部代码开发(18个文件, 8个API模块)` |
| 14:20 | AI | 分支 | 创建 `feat/frontend` 分支（从 feat/backend 分出） |
| 14:20 | AI | 创建 | `npm create vite@latest frontend -- --template vue` 搭建项目 |
| 14:25 | AI | 开发 | 完成 `frontend/src/api/index.js` — axios 封装 + 全部 API 方法 |
| 14:25 | AI | 开发 | 完成 `TopBar.vue` — 搜索栏组件 |
| 14:25 | AI | 开发 | 完成 `GraphPanel.vue` — 图谱主视图（D3 placeholder） |
| 14:25 | AI | 开发 | 完成 `DetailPanel.vue` — 节点详情 + 溯源面板 |
| 14:25 | AI | 开发 | 完成 `ChatPanel.vue` — 问答面板（SSE 流式接收） |
| 14:25 | AI | 开发 | 完成 `MessageBubble.vue` — 消息气泡（含溯源卡片） |
| 14:25 | AI | 开发 | 完成 `FeedbackButtons.vue` — 点赞/点踩 |
| 14:25 | AI | 开发 | 完成 `InputBox.vue` — 输入框 + 语音按钮 |
| 14:25 | AI | 开发 | 完成 `TraceCard.vue` — 溯源折叠卡片 |
| 14:30 | AI | 修复 | Vite 9 降级到 Vite 5（rolldown 原生模块不兼容 Node v24） |
| 14:35 | AI | 开发 | 添加 Electron 桌面壳（main.js + preload.js + package.json 构建配置） |
| 14:40 | AI | 配置 | neo4j.bat 指向自带 JRE（jlink 裁剪 ~50MB），分发无需系统 Java |

---

## 待完成

- [ ] 下载 APOC jar → `neo4j/.../plugins/`
- [ ] 下载 llama.cpp → `llama.cpp/`
- [ ] 下载 Qwen2.5-1.5B Q4_K_M → `model/`
- [ ] 下载 whisper.cpp → `whisper.cpp/`
- [x] 创建 `feat/backend` 分支开始后端开发 ✅
- [x] 创建 `feat/frontend` 分支开始前端开发 ✅
- [ ] `npm install` + `npm install axios`（你手动跑，网络超时）
- [ ] 创建 `feat/frontend` 分支开始前端开发

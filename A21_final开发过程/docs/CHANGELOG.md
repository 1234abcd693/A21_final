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

---

## 待完成

- [ ] 下载 APOC jar → `neo4j/.../plugins/`
- [ ] 下载 llama.cpp → `llama.cpp/`
- [ ] 下载 Qwen2.5-1.5B Q4_K_M → `model/`
- [ ] 下载 whisper.cpp → `whisper.cpp/`
- [ ] 创建 `feat/backend` 分支开始后端开发
- [ ] 创建 `feat/frontend` 分支开始前端开发

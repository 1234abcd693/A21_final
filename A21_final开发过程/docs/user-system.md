# A21 用户系统与历史管理设计

> 版本: v1.0 | 补充：登录注册、个人中心、历史管理（删除/置顶/搜索）

---

## 一、用户系统设计

### 1.1 为什么需要？

船上一台电脑多人共用。每人应该有独立的对话历史、个人偏好。管理员拥有导入导出和优化权限。

### 1.2 方案概览

因为是**本地离线桌面应用**，不做 OAuth/JWT/邮箱验证。采用轻量本地账号：

```
SQLite 存储用户 + 密码哈希
首次启动 → 创建 admin 账号 → 后续可添加普通用户
登录 → 进入主界面 → 所有操作关联当前用户 ID
```

### 1.3 数据模型（新增表）

#### users 表

```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,              -- bcrypt 哈希
    display_name  TEXT NOT NULL,              -- 显示名（中文）
    role          TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'admin')),
    avatar_color  TEXT DEFAULT '#1890ff',     -- 头像颜色（预设色板）
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
```

#### 修改现有表：添加 user_id

```sql
-- conversations 表增加 user_id
ALTER TABLE conversations ADD COLUMN user_id INTEGER REFERENCES users(id);

-- feedbacks 表增加 user_id
ALTER TABLE feedbacks ADD COLUMN user_id INTEGER REFERENCES users(id);
```

### 1.4 角色权限

| 功能 | user (船员) | admin (管理员) |
|------|:--:|:--:|
| 问答 | ✅ | ✅ |
| 查看自己的历史 | ✅ | ✅ |
| 点赞/点踩 | ✅ | ✅ |
| 语音输入 | ✅ | ✅ |
| 上传文档抽取 | ❌ | ✅ |
| 导入/导出 U盘 | ❌ | ✅ |
| 触发参数优化 | ❌ | ✅ |
| 管理用户（添加/删除） | ❌ | ✅ |

### 1.5 API

#### POST /api/v1/auth/register

管理员添加新用户。

```json
// 请求
{
  "username": "zhangsan",
  "password": "abc123",
  "display_name": "张三",
  "role": "user"
}
// 响应
{ "status": "ok", "user_id": 3 }
```

#### POST /api/v1/auth/login

```json
// 请求
{ "username": "zhangsan", "password": "abc123" }
// 响应
{
  "token": "sess_local_token_xxx",
  "user": { "id": 3, "username": "zhangsan", "display_name": "张三", "role": "user" }
}
```

> Token：本地随机字符串，存在内存中（不做 JWT，本地应用不需要过期机制）。重启应用需重新登录。

#### GET /api/v1/auth/me

当前登录用户信息。

```json
{ "id": 3, "username": "zhangsan", "display_name": "张三", "role": "user" }
```

#### GET /api/v1/users（admin 专用）

用户列表。

```json
{
  "users": [
    { "id": 1, "username": "admin", "display_name": "管理员", "role": "admin" },
    { "id": 2, "username": "lisi", "display_name": "李四", "role": "user" }
  ]
}
```

#### DELETE /api/v1/users/{id}（admin 专用）

删除用户（同时删除该用户的对话历史）。

---

## 二、个人中心

### 2.1 界面布局

```
┌── 个人中心 ──────────────────────────┐
│                                      │
│  [头像]  张三 (zhangsan)              │
│          船员                         │
│                                      │
│  ┌─ 统计 ──────────────────────────┐ │
│  │ 累计问答: 142 次                 │ │
│  │ 点赞: 87  |  点踩: 5             │ │
│  │ 知识贡献: 12 个实体              │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌─ 设置 ──────────────────────────┐ │
│  │ 显示名: [张三_________]          │ │
│  │ 修改密码: [旧密码] [新密码] [确认]│ │
│  │ 默认问答模式: [💬 智能问答]       │ │
│  └────────────────────────────────┘ │
│                                      │
│  ┌─ 管理员区 ──────────────────────┐ │
│  │ [用户管理] [数据统计] [导出日志] │ │
│  └────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
```

### 2.2 需要新增的 API

#### GET /api/v1/user/stats

```json
{
  "stats": {
    "total_questions": 142,
    "total_likes": 87,
    "total_dislikes": 5,
    "knowledge_contributed": 12,
    "active_days": 23
  }
}
```

#### PUT /api/v1/user/profile

修改个人设置。

---

## 三、历史对话管理

### 3.1 现有覆盖 vs 需要补充

| 功能 | 现有 | 需要补 |
|------|:--:|:--:|
| 查看历史列表 | ✅ GET /history | — |
| 查看对话详情 | ✅ GET /history/{sid} | — |
| **删除会话** | ❌ | 🆕 DELETE /history/{sid} |
| **置顶会话** | ❌ | 🆕 PATCH /history/{sid} |
| **搜索会话** | ❌ | 🆕 GET /history/search |
| **批量删除** | ❌ | 🆕 DELETE /history/batch |

### 3.2 新增 API

#### DELETE /api/v1/history/{session_id}

删除单个会话及其所有消息。

```json
// 响应
{ "status": "ok", "deleted_session": "sess_abc123", "deleted_messages": 6 }
```

#### PATCH /api/v1/history/{session_id}

置顶/取消置顶。

```json
// 请求
{ "pinned": true }
// 响应
{ "status": "ok", "session_id": "sess_abc123", "pinned": true }
```

#### GET /api/v1/history/search

搜索会话（标题或消息内容包含关键词）。

```
GET /api/v1/history/search?q=接触器&page=1&page_size=20
```

```json
{
  "query": "接触器",
  "total": 12,
  "sessions": [
    {
      "session_id": "sess_abc123",
      "title": "接触器线圈烧毁相关问答",
      "match_preview": "...检查接触器线圈时发现...",
      "pinned": true,
      "message_count": 4,
      "updated_at": "2026-05-25T14:35:00"
    }
  ]
}
```

#### DELETE /api/v1/history/batch

批量删除。

```json
// 请求
{ "session_ids": ["sess_abc123", "sess_def456"] }
// 响应
{ "status": "ok", "deleted_count": 2 }
```

### 3.3 数据模型修改

conversations 表增加 pinned 字段：

```sql
ALTER TABLE conversations ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0;
CREATE INDEX idx_conversations_pinned ON conversations(pinned);
CREATE INDEX idx_conversations_user ON conversations(user_id);
```

### 3.4 前端交互

```
历史面板（侧边栏或独立页）
┌── 历史对话 ───────────────────────┐
│  🔍 搜索会话...                    │
│                                    │
│  📌 接触器线圈烧毁相关问答          │  ← 置顶 + 加粗
│     4 条消息 · 5月25日 14:30       │     [🗑️删除]
│                                    │
│  📌 发动机常见故障整理             │
│     8 条消息 · 5月24日 09:15       │     [🗑️删除]
│                                    │
│  💬 电动机不能起动怎么办            │
│     2 条消息 · 5月25日 16:00       │     [📌置顶] [🗑️删除]
│                                    │
│  💬 锚机电气故障排查               │
│     6 条消息 · 5月23日 11:20       │     [📌置顶] [🗑️删除]
│                                    │
│  ─────────────────────────────── │
│  ☑ 全选  已选 2 项  [🗑️批量删除]  │
└────────────────────────────────────┘
```

**交互规则**：
- 置顶会话始终排在最上面，加粗 + 📌 图标
- 每个会话右侧有操作菜单（···）或直接显示按钮
- 长按/右键会话 → 弹出菜单（置顶/删除/重命名）
- 搜索为实时过滤（前端筛选）或后端全文搜索

---

## 四、用户界面更新

### 4.1 启动流程

```
双击 exe
    │
    ├── 首次启动（users 表为空）
    │   → 显示注册页面："创建管理员账号"
    │   → 用户名 + 密码 + 确认密码
    │   → 创建 admin → 自动登录 → 进入主界面
    │
    └── 已有用户
        → 显示登录页面
        → 用户名 + 密码
        → 验证 → 进入主界面
```

### 4.2 登录页面

```
┌─────────────────────────┐
│                         │
│  A21 船舶故障诊断系统     │
│                         │
│  ┌─────────────────┐   │
│  │ 👤 用户名        │   │
│  └─────────────────┘   │
│  ┌─────────────────┐   │
│  │ 🔒 密码          │   │
│  └─────────────────┘   │
│                         │
│  [      登 录      ]    │
│                         │
│  记住密码  □             │
│                         │
│  ─────────────────────  │
│  管理员可 [添加用户]     │
│                         │
└─────────────────────────┘
```

### 4.3 侧边栏更新

```
原有              新增/修改
────────          ──────────
📁 知识库浏览
📜 历史对话        → 带搜索、置顶、删除
📊 知识图谱
📤 文档上传
📥 导入/导出       → admin 可见
⚙️ 参数优化        → admin 可见
────────          ──────────
                  👤 个人中心    🆕
                  🚪 退出登录    🆕
```

---

## 五、全部新增 API 汇总

| # | 方法 | 路径 | 说明 |
|---|------|------|------|
| 18 | POST | /api/v1/auth/register | 注册（admin） |
| 19 | POST | /api/v1/auth/login | 登录 |
| 20 | GET | /api/v1/auth/me | 当前用户 |
| 21 | GET | /api/v1/users | 用户列表（admin） |
| 22 | DELETE | /api/v1/users/{id} | 删除用户（admin） |
| 23 | GET | /api/v1/user/stats | 个人统计 |
| 24 | PUT | /api/v1/user/profile | 修改个人设置 |
| 25 | DELETE | /api/v1/history/{sid} | 删除会话 |
| 26 | PATCH | /api/v1/history/{sid} | 置顶/取消 |
| 27 | GET | /api/v1/history/search | 搜索会话 |
| 28 | DELETE | /api/v1/history/batch | 批量删除 |

**总接口数：17 → 28**

---

## 六、协同开发评估

### 当前文档是否足够 Agent 协同开发？

| 维度 | 评分 | 说明 |
|------|:--:|------|
| **需求明确** | ⭐⭐⭐⭐⭐ | traceability-matrix: 8 大类 40+ 功能点，每个标注了来源、用户、模块 |
| **架构清晰** | ⭐⭐⭐⭐⭐ | 6 层架构 + 完整 API 契约 + 数据模型 + 组件树 |
| **前后端合同** | ⭐⭐⭐⭐⭐ | 28 个 API 完整定义，SSE 流式格式，错误格式 |
| **数据模型** | ⭐⭐⭐⭐⭐ | Neo4j + Chroma + SQLite(6表) + params.json 全覆盖 |
| **环境搭建** | ⭐⭐⭐⭐ | dev-env-setup 覆盖 Miniconda/Neo4j/llama.cpp/Node.js |
| **测试标准** | ⭐⭐⭐⭐ | 单元/集成/验收 三层，50 题标准测试集 |
| **编码规范** | ⭐⭐⭐⭐ | .opencode/rules.md 覆盖 Python/JS/Cypher |

**结论：足够。** Agent 拿到这些文档可以独立开始开发各自的模块。前端按 `api-contract.md` 调接口，后端按 `data-model.md` 建库建表。

---

## 七、版本记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-25 | v1.0 | 新增用户系统、个人中心、历史管理（删除/置顶/搜索），API 扩至 28 个 |

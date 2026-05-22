# GitHub 协作工作流程

> A21 项目 · 双人协作 · 单人也可用

---

## 一、分支策略

```
main ───────────────────────────────────────→ 最终交付版本
  │
  ├── Plan ─────────────────────────────────→ 设计文档、计划、架构讨论
  │
  ├── member-A/backend ─────────────────────→ 成员A：后端 + RAG + LLM
  │
  ├── member-B/kg ──────────────────────────→ 成员B：知识图谱 + 数据
  │
  └── dev ──────────────────────────────────→ 集成测试（可选）
```

### 规则
| 分支 | 用途 | 谁在用 |
|------|------|--------|
| `main` | 稳定版本，只有经过验证的代码才能合并进来 | 两人 |
| `Plan` | 设计文档、需求讨论、架构图 —— **现在就在这里** | 两人 |
| `member-A/xxx` | 成员 A 的开发分支 | A |
| `member-B/xxx` | 成员 B 的开发分支 | B |

---

## 二、日常操作流程

### 2.1 每天开始工作前

```bash
# 1. 切到自己的分支
git checkout member-A/backend

# 2. 拉取最新代码
git fetch origin
git rebase origin/main
```

### 2.2 工作中

```bash
# 随时保存进度
git add <改动的文件>
git commit -m "backend: 完成 /ask 接口的混合检索逻辑"

# 推送到远程备份
git push origin member-A/backend
```

**提交信息格式**：`模块: 简述`
```
backend: 实现 BM25 + 向量混合检索
kg: 新增发动机故障实体 30 条
frontend: 聊天界面流式显示
docs: 更新架构设计文档
```

### 2.3 完成一个功能后

```bash
# 1. 确保分支是最新的
git fetch origin
git rebase origin/main

# 2. 推送
git push origin member-A/backend

# 3. 去 GitHub 网页创建 Pull Request
#    base: main  ←  compare: member-A/backend
```

### 2.4 审查合并

- 在 GitHub 上查看 PR
- 另一人 Review 代码
- 确认没问题后点击 "Merge pull request"
- 删除远程功能分支

---

## 三、冲突处理

### 常见场景：两人改了同一个文件

```bash
# 拉取最新并变基
git fetch origin
git rebase origin/main

# 如果有冲突，Git 会提示。打开冲突文件：
# <<<<<<< HEAD        ← 远程的
# =======             ← 分界线
# >>>>>>> 你的修改    ← 你写的

# 手动编辑，保留正确内容，删除标记。然后：
git add <文件>
git rebase --continue
```

### 紧急情况：搞乱了想重来
```bash
git rebase --abort      # 放弃变基，回到之前状态
git reset --hard HEAD   # 放弃所有未提交的修改（谨慎！）
```

---

## 四、Pull Request 规范

### PR 标题格式
```
[模块] 简短描述
```
例：`[backend] 实现混合检索与流式问答`

### PR 描述模板
```markdown
## 做了什么
- 实现了 /ask 接口
- 混合检索 BM25 + 向量

## 测试方法
1. 启动后端 `python main.py`
2. POST /api/v1/ask {"question": "发动机无法启动"}

## 截图（前端改动时必填）
（粘贴截图）
```

---

## 五、.gitignore 已配置忽略项

以下文件**不会**上传到 GitHub：
- `opencode.json`、`.opencode/` —— OhMyOpenCode 本地配置
- `.obsidian/` —— Obsidian 本地配置
- `*.exe`、`*.gguf`、`node_modules/`、`__pycache__/`、`.env`

---

## 六、单人模式（如果你独自工作时）

简化版：
```bash
# 直接在 Plan 或 dev 分支工作
git add -A
git commit -m "做了什么"
git push

# 合并到 main
git checkout main
git merge Plan
git push
```

不需要 PR 和 Review 流程。

---

## 七、速查卡片

| 操作 | 命令 |
|------|------|
| 查看状态 | `git status` |
| 查看分支 | `git branch -a` |
| 切换分支 | `git checkout 分支名` |
| 拉取最新 | `git fetch origin` |
| 提交 | `git add .` → `git commit -m "消息"` |
| 推送 | `git push origin 分支名` |
| 变基到 main | `git rebase origin/main` |
| 撤销未提交修改 | `git checkout -- 文件名` |
| 查看提交历史 | `git log --oneline -10` |

# GitHub 协作工作流程

> A21 项目 · 双人协作 · 面向 Git 新手  
> 先讲原理，再讲操作。读完这篇，你应该能理解每一步在做什么、为什么要这样做。

---

## 零、先搞懂 Git 是什么

### Git ≠ GitHub

| | Git | GitHub |
|------|-----|--------|
| 是什么 | 版本管理工具，安装在你的电脑上 | 网站，托管 Git 仓库 |
| 在哪里 | 你的电脑（本地） | 云端服务器 |
| 类比 | Word 的"历史版本"功能，但是专业的 | 网盘，专门存代码历史 |

### 核心概念：三棵树

Git 在你的电脑上维护着三个"位置"：

```
工作目录              暂存区                本地仓库              远程仓库
(Working Dir)    →    (Stage/Index)    →   (Local Repo)    →   (Remote/GitHub)
    │                      │                     │                    │
  你写的代码          git add 之后         git commit 之后       git push 之后
  直接改文件          准备提交的文件         已保存的版本         上传到 GitHub
```

> **一句话**：你在工作目录改代码 → `git add` 告诉 Git "这些改动我要保存" → `git commit` 真正保存为一个版本 → `git push` 上传到 GitHub。

### 核心概念：分支是什么

分支 = 一条独立的开发线。想象你在写小说：

```
main 分支：已出版的第一版（稳定，不能乱改）
                ↓ 从这分叉
feat/rag 分支：正在写第二版的新章节（随便改，不影响已出版的）
```

**为什么要用分支？**
- 你不会把写到一半的代码直接放进稳定版本
- 队友可以同时在不同分支上工作，互不干扰
- 做坏了可以扔掉分支重来，不影响主线

---

## 一、分支策略（按模块，不按人）

### 分支结构

```
main ────────────────────────────────────────────→ 稳定版本，只有经过验证的代码
  │
  ├── Plan ──────────────────────────────────────→ 设计文档、架构讨论（我们现在在这里）
  │
  ├── dev ───────────────────────────────────────→ 集成测试，功能分支先合到这里
  │   │
  │   ├── feat/frontend ─────────────────────────→ 前端交互层（聊天界面、图谱可视化）
  │   ├── feat/backend ──────────────────────────→ 服务层（FastAPI 路由、SSE、中间件）
  │   ├── feat/rag ──────────────────────────────→ RAG 层（检索、生成、答案验证）
  │   ├── feat/kg ───────────────────────────────→ 知识图谱（Neo4j 本体、Cypher 查询）
  │   ├── feat/tools ────────────────────────────→ 工具层（抽取、清洗、导入导出）
  │   └── feat/feedback ─────────────────────────→ 反馈层（收集、存储、参数调优）
  │
  └── （用完就删的功能分支...）
```

### 分支命名规则

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat/` | 新功能开发 | `feat/rag`, `feat/frontend` |
| `fix/` | 修 bug | `fix/rag-timeout` |
| `docs/` | 文档更新 | `docs/api-spec` |

### 分支生命周期

```
git checkout -b feat/rag        ← 从 dev 创建
       ↓
...写代码，反复 add/commit...
       ↓
git push origin feat/rag        ← 推到 GitHub 备份
       ↓
在 GitHub 网页创建 Pull Request → dev
       ↓
队友 Review 通过，合并到 dev
       ↓
git branch -d feat/rag          ← 删除本地分支
git push origin --delete feat/rag ← 删除远程分支
```

---

## 二、每条命令到底在做什么

### `git status` —— 看看现在什么情况

```bash
git status
```

输出示例，逐行解释：

```
On branch feat/rag                              ← 你在 feat/rag 分支上
Changes not staged for commit:                  ← 有改动，但还没 git add
  modified:   backend/rag/retriever.py           ← 这个文件被你改过

Untracked files:                                 ← 新文件，Git 从来没管过它
  backend/rag/reranker.py
```

### `git add` —— 告诉 Git "这些文件我要提交"

```bash
git add backend/rag/retriever.py    # 添加一个文件
git add backend/rag/                # 添加整个目录
git add .                           # 添加当前目录所有改动
```

**原理**：`git add` 把文件从"工作目录"搬到"暂存区"。暂存区 = 你准备提交的"购物车"。

> ⚠️ `git add .` 是全部添加。如果你只想提交部分改动，请指定文件。

### `git commit` —— 真正保存一个版本

```bash
git commit -m "rag: 实现 BM25 检索器，支持中文分词"
```

-m 后面的引号里是提交信息。写清楚你做了什么。

提交后，这个版本就永久保存在本地仓库了。你可以随时通过 `git log` 找回它。

**提交信息格式**：`模块: 做了什么`

```
rag: BM25 检索器支持 jieba 中文分词
kg: 新增发动机故障实体 30 条，关系 15 条
frontend: 聊天界面支持 SSE 流式渲染
backend: 实现 /api/v1/feedback 路由
docs: 更新架构设计文档
```

### `git push` —— 上传到 GitHub

```bash
git push origin feat/rag
```

`origin` = GitHub 仓库的别名，`feat/rag` = 你要推哪个分支。

推完之后，队友就能在 GitHub 上看到你的代码了。

### `git pull` vs `git fetch` —— 获取远程更新

| 命令 | 做什么 | 什么时候用 |
|------|--------|-----------|
| `git fetch origin` | 只下载远程更新，**不合并**到你的代码 | **推荐**，先看看有什么变化 |
| `git pull` | 下载 + 自动合并 | 简单场景可以用，但可能产生混乱的合并记录 |

**推荐做法**：
```bash
git fetch origin                    # 下载
git rebase origin/main              # 把你的提交"接"到最新代码后面
```

### `git rebase` —— 变基（重要！）

**原理**：把你的提交"搬"到目标分支的最新位置。

```
变基前：
main:     A → B → C
               ↘
feat/rag:       D → E （你的两次提交）

变基后（git rebase main）：
main:     A → B → C
                    ↘
feat/rag:            D' → E' （你的提交被重新放在最新代码后面）
```

**为什么用 rebase 而不是 merge？**

| | rebase | merge |
|------|--------|-------|
| 历史记录 | 一条直线，干净 | 分叉合并，多一个"合并提交" |
| 冲突处理 | 逐个提交解决 | 一次性解决 |
| 推荐场景 | 把主分支的更新同步到你的分支 | 把功能分支合并到主分支 |

简单记：**同步更新用 rebase，合并功能用 merge（或 GitHub 网页的 PR 按钮）。**

---

## 三、日常工作流（按场景）

### 场景 1：开始一个新功能

```bash
# 1. 确保 dev 是最新的
git checkout dev
git fetch origin
git rebase origin/dev

# 2. 从 dev 创建功能分支
git checkout -b feat/rag

# 3. 确认你在正确的分支上
git branch    # 前面有 * 的就是当前分支
```

### 场景 2：日常开发循环

这是你每天重复最多的操作：

```bash
# 写了一些代码后...
git status                       # 看看改了什么
git add backend/rag/retriever.py # 添加到暂存区
git commit -m "rag: 实现 BM25 检索"      # 提交

# 又写了一些...
git add backend/rag/generator.py
git commit -m "rag: 实现 LLM 调用封装"

# 一天结束前，推送到 GitHub 备份
git push origin feat/rag
```

**原则**：
- 小步提交，不要攒一大堆才提交。一个逻辑改动 = 一次 commit。
- 每天结束前 push 到 GitHub，防止电脑坏了丢代码。

### 场景 3：同步主分支的最新代码

队友往 dev 合了东西，你需要同步过来：

```bash
# 1. 先保存你当前的改动
git add .
git commit -m "WIP: 临时保存"

# 2. 拉取远程更新
git fetch origin

# 3. 变基到最新的 dev
git rebase origin/dev

# 4. 如果有冲突，解决后继续（见第五节）
```

### 场景 4：功能完成，合并到 dev

```bash
# 1. 确保你的分支包含最新的 dev 代码
git fetch origin
git rebase origin/dev

# 2. 推送到 GitHub
git push origin feat/rag

# 3. 去 GitHub 网页：
#    点击 "Compare & pull request"
#    base: dev  ←  compare: feat/rag
#    填写 PR 描述，点击 "Create pull request"

# 4. 队友 Review 通过后，在网页上点击 "Merge"

# 5. 清理本地分支
git checkout dev
git fetch origin
git rebase origin/dev        # 拉取合并后的 dev
git branch -d feat/rag       # 删除本地分支
```

---

## 四、Pull Request（PR）详解

### PR 是什么

PR = "请把我的代码拉进你的分支"。你不是直接往 dev 或 main 写代码，而是提交一个请求，让队友看过之后再合并。

### 为什么需要 PR

- **代码审查**：队友能发现你没注意到的问题
- **讨论记录**：PR 下的评论就是设计决策的历史记录
- **安全网**：代码在被合入主分支之前必须通过审查

### PR 创建步骤（图文指引）

1. 浏览器打开 `https://github.com/1234abcd693/A21_final`
2. 点击顶部 `Pull requests` 标签
3. 点击绿色 `New pull request` 按钮
4. 设置：
   - **base: dev** ← 目标分支（合并到哪里）
   - **compare: feat/rag** ← 你的分支（从哪里合并）
5. 标题格式：`[模块] 简短描述`
6. 描述模板：

```markdown
## 做了什么
- 实现了 BM25 检索器，支持 jieba 分词
- 实现了向量检索器（Chroma + MiniLM）
- 两路融合使用加权求和

## 怎么测试
1. 启动后端: `python main.py`
2. 发送请求: POST /api/v1/ask {"question": "发动机无法启动"}
3. 预期: 返回流式答案，包含引用标记 [1][2]

## 截图（前端改动必填）
（拖入图片）
```

7. 点击 `Create pull request`
8. 在右侧 `Reviewers` 处添加队友

### Review 方操作

1. 打开 PR 页面，点击 `Files changed` 标签
2. 逐行查看改动，有疑问点击行号左侧的 `+` 添加评论
3. 看完后点击 `Review changes`
   - `Comment`：只是一般反馈
   - `Approve`：通过，可以合并
   - `Request changes`：有问题，需要修改后才能合并
4. 通过后点击 `Merge pull request` → `Confirm merge`

---

## 五、冲突处理

### 冲突是什么

你和队友改了同一个文件的同一行，Git 不知道保留谁的。

### 冲突长什么样

```python
<<<<<<< HEAD              ← 远程（目标分支）的版本
def search(query):
    return bm25_search(query)
=======                    ← 分界线
def search(query):
    return hybrid_search(query, alpha=0.6)
>>>>>>> feat/rag          ← 你的版本
```

### 怎么解决

```bash
# 1. 变基时遇到冲突，Git 会暂停
git rebase origin/dev

# Git 提示: CONFLICT in backend/rag/retriever.py

# 2. 打开那个文件，手动编辑
#    删除 <<<<<<<, =======, >>>>>>> 这些标记
#    保留正确的代码

# 3. 标记冲突已解决
git add backend/rag/retriever.py

# 4. 继续变基
git rebase --continue

# 5. 如果冲突太多想放弃重来
git rebase --abort
```

**原则**：
- 不确定保留谁的时候，**找队友商量**，不要自己猜
- 解决完冲突后，重新测试一下代码是否正常

---

## 六、常见翻车现场与抢救

| 场景 | 抢救命令 | 原理 |
|------|----------|------|
| 改错了文件，想撤销 | `git checkout -- 文件名` | 用暂存区版本覆盖工作目录 |
| `git add` 加错了文件 | `git reset HEAD 文件名` | 把文件从暂存区移回工作目录 |
| commit 信息写错了 | `git commit --amend -m "新信息"` | 修改最后一次 commit |
| 忘了切分支，在 dev 上写了代码 | `git stash` → `git checkout -b feat/xxx` → `git stash pop` | 把改动暂存，切到正确分支后再拿出来 |
| 整个功能做坏了想重来 | `git checkout feat/rag` → `git reset --hard origin/feat/rag` | 用远程版本完全覆盖本地 |
| rebase 搞乱了 | `git rebase --abort` | 放弃变基，回到原来的样子 |

---

## 七、双人协作的一天（完整示例）

### 上午 9:00 — 两人同步

```bash
# A 和 B 都做：
git checkout dev
git fetch origin
git rebase origin/dev
```

### A 开始做 RAG 检索

```bash
git checkout -b feat/rag
# ...写代码...
git add backend/rag/
git commit -m "rag: 实现 BM25 检索器"
git push origin feat/rag
```

### B 开始做知识图谱

```bash
git checkout -b feat/kg
# ...写代码...
git add backend/kg/
git commit -m "kg: 新增发动机故障实体和关系"
git push origin feat/kg
```

### 下午 — B 先完成了，创建 PR

B 在 GitHub 上创建 PR：`feat/kg` → `dev`。A 去 Review，通过后合并。

### A 同步 B 的代码

```bash
git checkout feat/rag
git fetch origin
git rebase origin/dev    # 现在 dev 里已经有 B 的知识图谱代码了
# 如果有冲突，解决后继续
git push origin feat/rag --force-with-lease   # 注意：rebase 后需要 force push
```

> ⚠️ `--force-with-lease` 只在你自己独占的分支上用！不要对 main、dev 用！

### A 完成后创建 PR

A 在 GitHub 上创建 PR：`feat/rag` → `dev`。B Review，通过，合并。

---

## 八、速查卡片

| 操作 | 命令 |
|------|------|
| 看状态 | `git status` |
| 看分支 | `git branch -a` |
| 看历史 | `git log --oneline -10` |
| 切分支 | `git checkout 分支名` |
| 新建并切换 | `git checkout -b 分支名` |
| 添加文件 | `git add 文件名` 或 `git add .` |
| 提交 | `git commit -m "模块: 简述"` |
| 推送到 GitHub | `git push origin 分支名` |
| 拉取远程更新 | `git fetch origin` |
| 变基同步 | `git rebase origin/dev` |
| 放弃变基 | `git rebase --abort` |
| 暂存当前改动 | `git stash` |
| 取出暂存 | `git stash pop` |
| 删除本地分支 | `git branch -d 分支名` |
| 删除远程分支 | `git push origin --delete 分支名` |
| 撤销工作区改动 | `git checkout -- 文件名` |
| 撤销 add | `git reset HEAD 文件名` |

---

## 九、.gitignore 已忽略项

以下**绝对不会**上传到 GitHub：
- `opencode.json`、`.opencode/` — 本地 AI 工具配置
- `.obsidian/` — Obsidian 笔记配置
- `*.exe`、`*.gguf`、`.env` — 二进制和敏感文件
- `node_modules/`、`__pycache__/`、`venv/` — 依赖和虚拟环境

---

## 十、一句话总结

```
改代码 → git add → git commit → git push
更新   → git fetch → git rebase
合并   → GitHub 网页创建 PR → Review → Merge
搞砸   → git rebase --abort（回到安全状态）
```

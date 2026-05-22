# Node.js 与 npm

## 一句话解释

Node.js = 让 JavaScript **脱离浏览器**也能运行。npm = Node.js 的"应用商店"。

## Node.js 是什么

JavaScript 本来只能在浏览器里跑。Node.js 把它"解放"出来，让你能在命令行里跑 JavaScript。

类比：Python 解释器 之于 Python ≈ Node.js 之于 JavaScript。

## 为什么我们需要它？

Electron 的主进程是 Node.js 环境。Vite 构建工具也是 Node.js 写的。

**你需要 Node.js，但不需要写 Node.js 代码。**

## npm 是什么

npm = Node Package Manager = 安装 JS 库的工具。

类比：pip 之于 Python ≈ npm 之于 JavaScript。

```bash
# Python 安装库             # JavaScript 安装库
pip install requests         npm install axios
pip install flask            npm install vue

# Python 的 requirements.txt  # JavaScript 的 package.json
# pip install -r req.txt      # npm install（读 package.json 自动装全部）
```

## 你需要知道的命令

| 命令 | 做什么 | 类比 Python |
|------|--------|-------------|
| `npm init` | 初始化项目，创建 `package.json` | 创建 `pyproject.toml` |
| `npm install 包名` | 安装一个库 | `pip install 包名` |
| `npm install` | 安装 `package.json` 里列出的所有库 | `pip install -r requirements.txt` |
| `npm run dev` | 启动开发服务器（Vite） | `python main.py` |
| `npm run build` | 构建生产版本 | 打包成 exe |

## 我们项目需要装的包

```bash
npm create vite@latest frontend -- --template vue  # 创建 Vue 项目（一行命令）
cd frontend
npm install             # 安装 Vue 和其他基础依赖
npm install axios       # HTTP 请求库（和 Python 后端通信）
npm install element-plus  # UI 组件库（按钮、输入框等）
npm install d3          # 知识图谱可视化（力导向图）
```

## node_modules 是什么

`npm install` 后生成的目录，包含所有下载的库。**这个目录巨大（几百 MB），已经被 .gitignore 排除了**，不会上传到 GitHub。

类比：Python 的 `venv/Lib/site-packages/`。

## 你实际要用的

你不需要理解 Node.js 的底层。日常操作就是：
1. `npm install`（装依赖，第一次或更新依赖时用）
2. `npm run dev`（启动开发服务器，写 Vue 代码时用）
3. `npm run build`（打包前端，最终交付时用）

# Vite 构建工具

## 一句话解释

Vite = 帮你**快速搭建和管理 Vue 项目**的工具。创建项目、启动开发服务器、打包成品都靠它。

## 类比

| Python | JavaScript (Vite) |
|--------|-------------------|
| `python -m venv venv` 创建虚拟环境 | `npm create vite@latest` 创建项目 |
| `python main.py` 启动开发服务器 | `npm run dev` 启动 Vite 开发服务器 |
| `pyinstaller main.py` 打包成 exe | `npm run build` 打包成静态文件 |

## 为什么叫 Vite？

法语"快"的意思。确实快 —— 改一行 Vue 代码，浏览器毫秒级热更新，不需要刷新页面。

## 项目结构（你运行 `npm create vite` 后会得到）

```
frontend/
├── index.html            ← 入口 HTML（一个空壳，挂载 Vue）
├── package.json          ← 项目配置 + 依赖列表
├── vite.config.js        ← Vite 配置（一般不用改）
├── node_modules/         ← 下载的库（已 gitignore）
├── public/               ← 静态资源（图标等）
└── src/
    ├── main.js           ← Vue 应用入口
    ├── App.vue           ← 根组件
    ├── components/       ← 你写的组件放这里
    │   ├── ChatWindow.vue
    │   ├── MessageBubble.vue
    │   └── ...
    ├── views/            ← 页面级组件
    └── api/              ← 和后端通信的代码
        └── index.js      ← axios 封装
```

## 日常开发流程

```bash
# 进入前端目录
cd frontend

# 启动开发服务器（写代码时一直开着）
npm run dev
# → 输出: http://localhost:5173/
# 浏览器打开这个地址就能看到你的 Vue 界面
# 改任何 .vue 文件 → 浏览器立刻更新（热更新）
```

## 构建生产版本

```bash
npm run build
# → 输出到 dist/ 目录
# dist/ 里的文件是纯 HTML + CSS + JS，Electron 直接加载
```

## Vite 和 Electron 的关系

```
开发阶段：
  npm run dev → Vite 启动 localhost:5173（浏览器看效果）

Electron 集成后：
  Electron 窗口加载 Vite 的开发地址（开发时）
  Electron 窗口加载 dist/ 里的文件（打包时）
```

开发时你可以先在浏览器里调试 Vue 界面（不用打开 Electron），更快更方便。

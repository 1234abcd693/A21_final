# A21 桌面应用打包方案

> 目标：交付一个 Windows .exe，用户双击就能用，无需安装任何依赖。

---

## 一、打包策略总览

```
┌────────────────────────────────────────────────┐
│            A21_Final.exe (入口)                  │
│          (electron-builder 打包)                 │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Electron 壳                               │  │
│  │  · 启动时自动拉起所有子进程                  │  │
│  │  · 窗口加载 Vue 前端                        │  │
│  │  · 关闭时自动停止所有子进程                  │  │
│  └──────────────────────────────────────────┘  │
│                    │                             │
│  ┌─────────────────┴───────────────────────┐   │
│  │  resources/  (随 exe 一起分发)            │   │
│  │                                          │   │
│  │  backend.exe       ← PyInstaller 打包     │   │
│  │  llama-server.exe  ← llama.cpp 预编译     │   │
│  │  model/            ← .gguf 模型文件       │   │
│  │  neo4j/            ← Neo4j 绿色版         │   │
│  │  import.cypher     ← KG 初始数据          │   │
│  │  start-services.js ← 子进程管理脚本        │   │
│  └──────────────────────────────────────────┘   │
└────────────────────────────────────────────────┘
```

## 二、各组件打包方式

| 组件 | 语言 | 打包工具 | 产物 | 大小 |
|------|:--:|----------|------|------|
| 前端 (Vue) | JS | Vite build → electron-builder | 嵌入 exe | ~3 MB |
| Electron 壳 | JS | electron-builder | A21_Final.exe | ~80 MB |
| 后端 (FastAPI) | Python | PyInstaller | backend.exe | ~50 MB |
| LLM 推理 | C++ | 预编译，无需打包 | llama-server.exe | ~20 MB |
| 模型 | — | 直接包含 | model/*.gguf | ~1 GB |
| 图数据库 | Java | 绿色版直接包含 | neo4j/ | ~200 MB |
| 向量库 | Python | 包含空库在 backend.exe 旁 | chroma_db/ | ~5 MB 初始 |

**总大小估算**：exe + resources ≈ 1.3 GB（主要是模型文件和 Neo4j）

---

## 三、Python 后端打包（PyInstaller）

### 3.1 安装 PyInstaller

```powershell
conda activate a21
pip install pyinstaller
```

### 3.2 打包配置

创建 `backend/build.spec`：

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含 Chroma 依赖
        ('../data/chroma_db', 'data/chroma_db'),
    ],
    hiddenimports=[
        'chromadb',
        'chromadb.config',
        'chromadb.db',
        'sentence_transformers',
        'sentence_transformers.models',
        'jieba',
        'neo4j',
        'langchain',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # 不显示命令行窗口（生产模式）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### 3.3 执行打包

```powershell
cd backend
pyinstaller build.spec --clean --noconfirm
# 产物: backend/dist/backend.exe
```

### 3.4 常见问题

| 问题 | 解决 |
|------|------|
| 缺少 chromadb 模块 | 确认 `hiddenimports` 列表完整，加 `--collect-all chromadb` |
| `sentence-transformers` 找不到模型 | 确保 huggingface 模型已下载到本地缓存 |
| exe 太大 | 用 `--exclude-module` 排除不用的包（如 matplotlib, numpy 子模块） |

---

## 四、前端打包（electron-builder）

### 4.1 安装依赖

```powershell
cd frontend
npm install
npm install electron electron-builder --save-dev
```

### 4.2 Electron 主进程

`frontend/electron/main.js` 核心逻辑：

```javascript
const { app, BrowserWindow } = require('electron')
const { spawn } = require('child_process')
const path = require('path')

let backendProcess, neo4jProcess, llamaProcess

app.whenReady().then(async () => {
  const resourcesPath = process.resourcesPath // electron-builder 的 resources 目录

  // 1. 启动 Neo4j
  neo4jProcess = spawn(
    path.join(resourcesPath, 'neo4j', 'bin', 'neo4j.bat'),
    ['console'],
    { cwd: path.join(resourcesPath, 'neo4j', 'bin') }
  )

  // 2. 启动 llama-server
  llamaProcess = spawn(
    path.join(resourcesPath, 'llama-server.exe'),
    ['-m', path.join(resourcesPath, 'model', 'qwen2.5-1.5b-instruct-q4_k_m.gguf'),
     '-c', '2048', '-t', '4', '--host', '127.0.0.1', '--port', '8080', '--mlock']
  )

  // 3. 启动 Python 后端
  backendProcess = spawn(
    path.join(resourcesPath, 'backend.exe'),
    [],
    { env: { ...process.env, NEO4J_PASSWORD: 'a21password' } }
  )

  // 4. 等待服务就绪
  await waitForService('http://127.0.0.1:8000/health', 30000)
  await waitForService('http://127.0.0.1:8080/health', 30000)

  // 5. 创建窗口
  const win = new BrowserWindow({ width: 1200, height: 800 })
  win.loadFile('dist/index.html')  // Vite build 产物
})

app.on('before-quit', () => {
  backendProcess?.kill()
  llamaProcess?.kill()
  neo4jProcess?.kill()
})
```

### 4.3 electron-builder 配置

`frontend/package.json` 中添加：

```json
{
  "main": "electron/main.js",
  "build": {
    "appId": "com.a21.ship-diagnosis",
    "productName": "A21 船舶故障诊断系统",
    "directories": {
      "output": "release"
    },
    "extraResources": [
      { "from": "../backend/dist/backend.exe", "to": "backend.exe" },
      { "from": "../llama.cpp/llama-server.exe", "to": "llama-server.exe" },
      { "from": "../model/", "to": "model/" },
      { "from": "../neo4j/", "to": "neo4j/", "filter": ["**/*", "!data/databases/neo4j/*"] },
      { "from": "../import.cypher", "to": "import.cypher" }
    ],
    "win": {
      "target": "nsis",
      "icon": "public/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true
    }
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "pack": "electron-builder --win"
  }
}
```

### 4.4 执行打包

```powershell
cd frontend
npm run build          # 1. Vite 构建前端
npm run pack           # 2. electron-builder 打包 exe
# 产物: frontend/release/A21 船舶故障诊断系统 Setup.exe
```

---

## 五、Neo4j 绿色版处理

Neo4j 需要 Java 运行环境。两个方案：

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| A: 内置 JRE | 在 resources/neo4j/ 里放一个 jre/ 目录 | 用户零依赖 | 增加 ~150 MB |
| B: 系统检测 | 启动时检查系统是否装了 Java，没装就提示 | 更小的安装包 | 用户可能不会装 |

**推荐方案 A**（仅增加 ~50 MB）：

```powershell
# 从你已安装的 JDK 26 生成精简 JRE
jlink --add-modules java.base,java.logging,java.xml,java.management,java.naming,java.sql --output neo4j\jre
```

然后修改 `neo4j\bin\neo4j.bat`，在文件开头加上：
```batch
set JAVA_HOME=%~dp0..\jre
set PATH=%JAVA_HOME%\bin;%PATH%
```

Neo4j 启动时自动用我们自带的 Java，不管用户系统有没有装 Java。

---

## 六、模型文件处理

模型文件 1GB，有两种分法方式：

| 方案 | 做法 |
|------|------|
| A: 随 exe 打包 | `extraResources` 包含 `model/` |
| B: 首次启动下载 | exe 很小，首次运行自动下载模型 |

**推荐方案 A**：赛题要求"完全离线运行"，不能依赖下载。虽然安装包 1.3GB，但满足离线要求。

如果文件太大无法分发，方案 B 作为备选：exe 启动后检查模型是否存在，不存在就提示用户从 U 盘拷贝。

---

## 七、完整构建流程

```powershell
# ===== 一次性构建 =====

# 1. Python 后端
cd backend
pip install -r requirements.txt pyinstaller
pyinstaller build.spec --clean --noconfirm
# → backend/dist/backend.exe

# 2. 前端
cd frontend
npm install
npm run build
npm run pack
# → frontend/release/A21 船舶故障诊断系统 Setup.exe

# 3. 验证
# 在干净 Windows 虚拟机中安装，双击 exe，确认：
#   - Neo4j 自动启动
#   - llama-server 自动启动
#   - 窗口正常打开
#   - 问答功能正常
```

---

## 八、与赛题要求的对照

| 赛题要求 | 实现 |
|----------|------|
| Windows 可执行程序包 | ✅ electron-builder 生成 Setup.exe |
| 无需安装依赖 | ✅ 所有依赖内置在 resources/ |
| 启动时间 ≤30s | ✅ Neo4j(~10s) + llama-server(~2s) + backend(~3s) = ~15s |
| 离线运行 | ✅ 模型、Neo4j、后端全部本地 |
| 支持后续扩展 | ✅ import.cypher 导入新数据，无需重装 |

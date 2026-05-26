/**
 * A21 Electron 主进程 — 桌面应用生命周期管理
 * ==============================================
 * 
 * 职责：
 *   1. 启动子进程：Neo4j 图数据库 + llama-server(LLM推理) + FastAPI 后端 + Vosk 语音
 *   2. 等待服务就绪：轮询 /health 接口，确保所有服务启动后再显示窗口
 *   3. 管理窗口：创建 BrowserWindow → 加载 Vue 前端 → 服务就绪后 show()
 *   4. IPC 通信：文件对话框（打开/保存），供渲染进程通过 contextBridge 调用
 *   5. 清理资源：窗口关闭时 kill 所有子进程
 * 
 * 开发模式 vs 生产模式：
 *   - 开发模式 (isDev=true)：从本地文件系统启动各组件，前端加载 Vite dev server(:5173)
 *   - 生产模式 (isDev=false)：从 resources/ 目录启动预编译的 exe，加载打包后的 dist/index.html
 * 
 * 安全配置：
 *   - contextIsolation: true  — 渲染进程无法直接访问 Node.js API
 *   - nodeIntegration: false  — 渲染进程不能使用 require()
 *   - preload.js              — 通过 contextBridge 暴露安全的 IPC 接口
 * 
 * 已知问题：
 *   - NEO4J_PASSWORD 硬编码在 env 对象中（line 64），应改为从配置文件读取
 *   - Vite 等待的 catch 块为空（line 127），静默吞掉 Vite 未就绪错误
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const http = require('http')

// ==================== 全局状态 ====================
let mainWindow = null
const processes = []          // 所有启动的子进程引用（用于退出时 kill）
const isDev = !app.isPackaged // 根据是否打包判断开发/生产模式

// 项目根路径：开发模式 = 项目根目录，生产模式 = resources/
const rootPath = isDev ? path.join(__dirname, '..', '..') : process.resourcesPath

// ==================== 子进程管理 ====================

/**
 * 启动子进程（静默模式：隐藏控制台窗口，管道捕获输出）。
 * 
 * @param {string} cmd  - 可执行文件路径
 * @param {string[]} args - 命令行参数
 * @param {object} opts  - { cwd, env, label } 
 *   - windowsHide: true  — 不弹出控制台窗口（用户体验）
 *   - stdio: 'pipe'      — 通过管道捕获 stdout/stderr（调试用）
 *   - label              — 日志前缀，如 '[neo4j]' '[llama]'
 * @returns {ChildProcess} — 子进程引用
 */
function spawnQuiet(cmd, args, opts = {}) {
  const p = spawn(cmd, args, {
    windowsHide: true,
    stdio: 'pipe',
    ...opts,
  })
  // 将子进程输出转发到主进程控制台（方便调试）
  p.stdout?.on('data', d => console.log(`[${opts.label||cmd}] ${d}`.trim()))
  p.stderr?.on('data', d => console.error(`[${opts.label||cmd}] ${d}`.trim()))
  processes.push(p)
  return p
}

/**
 * 轮询等待 HTTP 服务就绪。
 * 
 * 每秒发送一次 HTTP GET 请求，收到 200 响应后 resolve。
 * 超过最大重试次数后 reject（不阻塞启动，仅打印警告）。
 * 
 * @param {string} url        - 健康检查 URL（如 http://127.0.0.1:8000/health）
 * @param {number} maxRetries - 最大重试次数（默认 30 次 = 30 秒）
 * @returns {Promise<boolean>}
 */
function waitForService(url, maxRetries = 30) {
  return new Promise((resolve, reject) => {
    let tries = 0
    const check = () => {
      http.get(url, (res) => {
        if (res.statusCode === 200) resolve(true)
        else retry()
      }).on('error', retry)  // 连接被拒 → 重试
    }
    const retry = () => {
      if (++tries >= maxRetries) reject(new Error(`Service ${url} not ready after ${maxRetries}s`))
      else setTimeout(check, 1000)  // 每秒重试一次
    }
    check()
  })
}

// ==================== 服务启动 ====================

/**
 * 开发模式：从本地文件系统启动所有服务组件。
 * 
 * 启动顺序：
 *   1. Neo4j 图数据库 — console 模式（前台，方便看日志）
 *   2. llama-server — LLM 推理引擎，加载 Qwen2.5-1.5B Q4_K_M 量化模型
 *   3. FastAPI 后端 — uvicorn，含 RAG/反馈/同步/语音等全部路由
 *   4. Vosk HTTP 服务 — 中文语音识别（独立进程，提高可靠性）
 */
function startServices() {
  if (!isDev) return startPackaged()

  const modelPath = path.join(rootPath, 'model')

  // 1. Neo4j 图数据库 — console 模式启动
  console.log('[A21] Starting Neo4j...')
  spawnQuiet('cmd', [
    '/c', 'cd', '/d',
    path.join(rootPath, 'neo4j', 'neo4j-community-2026.02.3', 'bin'),
    '&&', 'neo4j.bat', 'console'
  ], { label: 'neo4j' })

  // 2. llama-server — LLM 推理引擎
  //    参数说明：-c 2048(上下文窗口) -t 4(线程数) --mlock(锁定内存防swap) --port 8082
  console.log('[A21] Starting llama-server...')
  spawnQuiet(
    path.join(rootPath, 'llama.cpp', 'llama-server.exe'),
    [
      '-m', path.join(modelPath, 'qwen2.5-1.5b-instruct-q4_k_m.gguf'),
      '-c', '2048', '-t', '4', '--host', '127.0.0.1', '--port', '8082', '--mlock'
    ],
    { label: 'llama' }
  )

  // 3. FastAPI 后端 — uvicorn (ASGI 服务器)
  //    NEO4J_PASSWORD 通过环境变量传入（TODO: 改为配置文件读取）
  //    VOSK_MODEL_DIR 指向本地模型目录
  console.log('[A21] Starting Backend...')
  const backendPath = path.join(rootPath, 'backend')
  spawnQuiet('python', [
    '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'
  ], {
    cwd: backendPath,
    env: {
      ...process.env,
      NEO4J_PASSWORD: 'a21password',  // TODO: 从配置文件读取，不要硬编码
      VOSK_MODEL_DIR: path.join(modelPath, 'vosk-model-small-cn-0.22'),
    },
    label: 'backend',
  })
  
  // 4. Vosk 语音识别 HTTP 服务（独立进程，端口 8765）
  spawnQuiet('python', ['tools/vosk_http.py'], {
    cwd: backendPath,
    label: 'vosk',
  })
}

/**
 * 生产模式：从 resources/ 目录启动预编译的可执行文件。
 * 
 * 打包后结构（由 electron-builder extraResources 配置）：
 *   resources/backend.exe
 *   resources/llama-server.exe
 *   resources/model/*.gguf
 *   resources/neo4j.bat + neo4j/
 */
function startPackaged() {
  spawnQuiet(path.join(rootPath, 'neo4j.bat'), [], { cwd: rootPath, label: 'neo4j' })
  spawnQuiet(path.join(rootPath, 'llama-server.exe'), [
    '-m', path.join(rootPath, 'model', 'model.gguf'),
    '-c', '2048', '-t', '4', '--host', '127.0.0.1', '--port', '8082', '--mlock'
  ], { label: 'llama' })
  spawnQuiet(path.join(rootPath, 'backend.exe'), [], { cwd: rootPath, label: 'backend' })
}

// ==================== 窗口管理 ====================

/**
 * 创建主窗口。
 * 
 * 窗口策略：
 *   - show: false — 先隐藏窗口，等服务就绪后再 show()，避免用户看到加载过程
 *   - ready-to-show 事件 — 页面加载完成后才触发，但这里手动控制 show 时机
 *   - 安全配置：contextIsolation(true) + nodeIntegration(false) + preload
 */
async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280, height: 800,
    minWidth: 900, minHeight: 600,
    title: 'A21 船舶故障诊断系统',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),  // 安全的 IPC 桥接
      contextIsolation: true,                        // 隔离渲染进程 Node.js 环境
      nodeIntegration: false,                        // 禁止渲染进程使用 require()
    },
    show: false,  // 等服务就绪再显示
  })

  // 加载前端页面
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')  // Vite 开发服务器
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))  // 打包产物
  }

  mainWindow.once('ready-to-show', () => mainWindow.show())
  mainWindow.on('closed', () => { mainWindow = null })
}

// ==================== IPC 通信 ====================

// 打开文件对话框（前端上传文档/导入知识包）
ipcMain.handle('dialog:openFile', async () => {
  const r = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: '文档', extensions: ['docx','pdf','txt'] },
      { name: '知识包', extensions: ['zip'] },
    ],
  })
  return r.canceled ? null : r.filePaths[0]
})

// 保存文件对话框（前端导出知识包/报告）
ipcMain.handle('dialog:saveFile', async (_, name) => {
  const r = await dialog.showSaveDialog(mainWindow, {
    defaultPath: name || 'export.zip',
    filters: [{ name: 'ZIP', extensions: ['zip'] }],
  })
  return r.canceled ? null : r.filePath
})

// ==================== 应用生命周期 ====================

app.whenReady().then(async () => {
  // 1. 启动所有后台服务
  startServices()

  // 2. 等待核心服务就绪（llama-server + FastAPI）
  try {
    console.log('[A21] Waiting for services...')
    if (isDev) {
      await Promise.all([
        waitForService('http://127.0.0.1:8082/health', 40),  // llama-server（40s 超时）
        waitForService('http://127.0.0.1:8000/health', 40),  // FastAPI 后端
      ])
    }
    console.log('[A21] Services ready!')
  } catch (e) {
    // 服务未就绪时不阻塞，允许窗口显示（用户可看到部分功能不可用）
    console.error('[A21] Some services may not be ready:', e.message)
  }

  // 3. 创建并加载窗口
  await createWindow()

  // 4. 开发模式下额外等待 Vite 就绪
  if (isDev) {
    try { await waitForService('http://localhost:5173', 20) } catch { console.error('[A21] Vite dev server not ready') }
  }

  // 5. 显示窗口（所有服务就绪后）
  mainWindow.show()
})

// 窗口全部关闭 → kill 所有子进程
app.on('window-all-closed', () => {
  processes.forEach(p => p.kill())
  if (process.platform !== 'darwin') app.quit()  // macOS 不自动退出（系统惯例）
})

// 应用退出前 → kill 所有子进程（双重保险）
app.on('before-quit', () => processes.forEach(p => p.kill()))

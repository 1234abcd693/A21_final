const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const http = require('http')

let mainWindow = null
const processes = []
const isDev = !app.isPackaged

// Project root path
const rootPath = isDev ? path.join(__dirname, '..', '..') : process.resourcesPath

function spawnQuiet(cmd, args, opts = {}) {
  const p = spawn(cmd, args, {
    windowsHide: true,
    stdio: 'pipe',
    ...opts,
  })
  p.stdout?.on('data', d => console.log(`[${opts.label||cmd}] ${d}`.trim()))
  p.stderr?.on('data', d => console.error(`[${opts.label||cmd}] ${d}`.trim()))
  processes.push(p)
  return p
}

function waitForService(url, maxRetries = 30) {
  return new Promise((resolve, reject) => {
    let tries = 0
    const check = () => {
      http.get(url, (res) => {
        if (res.statusCode === 200) resolve(true)
        else retry()
      }).on('error', retry)
    }
    const retry = () => {
      if (++tries >= maxRetries) reject(new Error(`Service ${url} not ready after ${maxRetries}s`))
      else setTimeout(check, 1000)
    }
    check()
  })
}

function startServices() {
  if (!isDev) return startPackaged()

  const modelPath = path.join(rootPath, 'model')

  // 1. Neo4j
  console.log('[A21] Starting Neo4j...')
  spawnQuiet('cmd', ['/c', 'cd', '/d', path.join(rootPath, 'neo4j', 'neo4j-community-2026.02.3', 'bin'), '&&', 'neo4j.bat', 'console'], { label: 'neo4j' })

  // 2. llama-server
  console.log('[A21] Starting llama-server...')
  spawnQuiet(
    path.join(rootPath, 'llama.cpp', 'llama-server.exe'),
    ['-m', path.join(modelPath, 'qwen2.5-1.5b-instruct-q4_k_m.gguf'), '-c', '2048', '-t', '4', '--host', '127.0.0.1', '--port', '8082', '--mlock'],
    { label: 'llama' }
  )

  // 3. Backend (FastAPI + Vosk bundled)
  console.log('[A21] Starting Backend...')
  const backendPath = path.join(rootPath, 'backend')
  spawnQuiet('python', ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
    cwd: backendPath,
    env: { ...process.env, NEO4J_PASSWORD: 'a21password', VOSK_MODEL_DIR: path.join(modelPath, 'vosk-model-small-cn-0.22') },
    label: 'backend',
  })
  
  // Vosk HTTP (separate process for reliability)
  spawnQuiet('python', ['tools/vosk_http.py'], {
    cwd: backendPath,
    label: 'vosk',
  })
}

function startPackaged() {
  // Production: all executables in resources/
  spawnQuiet(path.join(rootPath, 'neo4j.bat'), [], { cwd: rootPath, label: 'neo4j' })
  spawnQuiet(path.join(rootPath, 'llama-server.exe'), ['-m', path.join(rootPath, 'model', 'model.gguf'), '-c', '2048', '-t', '4', '--host', '127.0.0.1', '--port', '8082', '--mlock'], { label: 'llama' })
  spawnQuiet(path.join(rootPath, 'backend.exe'), [], { cwd: rootPath, label: 'backend' })
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280, height: 800, minWidth: 900, minHeight: 600,
    title: 'A21 船舶故障诊断系统',
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false },
    show: false, // 等服务就绪再显示
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  mainWindow.once('ready-to-show', () => mainWindow.show())
  mainWindow.on('closed', () => { mainWindow = null })
}

// IPC
ipcMain.handle('dialog:openFile', async () => {
  const r = await dialog.showOpenDialog(mainWindow, { properties: ['openFile'], filters: [{ name: '文档', extensions: ['docx','pdf','txt'] }, { name: '知识包', extensions: ['zip'] }] })
  return r.canceled ? null : r.filePaths[0]
})
ipcMain.handle('dialog:saveFile', async (_, name) => {
  const r = await dialog.showSaveDialog(mainWindow, { defaultPath: name || 'export.zip', filters: [{ name: 'ZIP', extensions: ['zip'] }] })
  return r.canceled ? null : r.filePath
})

app.whenReady().then(async () => {
  startServices()
  try {
    console.log('[A21] Waiting for services...')
    if (isDev) {
      await Promise.all([
        waitForService('http://127.0.0.1:8082/health', 40),
        waitForService('http://127.0.0.1:8000/health', 40),
      ])
    }
    console.log('[A21] Services ready!')
  } catch (e) {
    console.error('[A21] Some services may not be ready:', e.message)
  }
  await createWindow()
  // Wait for Vite in dev mode
  if (isDev) {
    try { await waitForService('http://localhost:5173', 20) } catch {}
  }
  mainWindow.show()
})

app.on('window-all-closed', () => {
  processes.forEach(p => p.kill())
  if (process.platform !== 'darwin') app.quit()
})
app.on('before-quit', () => processes.forEach(p => p.kill()))

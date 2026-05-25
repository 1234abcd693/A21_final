const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const { spawn } = require('child_process')
const path = require('path')

let mainWindow = null
let backendProcess = null

const isDev = !app.isPackaged

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'A21 船舶故障诊断智能问答系统',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
    if (backendProcess) {
      backendProcess.kill()
      backendProcess = null
    }
  })
}

function startBackend() {
  const resourcesPath = isDev
    ? path.join(__dirname, '..', '..', 'backend')
    : path.join(process.resourcesPath)

  const backendExe = isDev
    ? 'python'
    : path.join(resourcesPath, 'backend.exe')

  const backendArgs = isDev
    ? [path.join(resourcesPath, 'main.py')]
    : []

  // 启动 Python 后端
  backendProcess = spawn(backendExe, backendArgs, {
    cwd: resourcesPath,
    env: { ...process.env, NEO4J_PASSWORD: 'a21password' },
    stdio: 'pipe',
  })
  backendProcess.stdout?.on('data', (data) => console.log(`[backend] ${data}`))
  backendProcess.stderr?.on('data', (data) => console.error(`[backend] ${data}`))

  // 启动 whisper-server
  if (isDev) {
    const whisperPath = path.join(__dirname, '..', '..', 'whisper.cpp', 'Release')
    const modelPath = path.join(__dirname, '..', '..', 'model', 'ggml-base.bin')
    const whisperProcess = spawn(
      path.join(whisperPath, 'whisper-server.exe'),
      ['-m', modelPath, '--host', '127.0.0.1', '--port', '8081'],
      { stdio: 'pipe' },
    )
    whisperProcess.stdout?.on('data', (data) => console.log(`[whisper] ${data}`))
  }
}

// IPC: 打开文件对话框
ipcMain.handle('dialog:openFile', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: '文档', extensions: ['docx', 'pdf', 'txt'] },
      { name: '知识包', extensions: ['zip'] },
    ],
  })
  return result.canceled ? null : result.filePaths[0]
})

// IPC: 保存文件对话框
ipcMain.handle('dialog:saveFile', async (_, defaultName) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName || 'export.zip',
    filters: [{ name: 'ZIP', extensions: ['zip'] }],
  })
  return result.canceled ? null : result.filePath
})

app.whenReady().then(() => {
  startBackend()
  setTimeout(createWindow, 2000) // 等后端启动
})

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  if (backendProcess) backendProcess.kill()
})

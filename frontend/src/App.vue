<!--
  A21 船舶故障诊断系统 — 前端主组件（已拆分版）
  ============================================

  组件架构（2026-05-26 重构）：
  - LoginPage.vue    — 登录页（用户名/密码/错误提示）
  - SideMenu.vue     — 侧边栏（历史对话 + 用户条）
  - ChatPanel.vue    — 聊天消息区（欢迎页 + 消息气泡 + 流式光标）
  - MessageBubble.vue— 单条消息（用户/AI 样式 + Markdown + 反馈按钮）
  - InputBox.vue     — 输入框（文本 + 语音 + 发送 + 录音状态）
  - ProfileModal.vue — 个人设置弹窗（显示名/密码/保存/退出）

  状态管理：
  - 所有响应式状态集中在 App.vue 的 ref() 中
  - 通过 props 向下传递，通过 emits 向上通信
  - 未使用 Pinia/Vuex，适用于当前规模

  认证流程：
  - 登录成功 → localStorage 存 token + user 信息
  - 后续请求在 api/index.js 中自动携带 token
  - 退出时清除 localStorage，恢复登录页
-->

<template>
<div class="app">
  <!-- ==================== 登录页 ==================== -->
  <LoginPage
    v-if="!loggedIn"
    v-model:uname="uname"
    v-model:upass="upass"
    :loading="loading"
    :err="err"
    @login="doLogin"
  />

  <!-- ==================== 主界面（登录后） ==================== -->
  <div v-else class="main-layout">
    <!-- 侧边栏 -->
    <SideMenu
      :conversations="conversations"
      :active-id="activeId"
      :user-name="userName"
      @new-chat="newChat"
      @load-chat="loadChat"
      @del-conv="delConv"
      @toggle-profile="showProfile = !showProfile"
    />

    <!-- 聊天主区域 -->
    <main class="chat-area">
      <ChatPanel
        :messages="messages"
        :streaming="streaming"
        :thinking="thinking"
        :stream-text="streamText"
        @rate="rateMsg"
        @example-click="handleExampleClick"
      />
      <InputBox
        v-model="tx"
        :streaming="streaming"
        :recording="recording"
        :rec-time="recTime"
        @send="send"
        @toggle-voice="toggleVoice"
      />
    </main>

    <!-- 个人设置弹窗（Teleport 到 body，内部处理） -->
    <ProfileModal
      v-model="showProfile"
      v-model:disp-name="dispName"
      v-model:new-pass="newPass"
      @save="saveProfile"
      @logout="doLogout"
    />
  </div>
</div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import api, { askStream, feedbackAPI, authAPI, historyAPI } from './api/index.js'

import LoginPage from './components/LoginPage.vue'
import SideMenu from './components/SideMenu.vue'
import ChatPanel from './components/ChatPanel.vue'
import InputBox from './components/InputBox.vue'
import ProfileModal from './components/ProfileModal.vue'

// ==================== 认证状态 ====================
const loggedIn = ref(!!localStorage.getItem('a21_token'))
const uname = ref('admin')
const upass = ref('')
const loading = ref(false)
const err = ref('')
const userName = ref('')
const userId = ref(0)

// ==================== 聊天状态 ====================
const messages = ref([])
const tx = ref('')
const streaming = ref(false)
const streamText = ref('')
const thinking = ref(false)  // 检索中指示器

// 对话列表状态
const conversations = ref([])
const activeId = ref('')

// ==================== 语音输入状态 ====================
const recording = ref(false)
const recTime = ref(0)
let mediaRecorder = null
let chunks = []
let recTimer = null

// ==================== 个人设置状态 ====================
const showProfile = ref(false)
const dispName = ref('')
const newPass = ref('')

// ==================== 生命周期 ====================
onMounted(async () => {
  if (loggedIn.value) {
    try {
      const u = JSON.parse(localStorage.getItem('a21_user') || '{}')
      userName.value = u.display_name || u.username
      userId.value = u.id
      dispName.value = u.display_name || ''
    } catch {}
    loadConversations()
  }
})

// ==================== 认证逻辑 ====================
async function doLogin() {
  if (!uname.value || !upass.value) return
  loading.value = true; err.value = ''
  try {
    const { data } = await authAPI.login({ username: uname.value, password: upass.value })
    localStorage.setItem('a21_token', data.token)
    localStorage.setItem('a21_user', JSON.stringify(data.user))
    loggedIn.value = true
    userName.value = data.user.display_name
    userId.value = data.user.id
    loadConversations()
  } catch (e) { err.value = '登录失败' }
  finally { loading.value = false }
}

function doLogout() {
  localStorage.clear()
  loggedIn.value = false
  messages.value = []
}

// ==================== 历史对话管理 ====================
async function loadConversations() {
  try {
    const { data } = await historyAPI.list({ page: 1, page_size: 100 })
    conversations.value = (data.sessions || []).map(s => ({ id: s.session_id, title: s.title }))
  } catch {}
}

function newChat() {
  messages.value = []
  activeId.value = 'sess_' + Date.now()
  streamText.value = ''
  loadConversations()
}

async function loadChat(id) {
  activeId.value = id
  try {
    const { data } = await historyAPI.detail(id)
    messages.value = (data.messages || []).map(m => ({
      id: m.message_id,
      role: m.role,
      content: m.content,
      _rating: 0
    }))
  } catch {}
}

async function delConv(id) {
  try {
    await historyAPI.delete(id)
    if (activeId.value === id) { messages.value = []; activeId.value = '' }
    loadConversations()
  } catch {}
}

async function saveConv(q, a) {
  if (!activeId.value) return
  try {
    await api.post('/history/save', {
      session_id: activeId.value,
      title: q.slice(0, 40),
      user_msg: q,
      assistant_msg: a,
      user_id: userId.value
    })
  } catch {}
  loadConversations()
}

// ==================== 聊天核心逻辑 ====================

// 发送消息（接受可选的 text 参数，用于 InputBox 直接传入）
async function send(text) {
  const q = text || tx.value.trim()
  if (!q || streaming.value) return

  tx.value = ''

  messages.value.push({ role: 'user', content: q, _rating: 0 })
  streaming.value = true
  thinking.value = true
  streamText.value = ''
  await nextTick()

  try {
    const hist = messages.value.slice(-6).map(m => ({ role: m.role, content: m.content }))

    const r = await askStream(q, { mode: 'chat', session_id: activeId.value, history: hist })

    const d = new TextDecoder()
    let b = ''
    while (true) {
      const { done, value } = await r.read()
      if (done) break
      b += d.decode(value, { stream: true })
      const ls = b.split('\n')
      b = ls.pop() || ''
      for (const l of ls) {
        // 处理 SSE event 行（状态事件）
        if (l.startsWith('event: status')) {
          // status events: thinking, done
          continue
        }
        // 处理 data 行（token 数据，JSON 编码）
        if (l.startsWith('data: ')) {
          const raw = l.slice(6)
          // 跳过状态事件
          if (raw === 'thinking') continue
          // 跳过 metadata JSON（以 { 或 [ 开头）
          if (raw.startsWith('{') || raw.startsWith('[')) continue
          // JSON 解码 token（保留 \n 等特殊字符）
          try {
            streamText.value += JSON.parse(raw)
          } catch {
            // 兼容旧格式：直接拼接
            streamText.value += raw
          }
          thinking.value = false
        }
      }
    }

    // SSE 流结束：如果流中没有完整回答（metadata 事件流跳过），用 streamText
    const finalAnswer = streamText.value
    messages.value.push({ role: 'assistant', content: finalAnswer, _rating: 0 })
    saveConv(q, finalAnswer)
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '抱歉，生成回答时出错。', _rating: 0 })
  } finally {
    streaming.value = false
    thinking.value = false
    streamText.value = ''
  }
}

// 欢迎页示例问题点击处理
function handleExampleClick(ex) {
  tx.value = ex
  send()
}

// ==================== 语音输入逻辑 ====================
async function toggleVoice() {
  if (recording.value) {
    stopVoice()
    return
  }
  try {
    const s = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(s)
    chunks = []
    recording.value = true
    recTime.value = 0
    recTimer = setInterval(() => recTime.value++, 1000)

    mediaRecorder.ondataavailable = e => chunks.push(e.data)
    mediaRecorder.onstop = async () => {
      clearInterval(recTimer)
      recording.value = false
      s.getTracks().forEach(t => t.stop())
      try {
        const b = new Blob(chunks, { type: 'audio/webm' })
        const fd = new FormData()
        fd.append('audio', b)
        const { data } = await api.post('http://127.0.0.1:8765/transcribe', fd, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        if (data.text) tx.value = data.text
      } catch {}
    }
    mediaRecorder.start()
  } catch (e) {
    recording.value = false
  }
}

function stopVoice() {
  if (mediaRecorder && mediaRecorder.state === 'recording') mediaRecorder.stop()
}

// ==================== 反馈逻辑 ====================
async function rateMsg(m, v) {
  m._rating = m._rating === v ? 0 : v
  try {
    await feedbackAPI.submit({
      message_id: m.id || '',
      rating: v,
      question: '',
      answer_text: m.content,
      retrieved_chunks: '[]'
    })
  } catch {}
}

// ==================== 个人设置逻辑 ====================
async function saveProfile() {
  try {
    await api.put('/user/profile', {
      display_name: dispName.value,
      password: newPass.value || undefined
    }, { params: { token: localStorage.getItem('a21_token') } })
    alert('已保存')
    showProfile.value = false
  } catch {}
}
</script>

<style>
/* CSS 变量：全局暗色主题配色（DeepSeek 风格） */
:root {
  --bg: #1A1A2E;
  --sb: #16213E;
  --card: #0F3460;
  --accent: #533483;
  --text: #E0E0E0;
  --sub: #888;
  --border: #2A2A4A;
}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg);
  color: var(--text);
  overflow: hidden;
}
.app {
  height: 100vh;
}

/* 主布局 */
.main-layout {
  display: flex;
  height: 100vh;
}

/* 聊天区容器 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
}

/* 共享输入框样式（LoginPage + ProfileModal 共用） */
.inp {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: #fff;
  font-size: 15px;
  outline: none;
  margin-bottom: 12px;
}
.inp:focus {
  border-color: var(--accent);
}

/* 错误提示（LoginPage 使用） */
.err {
  color: #EF4444;
  font-size: 13px;
  margin-top: 8px;
}
</style>

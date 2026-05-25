<template>
  <div :class="['chat-panel', { collapsed }]">
    <div class="chat-header" @click="collapsed = !collapsed">
      <span>💬 智能问答</span>
      <button class="close-btn" @click.stop="$emit('close')">✕</button>
    </div>
    <div v-show="!collapsed" class="chat-body">
      <div class="messages" ref="msgList">
        <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
          <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
          <div class="bubble">
            <div class="text">{{ msg.content }}</div>
            <div v-if="msg.citations?.length" class="citations">
              引用:
              <span v-for="c in msg.citations" :key="c.num" class="cite" :title="`${c.doc_name} ${c.page}`">[{{ c.num }}] {{ c.doc_name }}</span>
            </div>
            <details v-if="msg.traceability" class="trace-card">
              <summary>🟢🟡🔴 可信度: {{ label(msg.traceability.confidence) }}</summary>
              <div v-for="c in msg.citations" :key="c.num" class="trace-item">
                <strong>[{{ c.num }}]</strong> {{ c.doc_name }} — {{ c.page }}
              </div>
            </details>
            <div v-if="msg.role === 'assistant' && msg.messageId" class="feedback">
              <button :class="{ active: msg._rating === 1 }" @click="rate(msg, 1)">👍</button>
              <button :class="{ active: msg._rating === -1 }" @click="rate(msg, -1)">👎</button>
            </div>
          </div>
        </div>
        <div v-if="streaming" class="streaming">🤖 {{ streamingText }}<span class="cursor">|</span></div>
      </div>
      <div class="input-row">
        <textarea v-model="text" placeholder="输入故障现象..." @keydown.enter.exact.prevent="send" :disabled="streaming" rows="2" />
        <button @mousedown.prevent="startVoice" @mouseup.prevent="stopVoice" class="voice-btn" title="按住说话">🎤</button>
        <button @click="send" :disabled="streaming || !text.trim()" class="send-btn">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import api, { askStream, feedbackAPI, transcribeAPI } from '../api/index.js'

const emit = defineEmits(['close', 'messageSent'])
const collapsed = ref(false), messages = ref([]), streaming = ref(false), streamingText = ref(''), text = ref(''), msgList = ref(null)

function label(c) { return c === 'green' ? '可信' : c === 'yellow' ? '部分可信' : '不可信' }

async function send() {
  if (!text.value.trim() || streaming.value) return
  const q = text.value.trim(); text.value = ''
  messages.value.push({ id: Date.now(), role: 'user', content: q })
  streaming.value = true; streamingText.value = ''; await nextTick(); scroll()

  try {
    const reader = await askStream(q, { mode: 'chat' })
    const dec = new TextDecoder(); let buffer = '', meta = null
    while (true) {
      const { done, value } = await reader.read(); if (done) break
      buffer += dec.decode(value, { stream: true })
      const lines = buffer.split('\n'); buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) { streamingText.value += line.slice(6); scroll() }
        else if (line.startsWith('event: metadata')) {
          try { meta = JSON.parse(lines.find(l => l.startsWith('data: '))?.slice(6) || '{}') } catch {}
        }
      }
    }
    messages.value.push({ id: Date.now() + 1, role: 'assistant', content: streamingText.value, citations: meta?.citations || [], traceability: meta?.traceability || {}, messageId: meta?.message_id || '' })
    emit('messageSent')
  } catch (e) {
    messages.value.push({ id: Date.now() + 1, role: 'assistant', content: `[错误: ${e.message}]`, citations: [] })
  } finally { streaming.value = false; streamingText.value = '' }
}

async function rate(msg, v) {
  msg._rating = msg._rating === v ? 0 : v
  const q = messages.value.find(m => m.role === 'user' && m.id < msg.id)?.content || ''
  feedbackAPI.submit({ message_id: msg.messageId, rating: msg._rating, question: q, answer_text: msg.content, retrieved_chunks: JSON.stringify(msg.citations || []) }).catch(() => {})
}

let recorder, chunks
async function startVoice() { try { const s = await navigator.mediaDevices.getUserMedia({ audio: true }); recorder = new MediaRecorder(s); chunks = []; recorder.ondataavailable = e => chunks.push(e.data); recorder.onstop = async () => { const b = new Blob(chunks, { type: 'audio/wav' }); const { data } = await transcribeAPI.send(b); if (data.text) text.value = data.text }; recorder.start() } catch {} }
function stopVoice() { if (recorder?.state !== 'inactive') { recorder.stop(); recorder.stream.getTracks().forEach(t => t.stop()) } }
function scroll() { nextTick(() => { if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight }) }
</script>

<style scoped>
.chat-panel { border-top: 3px solid #FFE76F; background: #fff; max-height: 420px; transition: max-height 0.3s; }
.chat-panel.collapsed { max-height: 40px; }
.chat-header { padding: 8px 16px; background: #F0F4FF; cursor: pointer; display: flex; justify-content: space-between; align-items: center; color: #002EA6; font-weight: 600; }
.close-btn { background: none; border: none; cursor: pointer; font-size: 16px; color: #999; }
.chat-body { display: flex; flex-direction: column; height: 380px; }
.messages { flex: 1; overflow-y: auto; padding: 12px 16px; }
.message { display: flex; gap: 8px; margin-bottom: 14px; }
.message.user { flex-direction: row-reverse; }
.avatar { font-size: 22px; flex-shrink: 0; }
.bubble { max-width: 80%; padding: 10px 14px; border-radius: 12px; background: #F5F7FA; }
.user .bubble { background: #002EA6; color: #fff; }
.text { white-space: pre-wrap; word-break: break-word; font-size: 14px; line-height: 1.5; }
.citations { margin-top: 8px; font-size: 11px; opacity: 0.7; }
.cite { cursor: pointer; margin-right: 6px; }
.user .cite { color: #FFE76F; }
.streaming { padding: 8px 16px; color: #002EA6; }
.cursor { animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0; } }
.trace-card { margin-top: 6px; padding: 6px 10px; background: #FFFDF0; border-radius: 6px; font-size: 12px; }
.trace-card summary { cursor: pointer; color: #B8860B; }
.input-row { display: flex; gap: 8px; padding: 10px 16px; border-top: 1px solid #F0F0F0; align-items: flex-end; }
textarea { flex: 1; padding: 10px 14px; border: 2px solid #E8ECF1; border-radius: 10px; resize: none; outline: none; font-size: 14px; }
textarea:focus { border-color: #002EA6; }
.voice-btn { padding: 8px 12px; border: 2px solid #E8ECF1; border-radius: 10px; background: #fff; cursor: pointer; font-size: 18px; }
.send-btn { padding: 10px 22px; border: none; border-radius: 10px; background: linear-gradient(135deg, #002EA6, #0040D0); color: #fff; cursor: pointer; font-weight: 600; }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.feedback { margin-top: 8px; display: flex; gap: 6px; }
.feedback button { padding: 4px 10px; border: 2px solid #E8ECF1; border-radius: 6px; background: #fff; cursor: pointer; font-size: 14px; }
.feedback button.active { border-color: #FFE76F; background: #FFFDF0; }
.user .feedback button { border-color: rgba(255,255,255,0.3); background: transparent; color: #fff; }
.user .feedback button.active { border-color: #FFE76F; }
</style>

<template>
  <div class="chat-panel" :class="{ collapsed }">
    <div class="chat-header" @click="collapsed = !collapsed">
      <span>💬 问答面板</span>
      <button class="close-btn" @click.stop="$emit('close')">✕</button>
    </div>
    <div v-show="!collapsed" class="chat-body">
      <div class="messages" ref="msgList">
        <MessageBubble
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
          @feedback="onFeedback"
        />
        <div v-if="streaming" class="streaming">🤖 {{ streamingText }}</div>
      </div>
      <InputBox
        :loading="streaming"
        @send="onSend"
        @voice="onVoice"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'
import InputBox from './InputBox.vue'
import { askStream } from '../api/index.js'

const props = defineProps({
  sessionId: String,
  contextNodes: Array,
})
const emit = defineEmits(['close', 'messageSent'])

const collapsed = ref(false)
const messages = ref([])
const streaming = ref(false)
const streamingText = ref('')
const msgList = ref(null)

async function onSend(text) {
  const userMsg = { id: Date.now(), role: 'user', content: text }
  messages.value.push(userMsg)
  streaming.value = true
  streamingText.value = ''
  await nextTick()
  scrollBottom()

  try {
    const reader = await askStream(text, {
      mode: 'chat',
      session_id: props.sessionId,
      context_nodes: props.contextNodes,
      history: messages.value.slice(-6),
    })
    const decoder = new TextDecoder()
    let buffer = ''
    let metadata = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const token = line.slice(6)
          streamingText.value += token
          scrollBottom()
        } else if (line.startsWith('event: metadata')) {
          // metadata 在下一行
        }
      }
    }

    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: streamingText.value,
      citations: metadata?.citations || [],
      traceability: metadata?.traceability || {},
      messageId: metadata?.message_id || '',
    })
    emit('messageSent')
  } catch (e) {
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: `[错误: ${e.message}]`,
      citations: [],
    })
  } finally {
    streaming.value = false
    streamingText.value = ''
  }
}

function onFeedback(msgId, rating) {
  const msg = messages.value.find(m => m.messageId === msgId)
  import('../api/index.js').then(({ feedbackAPI }) => {
    feedbackAPI.submit({
      message_id: msgId,
      rating,
      question: messages.value.find(m => m.role === 'user' && m.id < msg.id)?.content || '',
      answer_text: msg?.content || '',
      retrieved_chunks: JSON.stringify(msg?.citations || []),
    })
  })
}

async function onVoice(audioBlob) {
  const { transcribeAPI } = await import('../api/index.js')
  const { data } = await transcribeAPI.send(audioBlob)
  return data.text || ''
}

function scrollBottom() {
  nextTick(() => {
    if (msgList.value) {
      msgList.value.scrollTop = msgList.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-panel { border-top: 2px solid #1890ff; background: #fff; max-height: 420px; transition: all 0.3s; }
.chat-panel.collapsed { max-height: 40px; }
.chat-header { padding: 8px 16px; background: #f0f5ff; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.close-btn { background: none; border: none; cursor: pointer; font-size: 16px; }
.chat-body { display: flex; flex-direction: column; height: 380px; }
.messages { flex: 1; overflow-y: auto; padding: 12px; }
.streaming { padding: 8px 12px; color: #666; }
</style>

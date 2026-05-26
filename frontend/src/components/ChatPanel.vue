<template>
  <div class="messages" ref="msgRef">
    <!-- Welcome screen -->
    <div v-if="!messages.length && !streaming" class="welcome">
      <h2>船舶故障智能诊断</h2>
      <p>输入故障现象，获取维修建议</p>
      <div class="examples">
        <button
          v-for="ex in examples"
          :key="ex"
          @click="$emit('example-click', ex)"
          class="ex-btn"
        >{{ ex }}</button>
      </div>
    </div>

    <!-- Message list -->
    <MessageBubble
      v-for="(m, i) in messages"
      :key="i"
      :message="m"
      @rate="(msg, val) => $emit('rate', msg, val)"
    />

    <!-- Thinking indicator (shown during retrieval, before first token) -->
    <div v-if="thinking && !streamText" class="thinking-indicator">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      <span class="thinking-text">正在检索知识库…</span>
    </div>

    <!-- Streaming message -->
    <div v-if="streaming" class="msg assistant">
      <div class="msg-content" v-html="renderedStream"></div>
      <span class="cursor">▊</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { marked } from 'marked'
import MessageBubble from './MessageBubble.vue'

marked.setOptions({ breaks: true, gfm: true })

const props = defineProps({
  messages: { type: Array, default: () => [] },
  streaming: { type: Boolean, default: false },
  thinking: { type: Boolean, default: false },
  streamText: { type: String, default: '' }
})

const emit = defineEmits(['rate', 'example-click'])
const msgRef = ref(null)

const examples = [
  '接触器线圈烧毁怎么修？',
  '电动机不能起动怎么办？',
  '发电机电压异常的原因'
]

// 流式渲染：用 marked 实时渲染
const renderedStream = computed(() => {
  const text = props.streamText || ''
  const cleaned = text.replace(/^\s*\[\d+\]\s*/gm, '')
  // marked v5+ 需要 async: false 才能同步返回
  try {
    const html = marked.parse(cleaned, { breaks: true, gfm: true, async: false })
    return typeof html === 'string' ? html : (cleaned.replace(/\n/g, '<br>'))
  } catch {
    return cleaned.replace(/\n/g, '<br>')
  }
})

function scrollBottom() {
  nextTick(() => {
    if (msgRef.value) {
      msgRef.value.scrollTop = msgRef.value.scrollHeight
    }
  })
}

watch(() => props.messages.length, () => scrollBottom())
watch(() => props.streamText, () => scrollBottom())
</script>

<style scoped>
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
}
.welcome {
  text-align: center;
  padding: 80px 20px;
}
.welcome h2 {
  font-size: 24px;
  color: #fff;
  margin-bottom: 8px;
}
.welcome p {
  color: var(--sub);
  font-size: 15px;
  margin-bottom: 24px;
}
.examples {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.ex-btn {
  padding: 10px 18px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  cursor: pointer;
  font-size: 13px;
  transition: all .2s;
}
.ex-btn:hover {
  background: rgba(83,52,131,0.2);
  border-color: var(--accent);
}
.msg {
  margin-bottom: 28px;
  padding: 0 4px;
}
.msg-content {
  max-width: 85%;
  padding: 14px 20px;
  border-radius: 16px;
  background: rgba(255,255,255,0.04);
  line-height: 1.7;
  font-size: 15px;
  color: var(--text);
}
/* Stream markdown styling — report quality */
.msg-content :deep(h2) {
  font-size: 20px;
  font-weight: 700;
  margin: 20px 0 12px;
  color: #fff;
  border-bottom: 2px solid var(--accent);
  padding-bottom: 8px;
  line-height: 1.3;
}
.msg-content :deep(h3) {
  font-size: 17px;
  font-weight: 600;
  margin: 16px 0 10px;
  color: #e0e0e0;
}
.msg-content :deep(strong) {
  font-weight: 700;
  color: #fff;
}
.msg-content :deep(ol), .msg-content :deep(ul) {
  margin: 10px 0;
  padding-left: 26px;
}
.msg-content :deep(li) {
  margin: 6px 0;
  line-height: 1.7;
}
.msg-content :deep(p) {
  margin: 10px 0;
  line-height: 1.8;
}
.msg-content :deep(code) {
  background: rgba(255,255,255,0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
.msg-content :deep(pre) {
  background: rgba(0,0,0,0.3);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}
.cursor {
  animation: blink 1s infinite;
  color: var(--accent);
  font-size: 20px;
  margin-left: 4px;
}
@keyframes blink {
  50% { opacity: 0; }
}

/* Thinking indicator */
.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 20px;
  margin-bottom: 28px;
}
.thinking-indicator .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: dotBounce 1.4s infinite;
}
.thinking-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-indicator .dot:nth-child(3) { animation-delay: 0.4s; }
.thinking-text {
  color: var(--sub);
  font-size: 14px;
  margin-left: 8px;
}
@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
</style>

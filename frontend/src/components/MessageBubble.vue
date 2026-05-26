<template>
  <div :class="['msg', message.role]">
    <div class="msg-content" v-html="renderedContent"></div>
    <div class="msg-actions" v-if="message.role==='assistant'">
      <button @click="rate(1)" :class="{active:message._rating===1}">👍</button>
      <button @click="rate(-1)" :class="{active:message._rating===-1}">👎</button>
      <button @click="copyContent" :class="{ copied }" title="复制回答">
        {{ copied ? '✓ 已复制' : '📋 复制' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { marked } from 'marked'

// 配置 marked：安全渲染（不解析 HTML），支持 GFM 表格和换行
marked.setOptions({
  breaks: true,
  gfm: true,
})

const props = defineProps({
  message: { type: Object, required: true }
})

const emit = defineEmits(['rate'])
const copied = ref(false)

function rate(v) {
  emit('rate', props.message, v)
}

async function copyContent() {
  try {
    await navigator.clipboard.writeText(props.message.content)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  } catch {
    // fallback: select and copy
    const el = document.createElement('textarea')
    el.value = props.message.content
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  }
}

const renderedContent = computed(() => {
  const raw = props.message.content || ''
  if (props.message.role === 'user') {
    return raw.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
  try {
    const html = marked.parse(raw, { breaks: true, gfm: true, async: false })
    return typeof html === 'string' ? html : raw.replace(/\n/g, '<br>').replace(/</g, '&lt;')
  } catch {
    return raw.replace(/\n/g, '<br>').replace(/</g, '&lt;')
  }
})
</script>

<style scoped>
.msg {
  margin-bottom: 28px;
  padding: 0 4px;
}
.msg.user {
  display: flex;
  justify-content: flex-end;
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
.msg.user .msg-content {
  background: var(--accent);
  max-width: 65%;
}
/* Markdown rendered styles — report quality */
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
.msg-content :deep(pre code) {
  background: none;
  padding: 0;
}
.msg-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  padding-left: 4px;
}
.msg-actions button {
  padding: 4px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: transparent;
  color: var(--sub);
  cursor: pointer;
  font-size: 12px;
  transition: all .2s;
}
.msg-actions button:hover {
  border-color: var(--accent);
}
.msg-actions button.active {
  border-color: #FFE76F;
  color: #FFE76F;
}
.msg-actions button.copied {
  border-color: #22C55E;
  color: #22C55E;
}
</style>

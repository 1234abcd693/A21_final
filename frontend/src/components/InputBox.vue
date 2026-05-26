<template>
  <div class="input-wrapper">
    <div class="input-area">
      <textarea
        :value="modelValue"
        @input="onInput"
        @keydown.enter.exact.prevent="onSend"
        :disabled="streaming"
        rows="1"
        ref="txRef"
        placeholder="输入故障现象..."
      />
      <button
        @click="$emit('toggle-voice')"
        :class="['voice-btn', { recording }]"
      >
        {{ recording ? '⏹' : '🎤' }}
      </button>
      <button
        @click="onSend"
        :disabled="streaming || !modelValue.trim()"
        class="send-btn"
      >↑</button>
    </div>
    <div v-if="recording" class="rec-bar">
      🔴 录音中 {{ recTime }}s — 点击⏹停止
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  streaming: { type: Boolean, default: false },
  recording: { type: Boolean, default: false },
  recTime: { type: Number, default: 0 }
})

const emit = defineEmits(['update:modelValue', 'send', 'toggle-voice'])

const txRef = ref(null)

function onInput(e) {
  emit('update:modelValue', e.target.value)
  autoResize()
}

function onSend() {
  if (!props.modelValue.trim() || props.streaming) return
  emit('send', props.modelValue.trim())
}

function autoResize() {
  const el = txRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

watch(() => props.modelValue, (val) => {
  nextTick(() => {
    if (txRef.value) {
      if (!val) {
        txRef.value.style.height = 'auto'
      } else {
        txRef.value.style.height = 'auto'
        txRef.value.style.height = Math.min(txRef.value.scrollHeight, 120) + 'px'
      }
    }
  })
})
</script>

<style scoped>
.input-wrapper {
  position: relative;
}
.input-area {
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  align-items: flex-end;
}
textarea {
  flex: 1;
  padding: 14px 18px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 14px;
  resize: none;
  outline: none;
  font-size: 15px;
  color: var(--text);
  line-height: 1.5;
  font-family: inherit;
  max-height: 120px;
}
textarea:focus {
  border-color: var(--accent);
}
.voice-btn {
  width: 42px;
  height: 42px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: transparent;
  color: var(--sub);
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all .2s;
}
.voice-btn:hover {
  background: rgba(255,255,255,0.04);
}
.voice-btn.recording {
  background: #EF4444;
  color: #fff;
  border-color: #EF4444;
}
.send-btn {
  width: 42px;
  height: 42px;
  border: none;
  border-radius: 12px;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all .2s;
}
.send-btn:hover {
  opacity: .9;
}
.send-btn:disabled {
  opacity: .3;
  cursor: not-allowed;
}
.rec-bar {
  position: fixed;
  bottom: 90px;
  left: 50%;
  transform: translateX(-50%);
  background: #EF4444;
  color: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 13px;
  z-index: 99;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
</style>

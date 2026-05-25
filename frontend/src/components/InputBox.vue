<template>
  <div class="input-box">
    <div class="input-row">
      <textarea
        v-model="text"
        placeholder="输入故障现象..."
        @keydown.enter.exact.prevent="send"
        @keydown.enter.shift.exact="() => {}"
        :disabled="loading"
        rows="2"
      />
      <button
        @mousedown.prevent="startVoice"
        @mouseup.prevent="stopVoice"
        class="voice-btn"
        title="按住说话"
      >🎤</button>
      <button @click="send" :disabled="loading || !text.trim()" class="send-btn">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({ loading: Boolean })
const emit = defineEmits(['send', 'voice'])
const text = ref('')

function send() {
  if (text.value.trim() && !props.loading) {
    emit('send', text.value.trim())
    text.value = ''
  }
}

let mediaRecorder = null
let chunks = []

async function startVoice() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    chunks = []
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/wav' })
      const result = await emit('voice', blob)
      if (result) text.value = result
    }
    mediaRecorder.start()
  } catch (e) {
    console.error('录音失败:', e)
  }
}

function stopVoice() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(t => t.stop())
  }
}
</script>

<style scoped>
.input-box { padding: 10px 16px; border-top: 1px solid #f0f0f0; }
.input-row { display: flex; gap: 8px; align-items: flex-end; }
textarea { flex: 1; padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 8px; resize: none; outline: none; font-size: 14px; }
.voice-btn { padding: 8px 12px; border: 1px solid #d9d9d9; border-radius: 8px; background: #fff; cursor: pointer; font-size: 18px; }
.send-btn { padding: 8px 20px; border: none; border-radius: 8px; background: #1890ff; color: #fff; cursor: pointer; }
.send-btn:disabled { background: #d9d9d9; cursor: not-allowed; }
</style>

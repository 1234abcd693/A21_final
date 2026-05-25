<template>
  <div :class="['message', role]">
    <div class="avatar">{{ role === 'user' ? '👤' : '🤖' }}</div>
    <div class="bubble">
      <div class="text">{{ message.content }}</div>
      <div v-if="message.citations?.length" class="citations">
        引用:
        <span
          v-for="c in message.citations"
          :key="c.num"
          class="cite"
          :title="`${c.doc_name} ${c.page}`"
        >
          [{{ c.num }}] {{ c.doc_name }}
        </span>
      </div>
      <TraceCard
        v-if="message.traceability"
        :traceability="message.traceability"
        :citations="message.citations"
      />
      <FeedbackButtons
        v-if="role === 'assistant' && message.messageId"
        @rate="(r) => $emit('feedback', message.messageId, r)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import FeedbackButtons from './FeedbackButtons.vue'
import TraceCard from './TraceCard.vue'

const props = defineProps({ message: Object })
defineEmits(['feedback'])
const role = computed(() => props.message.role)
</script>

<style scoped>
.message { display: flex; gap: 10px; margin-bottom: 16px; }
.message.user { flex-direction: row-reverse; }
.avatar { font-size: 24px; }
.bubble { max-width: 75%; padding: 10px 14px; border-radius: 12px; background: #f5f5f5; }
.user .bubble { background: #1890ff; color: #fff; }
.text { white-space: pre-wrap; word-break: break-word; }
.citations { margin-top: 8px; font-size: 12px; opacity: 0.7; }
.cite { color: #1890ff; cursor: pointer; margin-right: 8px; }
.user .cite { color: #fff; }
</style>

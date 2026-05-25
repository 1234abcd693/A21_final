<template>
  <div class="feedback">
    <button :class="{ active: current === 1 }" @click="rate(1)">👍</button>
    <button :class="{ active: current === -1 }" @click="rate(-1)">👎</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const emit = defineEmits(['rate'])
const current = ref(0)

function rate(v) {
  if (current.value === v) { current.value = 0; emit('rate', 0) }
  else { current.value = v; emit('rate', v) }
}
</script>

<style scoped>
.feedback { margin-top: 8px; display: flex; gap: 8px; }
.feedback button { padding: 4px 10px; border: 1px solid #d9d9d9; border-radius: 6px; background: #fff; cursor: pointer; font-size: 16px; }
.feedback button.active { border-color: #1890ff; background: #e6f7ff; transform: scale(1.15); }
</style>

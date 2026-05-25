<template>
  <div class="topbar">
    <div class="logo">A21 船舶故障诊断系统</div>
    <div class="search-box">
      <input
        v-model="query"
        placeholder="搜索实体、故障、关键词..."
        @keyup.enter="onSearch"
      />
      <button @click="onSearch">🔍</button>
    </div>
    <div class="actions">
      <button @click="$emit('toggleChat')" title="问答面板">💬</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const query = ref('')
const emit = defineEmits(['search', 'toggleChat'])

function onSearch() {
  if (query.value.trim()) {
    emit('search', query.value.trim())
  }
}
</script>

<style scoped>
.topbar {
  display: flex; align-items: center; padding: 10px 16px;
  background: #001529; color: #fff; gap: 16px;
}
.logo { font-size: 18px; font-weight: bold; white-space: nowrap; }
.search-box { flex: 1; display: flex; max-width: 500px; }
.search-box input {
  flex: 1; padding: 6px 12px; border: none; border-radius: 4px 0 0 4px; outline: none;
}
.search-box button {
  padding: 6px 12px; border: none; border-radius: 0 4px 4px 0; background: #1890ff; color: #fff; cursor: pointer;
}
.actions button {
  background: transparent; border: 1px solid #fff3; color: #fff;
  padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 16px;
}
</style>

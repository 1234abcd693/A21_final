<template>
  <div class="history-panel">
    <div class="panel-header">
      <h3>📜 历史对话</h3>
      <span v-if="selected.size" class="batch-bar">
        已选 {{ selected.size }} 项
        <button @click="batchDelete" class="btn-batch">🗑 删除</button>
      </span>
    </div>

    <div class="search-box">
      <input v-model="searchQuery" placeholder="搜索会话..." @input="onSearch" />
    </div>

    <div class="list">
      <div v-for="s in sessions" :key="s.session_id"
           :class="['item', { pinned: s.pinned, selected: selected.has(s.session_id) }]">
        <input type="checkbox" :checked="selected.has(s.session_id)" @change="toggleSelect(s.session_id)" class="cb" />
        <div class="content" @click="$emit('select', s)">
          <div class="title-row">
            <span v-if="s.pinned" class="pin">📌</span>
            <span class="title">{{ s.title }}</span>
          </div>
          <div class="meta">{{ s.message_count }} 条消息 · {{ formatTime(s.updated_at) }}</div>
        </div>
        <div class="actions">
          <button @click.stop="togglePin(s)" :title="s.pinned ? '取消置顶' : '置顶'">{{ s.pinned ? '📌' : '📍' }}</button>
          <button @click.stop="deleteSession(s.session_id)" title="删除">🗑</button>
        </div>
      </div>
      <div v-if="!sessions.length" class="empty">暂无历史对话</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { historyAPI } from '../api/index.js'

const emit = defineEmits(['select', 'close'])
const sessions = ref([])
const searchQuery = ref('')
const selected = ref(new Set())
let timer = null

onMounted(fetchAll)

function fetchAll() {
  const params = { page: 1, page_size: 50 }
  if (searchQuery.value) {
    historyAPI.search({ q: searchQuery.value, page: 1, page_size: 50 }).then(({ data }) => sessions.value = data.sessions || [])
  } else {
    historyAPI.list(params).then(({ data }) => sessions.value = data.sessions || [])
  }
}

function onSearch() {
  clearTimeout(timer); timer = setTimeout(fetchAll, 300)
}

async function deleteSession(sid) {
  await historyAPI.delete(sid); fetchAll()
}

async function togglePin(s) {
  await historyAPI.pin(s.session_id, !s.pinned); fetchAll()
}

async function batchDelete() {
  await historyAPI.batchDelete([...selected.value]); selected.value.clear(); fetchAll()
}

function toggleSelect(sid) {
  const s = new Set(selected.value)
  s.has(sid) ? s.delete(sid) : s.add(sid)
  selected.value = s
}

function formatTime(t) { return t ? t.slice(0, 16).replace('T', ' ') : '' }
</script>

<style scoped>
.history-panel { width: 360px; background: #fff; border-right: 1px solid #E8ECF1; display: flex; flex-direction: column; height: 100%; }
.panel-header { padding: 16px 20px; border-bottom: 1px solid #E8ECF1; display: flex; justify-content: space-between; align-items: center; }
.panel-header h3 { font-size: 16px; color: #002EA6; }
.batch-bar { font-size: 12px; color: #FF4D4F; }
.btn-batch { background: #FF4D4F; color: #fff; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; }
.search-box { padding: 12px 16px; border-bottom: 1px solid #E8ECF1; }
.search-box input { width: 100%; padding: 10px 14px; border: 2px solid #E8ECF1; border-radius: 8px; font-size: 13px; outline: none; }
.search-box input:focus { border-color: #002EA6; }
.list { flex: 1; overflow-y: auto; }
.item { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid #F5F7FA; cursor: pointer; transition: background 0.15s; }
.item:hover { background: #F0F4FF; }
.item.pinned { background: #FFFDF0; }
.item.selected { background: #E8F0FF; }
.cb { margin-right: 10px; }
.content { flex: 1; min-width: 0; }
.title-row { display: flex; align-items: center; gap: 4px; }
.title { font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pin { font-size: 12px; }
.meta { font-size: 12px; color: #999; margin-top: 4px; }
.actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.2s; }
.item:hover .actions { opacity: 1; }
.actions button { background: none; border: none; cursor: pointer; font-size: 14px; padding: 4px; border-radius: 4px; }
.actions button:hover { background: #F5F7FA; }
.empty { text-align: center; padding: 40px; color: #999; font-size: 14px; }
</style>

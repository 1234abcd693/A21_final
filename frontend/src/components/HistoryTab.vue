<template>
  <div class="history-tab">
    <div class="hist-toolbar">
      <input v-model="searchQ" @input="doSearch" placeholder="搜索历史对话..." class="search-inp" />
      <button v-if="selected.length" @click="batchDelete" class="btn-danger">批量删除({{ selected.length }})</button>
      <button @click="exportAll" class="btn-outline">导出全部</button>
      <button @click="loadList" class="btn-outline">刷新</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!sessions.length" class="empty">暂无历史对话</div>

    <div v-else class="hist-list">
      <div v-for="s in sessions" :key="s.session_id" class="hist-card" :class="{ selected: selected.includes(s.session_id) }" @click.self="toggleSelect(s.session_id)">
        <div class="card-check">
          <input type="checkbox" :checked="selected.includes(s.session_id)" @change="toggleSelect(s.session_id)" />
        </div>
        <div class="card-body" @click="openDetail(s)">
          <div class="card-title">
            <span v-if="s.pinned" class="pin-icon">📌</span>
            {{ s.title || '未命名对话' }}
          </div>
          <div class="card-meta">
            <span>{{ s.message_count || 0 }} 条消息</span>
            <span>{{ formatTime(s.updated_at) }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button @click.stop="togglePin(s)" :title="s.pinned?'取消置顶':'置顶'">{{ s.pinned ? '📌' : '📌' }}</button>
          <button @click.stop="startRename(s)" title="重命名">✏️</button>
          <button @click.stop="exportSession(s)" title="导出">📥</button>
          <button @click.stop="delSession(s)" title="删除">🗑</button>
        </div>
      </div>
    </div>

    <!-- Rename modal -->
    <div v-if="renameTarget" class="modal-overlay" @click="renameTarget=null">
      <div class="modal-box" @click.stop>
        <h3>重命名对话</h3>
        <input v-model="newTitle" @keydown.enter="doRename" class="inp" placeholder="输入新标题" />
        <div class="modal-actions">
          <button @click="doRename" class="btn-primary">确认</button>
          <button @click="renameTarget=null" class="btn-outline">取消</button>
        </div>
      </div>
    </div>

    <!-- Detail modal -->
    <div v-if="detailSession" class="modal-overlay" @click="detailSession=null">
      <div class="modal-box wide" @click.stop>
        <h3>{{ detailSession.title || '对话详情' }}</h3>
        <div class="detail-msgs">
          <div v-for="m in detailMessages" :key="m.message_id" :class="['dm', m.role]">
            <div class="dm-role">{{ m.role === 'user' ? '👤 用户' : '🤖 系统' }}</div>
            <div class="dm-content" v-html="renderContent(m.content)"></div>
          </div>
        </div>
        <button @click="detailSession=null" class="btn-outline">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

const sessions = ref([])
const selected = ref([])
const loading = ref(false)
const searchQ = ref('')
const renameTarget = ref(null)
const newTitle = ref('')
const detailSession = ref(null)
const detailMessages = ref([])

async function loadList() {
  loading.value = true
  try {
    const { data } = await api.get('/history', { params: { page: 1, page_size: 200 } })
    sessions.value = data.sessions || []
  } catch {} finally { loading.value = false }
}

async function doSearch() {
  if (!searchQ.value.trim()) { loadList(); return }
  try {
    const { data } = await api.get('/history/search', { params: { q: searchQ.value } })
    sessions.value = data.sessions || []
  } catch {}
}

function toggleSelect(sid) {
  const i = selected.value.indexOf(sid)
  if (i >= 0) selected.value.splice(i, 1)
  else selected.value.push(sid)
}

async function delSession(s) {
  if (!confirm('确定删除对话: ' + (s.title || '未命名') + '?')) return
  try { await api.delete('/history/' + s.session_id); loadList() } catch {}
}

async function batchDelete() {
  if (!confirm('确定删除选中的 ' + selected.value.length + ' 个对话?')) return
  try { await api.delete('/history/batch', { data: { session_ids: selected.value } }); selected.value = []; loadList() } catch {}
}

async function togglePin(s) {
  try { await api.patch('/history/' + s.session_id, { pinned: !s.pinned }); loadList() } catch {}
}

function startRename(s) { renameTarget.value = s; newTitle.value = s.title || '' }
async function doRename() {
  if (!newTitle.value.trim()) return
  try {
    await api.put('/history/' + renameTarget.value.session_id + '/rename', null, { params: { title: newTitle.value } })
    renameTarget.value = null; loadList()
  } catch {}
}

async function exportSession(s) {
  try {
    const r = await api.get('/report', { params: { session_id: s.session_id }, responseType: 'blob' })
    const url = URL.createObjectURL(r.data)
    const a = document.createElement('a'); a.href = url; a.download = 'report.docx'; a.click()
  } catch {}
}

async function exportAll() {
  try {
    const r = await api.get('/report', { responseType: 'blob' })
    const url = URL.createObjectURL(r.data)
    const a = document.createElement('a'); a.href = url; a.download = 'report_all.docx'; a.click()
  } catch {}
}

async function openDetail(s) {
  try {
    const { data } = await api.get('/history/' + s.session_id)
    detailSession.value = s
    detailMessages.value = data.messages || []
  } catch {}
}

function formatTime(t) {
  if (!t) return ''
  return t.replace('T', ' ').slice(0, 16)
}

function renderContent(c) {
  return (c || '').replace(/\n/g, '<br>').replace(/</g, '&lt;')
}

onMounted(() => { loadList() })
</script>

<style scoped>
.history-tab { display: flex; flex-direction: column; height: 100%; }
.hist-toolbar { padding: 12px 20px; display: flex; gap: 10px; align-items: center; border-bottom: 1px solid var(--border); }
.search-inp { flex: 1; max-width: 300px; padding: 8px 12px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
.search-inp:focus { border-color: var(--accent); }
.btn-danger { padding: 6px 14px; background: #EF4444; border: none; border-radius: 6px; color: #fff; cursor: pointer; font-size: 12px; }
.btn-outline { padding: 6px 14px; background: transparent; border: 1px solid var(--border); border-radius: 6px; color: var(--sub); cursor: pointer; font-size: 12px; }
.btn-primary { padding: 8px 16px; background: var(--accent); border: none; border-radius: 8px; color: #fff; cursor: pointer; }
.loading, .empty { text-align: center; padding: 40px; color: var(--sub); }
.hist-list { flex: 1; overflow-y: auto; padding: 12px 20px; }
.hist-card { display: flex; gap: 10px; padding: 12px 14px; margin-bottom: 8px; background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 10px; cursor: pointer; transition: all .2s; align-items: center; }
.hist-card:hover { background: rgba(255,255,255,0.04); border-color: var(--accent); }
.hist-card.selected { border-color: var(--accent); background: rgba(83,52,131,0.1); }
.card-body { flex: 1; }
.card-title { font-size: 15px; color: #fff; margin-bottom: 4px; }
.pin-icon { margin-right: 4px; }
.card-meta { display: flex; gap: 16px; font-size: 12px; color: var(--sub); }
.card-actions { display: flex; gap: 4px; }
.card-actions button { padding: 4px 8px; background: transparent; border: 1px solid var(--border); border-radius: 4px; color: var(--sub); cursor: pointer; font-size: 13px; }
.card-actions button:hover { border-color: var(--accent); }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-box { background: var(--sb); border: 1px solid var(--border); border-radius: 12px; padding: 24px; min-width: 360px; max-width: 90vw; max-height: 80vh; overflow-y: auto; }
.modal-box.wide { width: 700px; }
.modal-box h3 { color: #fff; margin-bottom: 14px; font-size: 16px; }
.modal-actions { display: flex; gap: 10px; margin-top: 14px; justify-content: flex-end; }
.inp { width: 100%; padding: 10px 14px; background: rgba(255,255,255,0.06); border: 1px solid var(--border); border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
.detail-msgs { max-height: 50vh; overflow-y: auto; }
.dm { margin-bottom: 14px; }
.dm-role { font-size: 12px; color: var(--sub); margin-bottom: 4px; }
.dm-content { padding: 10px 14px; background: rgba(255,255,255,0.04); border-radius: 8px; font-size: 14px; color: var(--text); line-height: 1.6; }
.dm.user .dm-content { background: var(--accent); }
</style>

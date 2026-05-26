<template>
  <div class="import-tab">
    <h2>导入知识数据</h2>
    <p class="desc">上传 PDF 或 DOCX 文档，系统将自动抽取知识并导入 Neo4j 和 ChromaDB</p>

    <!-- Admin password check -->
    <div v-if="!authorized" class="auth-box">
      <label>请输入管理员密码以继续：</label>
      <input v-model="adminPass" type="password" class="inp" placeholder="管理员密码" @keydown.enter="checkAdmin" />
      <button @click="checkAdmin" class="btn-primary" :disabled="checking">{{ checking ? '验证中...' : '验证' }}</button>
      <div v-if="authErr" class="err">{{ authErr }}</div>
    </div>

    <!-- Upload area -->
    <div v-else>
      <div class="upload-zone" @dragover.prevent @drop.prevent="onDrop" @click="triggerFile">
        <input type="file" ref="fileInput" accept=".pdf,.docx" @change="onFileChange" style="display:none" />
        <div v-if="!file" class="upload-prompt">
          <div class="upload-icon">📄</div>
          <p>点击或拖拽 PDF/DOCX 文件到此处</p>
        </div>
        <div v-else class="file-info">
          <div class="file-icon">📄</div>
          <div class="file-name">{{ file.name }} ({{ formatSize(file.size) }})</div>
          <button @click.stop="clearFile" class="btn-sm">✕</button>
        </div>
      </div>

      <button v-if="file && !processing" @click="startUpload" class="btn-primary" style="margin-top:16px">开始解析与导入</button>

      <!-- Progress -->
      <div v-if="processing" class="progress-section">
        <div class="progress-bar"><div class="progress-fill" :style="{width: progress+'%'}"></div></div>
        <p class="progress-text">{{ statusText }}</p>
      </div>

      <!-- Results -->
      <div v-if="results" class="results-box">
        <h3>导入结果</h3>
        <div class="result-row"><span>提取候选实体:</span> <strong>{{ results.candidates?.length || 0 }}</strong></div>
        <div class="result-row"><span>导入 Neo4j 实体:</span> <strong>{{ results.imported?.entities || 0 }}</strong></div>
        <div class="result-row"><span>导入 Neo4j 关系:</span> <strong>{{ results.imported?.relationships || 0 }}</strong></div>
        <div class="result-row"><span>导入 ChromaDB chunks:</span> <strong>{{ results.chroma_chunks_added || 0 }}</strong></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/index.js'

const authorized = ref(false)
const adminPass = ref('')
const checking = ref(false)
const authErr = ref('')
const file = ref(null)
const fileInput = ref(null)
const processing = ref(false)
const progress = ref(0)
const statusText = ref('')
const results = ref(null)

async function checkAdmin() {
  checking.value = true; authErr.value = ''
  try {
    await api.post('/auth/admin-verify', { password: adminPass.value })
    authorized.value = true
  } catch { authErr.value = '密码错误' }
  finally { checking.value = false }
}

function triggerFile() { fileInput.value?.click() }
function onFileChange(e) { file.value = e.target.files?.[0] }
function onDrop(e) { file.value = e.dataTransfer.files?.[0] }
function clearFile() { file.value = null; results.value = null }
function formatSize(b) { return b > 1024*1024 ? (b/1024/1024).toFixed(1)+'MB' : Math.ceil(b/1024)+'KB' }

async function startUpload() {
  if (!file.value) return
  processing.value = true; progress.value = 0; results.value = null

  try {
    // Step 1: Parse document
    statusText.value = '正在解析文档...'; progress.value = 20
    const form = new FormData(); form.append('file', file.value)
    const { data: parsed } = await api.post('/parse', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    statusText.value = '正在抽取知识...'; progress.value = 50

    // Step 2: Confirm import
    const { data: confirmed } = await api.post('/confirm', {
      parse_id: parsed.parse_id,
      confirmed: parsed.candidates || [],
      rejected: [],
      edits: []
    })

    statusText.value = '导入完成!'; progress.value = 100
    results.value = {
      candidates: parsed.candidates,
      imported: confirmed.imported,
      chroma_chunks_added: confirmed.chroma_chunks_added
    }
  } catch (e) {
    statusText.value = '导入失败: ' + (e.response?.data?.detail || e.message)
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.import-tab { padding: 30px; max-width: 700px; margin: 0 auto; }
.import-tab h2 { font-size: 22px; color: #fff; margin-bottom: 8px; }
.desc { color: var(--sub); font-size: 14px; margin-bottom: 24px; }
.auth-box { padding: 20px; background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 10px; }
.auth-box label { display: block; font-size: 14px; color: var(--sub); margin-bottom: 10px; }
.inp { width: 100%; padding: 10px 14px; background: rgba(255,255,255,0.06); border: 1px solid var(--border); border-radius: 8px; color: #fff; font-size: 14px; outline: none; margin-bottom: 10px; }
.inp:focus { border-color: var(--accent); }
.btn-primary { padding: 8px 20px; background: var(--accent); border: none; border-radius: 8px; color: #fff; cursor: pointer; font-size: 14px; margin-top: 8px; }
.btn-primary:disabled { opacity: .5; }
.btn-sm { padding: 4px 10px; background: transparent; border: 1px solid var(--border); border-radius: 4px; color: var(--sub); cursor: pointer; }
.err { color: #EF4444; font-size: 13px; margin-top: 8px; }
.upload-zone { margin-top: 16px; padding: 40px; border: 2px dashed var(--border); border-radius: 12px; text-align: center; cursor: pointer; transition: all .2s; }
.upload-zone:hover { border-color: var(--accent); background: rgba(83,52,131,0.05); }
.upload-icon { font-size: 40px; margin-bottom: 12px; }
.upload-prompt p { color: var(--sub); font-size: 14px; }
.file-info { display: flex; align-items: center; gap: 12px; justify-content: center; }
.file-icon { font-size: 30px; }
.file-name { color: #fff; font-size: 15px; }
.progress-section { margin-top: 20px; }
.progress-bar { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--accent); transition: width .5s; }
.progress-text { font-size: 13px; color: var(--sub); margin-top: 8px; }
.results-box { margin-top: 20px; padding: 16px; background: rgba(34,197,94,0.05); border: 1px solid #22C55E; border-radius: 10px; }
.results-box h3 { font-size: 16px; color: #22C55E; margin-bottom: 10px; }
.result-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; color: var(--text); }
.result-row strong { color: #22C55E; }
</style>

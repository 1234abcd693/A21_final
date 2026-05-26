<template>
  <div class="graph-tab">
    <!-- Search bar -->
    <div class="graph-toolbar">
      <div class="search-box">
        <input v-model="keyword" @keydown.enter="doSearch" placeholder="搜索知识图谱节点..." />
        <button @click="doSearch">搜索</button>
      </div>
      <div class="level-selector">
        <label>显示层级：</label>
        <select v-model.number="maxLevel" @change="loadOverview">
          <option :value="2">L2 设备大类</option>
          <option :value="3">L3 设备型号</option>
          <option :value="99">全部节点</option>
        </select>
        <span class="count">节点: {{ nodes.length }} | 边: {{ edges.length }}</span>
      </div>
    </div>

    <!-- Graph canvas -->
    <div class="graph-canvas" ref="canvasRef">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="!nodes.length" class="empty">暂无数据，请先导入知识图谱数据</div>
      <svg v-else ref="svgRef" @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp" @wheel="onWheel">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="30" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#888"/>
          </marker>
        </defs>
        <!-- Edges -->
        <line v-for="(e, i) in renderEdges" :key="'e'+i"
          :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2"
          stroke="#555" stroke-width="1" marker-end="url(#arrow)"/>
        <!-- Nodes -->
        <g v-for="(n, i) in renderNodes" :key="'n'+i" :transform="'translate('+n.x+','+n.y+')'"
           @click="selectNode(n)" class="node-group">
          <circle :r="n.r || 14" :fill="nodeColor(n.label)"/>
          <text y="5" text-anchor="middle" fill="white" font-size="11">{{ n.label[0] }}</text>
          <text y="24" text-anchor="middle" fill="#ccc" font-size="11">{{ n.name?.length > 6 ? n.name.slice(0,6)+'..' : n.name }}</text>
        </g>
      </svg>
    </div>

    <!-- Search results sidebar -->
    <div v-if="searchResults.length" class="search-results">
      <h3>搜索结果 ({{ searchResults.length }})</h3>
      <div v-for="r in searchResults" :key="r.uid" class="result-item" @click="selectByUid(r.uid)">
        <span class="result-label" :style="{color: nodeColor(r.label)}">[{{ r.label }}]</span>
        {{ r.name }}
      </div>
    </div>

    <!-- Node detail panel -->
    <div v-if="selectedNode" class="detail-panel">
      <h3>{{ selectedNode.name }}</h3>
      <p class="detail-type">类型: {{ selectedNode.label }}</p>
      <div v-if="selectedNode.properties?.source_doc" class="detail-source">来源: {{ selectedNode.properties.source_doc }}</div>
      <div v-if="nodeRelations.length" class="detail-relations">
        <h4>关联关系</h4>
        <div v-for="r in nodeRelations" :key="r.type+r.to_uid" class="rel-item">
          <span class="rel-type">{{ r.type }}</span>
          <span class="rel-name">{{ r.to_name }}</span>
        </div>
      </div>
      <button @click="selectedNode=null" class="close-btn">关闭</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api/index.js'

const keyword = ref('')
const maxLevel = ref(3)
const nodes = ref([])
const edges = ref([])
const loading = ref(false)
const selectedNode = ref(null)
const nodeRelations = ref([])
const searchResults = ref([])

const canvasRef = ref(null)
const svgRef = ref(null)

// Force layout
const renderNodes = ref([])
const renderEdges = ref([])
let dragging = false
let dragNode = null
let offsetX = 0, offsetY = 0

function layoutGraph() {
  if (!nodes.value.length) return
  const w = 800, h = 500
  const positions = {}
  // Simple circular layout by label
  const byLabel = {}
  nodes.value.forEach(n => {
    if (!byLabel[n.label]) byLabel[n.label] = []
    byLabel[n.label].push(n)
  })
  const labels = Object.keys(byLabel)
  labels.forEach((label, li) => {
    const angleStep = (2 * Math.PI) / labels.length
    const cx = w/2 + Math.cos(angleStep * li) * w/3
    const cy = h/2 + Math.sin(angleStep * li) * h/3
    const group = byLabel[label]
    group.forEach((n, i) => {
      const a = (2 * Math.PI * i) / group.length
      positions[n.uid] = { x: cx + Math.cos(a) * 40, y: cy + Math.sin(a) * 40 }
    })
  })
  renderNodes.value = nodes.value.map(n => ({
    ...n, x: positions[n.uid]?.x || w/2, y: positions[n.uid]?.y || h/2, r: 14
  }))
  renderEdges.value = edges.value.map(e => {
    const from = positions[e.from], to = positions[e.to]
    return from && to ? { x1: from.x, y1: from.y, x2: to.x, y2: to.y, ...e } : null
  }).filter(Boolean)
}

function nodeColor(label) {
  const colors = {
    Symptom: '#EF4444', Cause: '#F97316', Step: '#22C55E',
    Equipment: '#3B82F6', SparePart: '#A855F7', Tool: '#F59E0B', Precaution: '#EC4899'
  }
  return colors[label] || '#888'
}

async function loadOverview() {
  loading.value = true
  try {
    const { data } = await api.get('/graph/overview')
    let allNodes = data.nodes || []
    if (maxLevel.value < 99) {
      allNodes = allNodes.filter(n => (n.level || 0) <= maxLevel.value || !n.level)
    }
    nodes.value = allNodes
    edges.value = data.edges || []
    layoutGraph()
  } catch (e) {
    console.error('Load graph failed:', e)
  } finally {
    loading.value = false
  }
}

async function doSearch() {
  if (!keyword.value.trim()) { loadOverview(); return }
  try {
    const { data } = await api.get('/graph/search', { params: { q: keyword.value, limit: 20 } })
    searchResults.value = data.results || []
  } catch (e) {
    searchResults.value = []
  }
}

async function selectNode(n) {
  selectedNode.value = { ...n }
  try {
    const { data } = await api.get(`/graph/node/${n.uid}`)
    selectedNode.value = { ...data, label: data.label, name: data.name, properties: data.properties }
    nodeRelations.value = [
      ...(data.relations?.incoming || []).map(r => ({ ...r, type: '← ' + r.type, to_name: r.from_name })),
      ...(data.relations?.outgoing || []).map(r => ({ ...r, type: '→ ' + r.type, to_name: r.to_name })),
    ]
  } catch { nodeRelations.value = [] }
}

function selectByUid(uid) {
  const n = nodes.value.find(x => x.uid === uid)
  if (n) selectNode(n)
}

function onMouseDown(e) {
  const el = e.target.closest('.node-group')
  if (el) { dragging = true; dragNode = el }
}
function onMouseMove(e) { if (dragging && dragNode) { /* simplified */ } }
function onMouseUp() { dragging = false; dragNode = null }
function onWheel(e) { e.preventDefault() }

onMounted(() => { loadOverview() })
</script>

<style scoped>
.graph-tab { display: flex; flex-direction: column; height: 100%; position: relative; }
.graph-toolbar { padding: 12px 20px; display: flex; gap: 16px; align-items: center; border-bottom: 1px solid var(--border); }
.search-box { display: flex; gap: 8px; }
.search-box input { width: 240px; padding: 8px 12px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 8px; color: #fff; font-size: 14px; outline: none; }
.search-box input:focus { border-color: var(--accent); }
.search-box button { padding: 8px 16px; background: var(--accent); border: none; border-radius: 8px; color: #fff; cursor: pointer; font-size: 13px; }
.level-selector { display: flex; gap: 8px; align-items: center; font-size: 13px; color: var(--sub); }
.level-selector select { padding: 6px 10px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 6px; color: #fff; font-size: 13px; }
.count { margin-left: 12px; }
.graph-canvas { flex: 1; overflow: hidden; position: relative; min-height: 400px; }
.graph-canvas svg { width: 100%; height: 100%; }
.loading, .empty { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); color: var(--sub); font-size: 16px; }
.node-group { cursor: pointer; transition: opacity .2s; }
.node-group:hover { opacity: .8; }
.search-results { position: absolute; right: 8px; top: 60px; width: 260px; max-height: 400px; overflow-y: auto; background: rgba(22,33,62,0.95); border: 1px solid var(--border); border-radius: 10px; padding: 12px; z-index: 10; }
.search-results h3 { font-size: 14px; color: #fff; margin-bottom: 8px; }
.result-item { padding: 6px 8px; cursor: pointer; border-radius: 6px; font-size: 13px; color: var(--text); }
.result-item:hover { background: rgba(255,255,255,0.06); }
.result-label { font-size: 11px; margin-right: 6px; }
.detail-panel { position: absolute; left: 8px; top: 60px; width: 280px; max-height: 70%; overflow-y: auto; background: rgba(22,33,62,0.95); border: 1px solid var(--border); border-radius: 10px; padding: 16px; z-index: 10; }
.detail-panel h3 { font-size: 16px; color: #fff; margin-bottom: 6px; }
.detail-type { font-size: 13px; color: var(--accent); margin-bottom: 4px; }
.detail-source { font-size: 12px; color: var(--sub); margin-bottom: 10px; }
.detail-relations h4 { font-size: 13px; color: #fff; margin: 10px 0 6px; }
.rel-item { display: flex; gap: 8px; padding: 4px 0; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.04); }
.rel-type { color: var(--accent); white-space: nowrap; }
.rel-name { color: var(--text); }
.close-btn { margin-top: 10px; padding: 6px 14px; background: transparent; border: 1px solid var(--border); border-radius: 6px; color: var(--sub); cursor: pointer; font-size: 12px; }
</style>

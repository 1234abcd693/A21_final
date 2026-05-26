<template>
<div class="gv">
  <div class="tb">
    <input v-model="q" placeholder="搜索实体..." @keyup.enter="onS"/>
    <button @click="onS">搜索</button>
    <select v-model="flt" @change="render" class="s">
      <option value="">全部</option>
      <option v-for="t in ts" :key="t" :value="t">{{t}}</option>
    </select>
    <select v-model="lim" @change="render" class="s">
      <option :value="0">不限</option><option :value="30">30</option>
      <option :value="60">60</option><option :value="100">100</option>
    </select>
  </div>
  <div ref="c" class="gc"></div>
  <div class="lg">
    <span v-for="l in lg" :key="l.l" class="li"><span class="d" :style="{background:l.c}"></span>{{l.l}}</span>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import G6 from '@antv/g6'
import { graphAPI } from '../api/index.js'

const c = ref(null), q = ref(''), flt = ref(''), lim = ref(60)
let graph = null, aN = [], aE = []

const lg = [
  {l:'设备',c:'#002EA6'},{l:'故障',c:'#EF4444'},{l:'原因',c:'#F59E0B'},
  {l:'维修',c:'#10B981'},{l:'注意',c:'#8B5CF6'},{l:'备件',c:'#06B6D4'},{l:'工具',c:'#6B7280'}
]
const nc = {Equipment:'#002EA6',Symptom:'#EF4444',Cause:'#F59E0B',Step:'#10B981',Precaution:'#8B5CF6',SparePart:'#06B6D4',Tool:'#6B7280'}
const ec = {CAUSED_BY:'#F59E0B',FIXED_BY:'#10B981',NEXT_STEP:'#06B6D4',BELONGS_TO:'#002EA6',SUBCLASS_OF:'#002EA6',HAS_PRECAUTION:'#8B5CF6',REQUIRES_TOOL:'#6B7280',USES_SPAREPART:'#06B6D4'}
const ts = ['Equipment','Symptom','Cause','Step','Precaution','SparePart','Tool']

onMounted(async () => {
  try { const { data } = await graphAPI.overview(); aN = data.nodes || []; aE = data.edges || []; render() } catch (e) {}
})

function onS() {
  if (!q.value.trim()) { render(); return }
  graphAPI.search(q.value).then(({ data }) => {
    const s = new Set((data.results || []).map(r => r.uid)); render(s)
  })
}

function render(hl) {
  let ns = aN, es = aE
  if (flt.value) { ns = ns.filter(n => n.label === flt.value); const ids = new Set(ns.map(n => n.uid)); es = es.filter(e => ids.has(e.from) && ids.has(e.to)) }
  if (lim.value > 0) { ns = ns.slice(0, lim.value); const ids = new Set(ns.map(n => n.uid)); es = es.filter(e => ids.has(e.from) && ids.has(e.to)) }
  if (!c.value) return
  if (graph) { graph.destroy() }

  const w = c.value.clientWidth || 800, h = c.value.clientHeight || 500
  graph = new G6.Graph({
    container: c.value, width: w, height: h, fitView: true, fitViewPadding: 60, animate: true,
    modes: { default: ['drag-canvas', 'zoom-canvas', 'drag-node'] },
    layout: { type: 'gForce', preventOverlap: true, nodeSpacing: 160, linkDistance: 220, nodeStrength: 2000, gravity: 8 },
    defaultNode: { size: 26, labelCfg: { style: { fill: '#fff', fontSize: 10 } }, style: { stroke: '#fff', lineWidth: 2, cursor: 'pointer' } },
    defaultEdge: { type: 'cubic-horizontal', style: { lineWidth: 1.5, stroke: '#D1D5DB', endArrow: { path: G6.Arrow.triangle(5, 7, 0), fill: '#D1D5DB' } } },
  })

  const nodes = ns.map(n => ({
    id: n.uid, label: (n.name || '').length > 10 ? (n.name || '').slice(0, 10) : (n.name || ''), lt: n.label,
    size: ['Equipment', 'Symptom'].includes(n.label) ? 28 : 22,
    style: { fill: nc[n.label] || '#002EA6' }
  }))

  const labelMap = { CAUSED_BY: '原因', FIXED_BY: '维修' }
  const importantTypes = ['CAUSED_BY', 'FIXED_BY']
  const edges = es.map(e => ({
    id: e.from + '-' + e.to, source: e.from, target: e.to,
    style: { stroke: ec[e.type] || '#D1D5DB', lineWidth: importantTypes.includes(e.type) ? 2.5 : 1.5, endArrow: { path: G6.Arrow.triangle(5, 7, 0), fill: ec[e.type] || '#D1D5DB' } },
    label: labelMap[e.type] || ''
  }))

  graph.data({ nodes, edges }); graph.render()

  graph.on('node:click', async e => { try { await graphAPI.node(e.item.getModel().id) } catch {} })
  graph.on('node:dblclick', async e => { await expand(e.item.getModel().id) })

  if (hl) {
    graph.getNodes().forEach(n => {
      const h = hl.has(n.getModel().id)
      graph.updateItem(n, { style: { opacity: h ? 1 : 0.06, stroke: h ? '#FFE76F' : (nc[n.getModel().lt] || '#002EA6'), lineWidth: h ? 4 : 2 } })
    })
  }
}

async function expand(uid) {
  try {
    const { data } = await graphAPI.expand(uid)
    const ex = new Set(graph.getNodes().map(n => n.getModel().id))
    for (const n of (data.nodes || [])) {
      if (!ex.has(n.uid)) { graph.addItem('node', { id: n.uid, label: (n.name || '').length > 10 ? (n.name || '').slice(0, 10) : (n.name || ''), lt: n.label, size: 22, style: { fill: nc[n.label] || '#002EA6' } }); ex.add(n.uid) }
    }
    for (const e of (data.edges || [])) {
      const eid = e.from + '-' + e.to
      if (!graph.findById(eid)) { graph.addItem('edge', { id: eid, source: e.from, target: e.to, style: { stroke: ec[e.type] || '#D1D5DB', lineWidth: 2, endArrow: { path: G6.Arrow.triangle(5, 7, 0), fill: ec[e.type] || '#D1D5DB' } } }) }
    }
    graph.layout(); graph.fitView(40)
  } catch (e) {}
}
</script>

<style scoped>
.gv { width: 100%; height: 100%; position: relative; display: flex; flex-direction: column; }
.tb { display: flex; gap: 8px; padding: 10px 14px; background: #fff; border-bottom: 1px solid #F0F0F0; z-index: 10; }
.tb input { flex: 1; padding: 7px 12px; border: 1.5px solid #E5E7EB; border-radius: 8px; font-size: 13px; outline: none; }
.tb input:focus { border-color: #002EA6; }
.tb button { padding: 7px 14px; background: #002EA6; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
.s { padding: 6px 10px; border: 1.5px solid #E5E7EB; border-radius: 8px; font-size: 13px; outline: none; background: #fff; }
.gc { flex: 1; background: #F9FAFB; }
.lg { position: absolute; bottom: 14px; left: 14px; display: flex; gap: 10px; background: rgba(255,255,255,0.95); padding: 8px 16px; border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,0.06); flex-wrap: wrap; z-index: 10; }
.li { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #666; }
.d { width: 10px; height: 10px; border-radius: 50%; }
</style>

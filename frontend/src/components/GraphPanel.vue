<template>
  <div class="graph-panel" ref="container">
    <svg ref="svgRef">
      <defs>
        <marker v-for="t in edgeTypes" :key="t" :id="`arrow-${t}`" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" :fill="edgeColors[t] || '#999'" />
        </marker>
      </defs>
    </svg>
    <div class="controls">
      <button @click="zoomIn" title="放大">+</button>
      <button @click="zoomOut" title="缩小">−</button>
      <button @click="resetView" title="重置">⌂</button>
    </div>
    <div class="legend">
      <span v-for="item in legend" :key="item.label" class="legend-item">
        <span class="dot" :style="{ background: item.color }"></span>{{ item.label }}
      </span>
    </div>
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { graphAPI } from '../api/index.js'

const props = defineProps({ highlightNodes: { type: Array, default: () => [] } })
const emit = defineEmits(['node-click'])
const container = ref(null), svgRef = ref(null), loading = ref(false)

const legend = [
  { label: '设备', color: '#002EA6' }, { label: '故障', color: '#FF4D4F' },
  { label: '原因', color: '#FA8C16' }, { label: '维修', color: '#52C41A' },
  { label: '注意', color: '#722ED1' }, { label: '备件', color: '#13C2C2' },
  { label: '工具', color: '#8C8C8C' },
]
const colorMap = { Equipment: '#002EA6', Symptom: '#FF4D4F', Cause: '#FA8C16', Step: '#52C41A', Precaution: '#722ED1', SparePart: '#13C2C2', Tool: '#8C8C8C' }
const edgeColors = { CAUSED_BY: '#FA8C16', FIXED_BY: '#52C41A', NEXT_STEP: '#13C2C2', BELONGS_TO: '#002EA6', SUBCLASS_OF: '#002EA6', HAS_PRECAUTION: '#722ED1', REQUIRES_TOOL: '#8C8C8C', USES_SPAREPART: '#13C2C2' }
const edgeTypes = Object.keys(edgeColors)

let sim, svg, g, currentTransform = d3.zoomIdentity
const expandedNodes = new Set()  // 已展开的节点 uid

onMounted(async () => {
  await loadOverview()
})

watch(() => props.highlightNodes, ids => {
  highlight(ids)
})

function highlight(ids) {
  if (!svg) return
  const isets = new Set(ids)
  svg.selectAll('circle.node-circle')
    .attr('opacity', d => {
      if (!ids.length) return 1
      return isets.has(d.uid) ? 1 : 0.12
    })
    .attr('stroke-width', d => isets.has(d.uid) ? 3 : 1.5)
    .attr('stroke', d => isets.has(d.uid) ? '#FFE76F' : '#fff')
    .classed('pulse', d => isets.has(d.uid))

  svg.selectAll('text.node-label')
    .attr('opacity', d => {
      if (!ids.length) return 1
      return isets.has(d.uid) ? 1 : 0.15
    })
    .attr('font-weight', d => isets.has(d.uid) ? 'bold' : 'normal')
    .attr('font-size', d => isets.has(d.uid) ? '13px' : '10px')
}

async function loadOverview() {
  loading.value = true
  try {
    const { data } = await graphAPI.overview()
    initGraph(data.nodes || [], data.edges || [])
  } catch (e) { console.error('图谱加载失败:', e) }
  finally { loading.value = false }
}

function initGraph(nodes, edges) {
  const w = container.value?.clientWidth || 900
  const h = container.value?.clientHeight || 600

  svg = d3.select(svgRef.value).attr('viewBox', [0, 0, w, h])
  svg.selectAll('g').remove()
  g = svg.append('g')

  const zoom = d3.zoom().scaleExtent([0.15, 5]).on('zoom', e => {
    currentTransform = e.transform
    g.attr('transform', e.transform)
  })
  svg.call(zoom)

  // Initial position: center + small random spread
  nodes.forEach(n => {
    n.x = w / 2 + (Math.random() - 0.5) * 200
    n.y = h / 2 + (Math.random() - 0.5) * 200
  })

  drawGraph(nodes, edges)
  svg.call(zoom.transform, d3.zoomIdentity.translate(w / 2 - 400, h / 2 - 300).scale(0.6))
}

function drawGraph(nodes, edges) {
  g.selectAll('*').remove()

  // Edge lines with arrows
  const link = g.selectAll('line').data(edges, d => `${d.from}-${d.to}-${d.type}`).join('line')
    .attr('stroke', d => edgeColors[d.type] || '#D0D8E8')
    .attr('stroke-width', d => d.type === 'CAUSED_BY' ? 2 : 1.2)
    .attr('stroke-opacity', 0.55)
    .attr('marker-end', d => `url(#arrow-${d.type})`)

  // Edge labels (on hover or always for important edges)
  const edgeLabels = g.selectAll('text.edge-label').data(edges.filter(e => ['CAUSED_BY', 'FIXED_BY', 'BELONGS_TO'].includes(e.type)),
    d => `${d.from}-${d.to}-${d.type}`).join('text')
    .text(d => d.type === 'CAUSED_BY' ? '原因' : d.type === 'FIXED_BY' ? '维修' : d.type === 'BELONGS_TO' ? '归属' : '')
    .attr('class', 'edge-label')
    .attr('font-size', 9).attr('text-anchor', 'middle').attr('dy', -6)
    .attr('fill', d => edgeColors[d.type] || '#999')
    .attr('opacity', 0.7)

  // Nodes
  const node = g.selectAll('circle').data(nodes, d => d.uid).join('circle')
    .attr('class', 'node-circle')
    .attr('r', d => d.label === 'Equipment' ? 14 : d.label === 'Symptom' ? 9 : 7)
    .attr('fill', d => colorMap[d.label] || '#002EA6')
    .attr('stroke', '#fff').attr('stroke-width', 1.5)
    .style('cursor', 'pointer')
    .on('click', async (event, d) => {
      event.stopPropagation()
      try {
        const { data: detail } = await graphAPI.node(d.uid)
        emit('node-click', detail)
      } catch (e) {}
    })
    .on('dblclick', async (event, d) => {
      event.stopPropagation()
      await toggleExpand(d)
    })
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null }))

  node.append('title').text(d => `${d.label}: ${d.name}${expandedNodes.has(d.uid) ? ' (已展开)' : ' (双击展开)'}`)

  // Labels
  const label = g.selectAll('text.node-label').data(nodes, d => d.uid).join('text')
    .attr('class', 'node-label')
    .text(d => d.name.length > 8 ? d.name.slice(0, 8) + '…' : d.name)
    .attr('font-size', 10).attr('text-anchor', 'middle').attr('dy', d => d.label === 'Equipment' ? 26 : 19)
    .attr('fill', '#555').style('pointer-events', 'none')

  // Force simulation
  if (sim) sim.stop()
  sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.uid).distance(d => d.type === 'SUBCLASS_OF' ? 60 : 120))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter((container.value?.clientWidth || 900) / 2, (container.value?.clientHeight || 600) / 2))
    .force('collision', d3.forceCollide(30))
    .alpha(0.5)
    .on('tick', () => {
      link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
      node.attr('cx', d => d.x).attr('cy', d => d.y)
      label.attr('x', d => d.x).attr('y', d => d.y)
      edgeLabels.attr('x', d => (d.source.x + d.target.x) / 2).attr('y', d => (d.source.y + d.target.y) / 2)
    })

  // Click on background = deselect
  svg.on('click', () => {})
}

async function toggleExpand(nodeData) {
  const uid = nodeData.uid
  if (expandedNodes.has(uid)) {
    // Collapse: remove all nodes that were added by this expansion
    expandedNodes.delete(uid)
    // Reload overview (simplest collapse strategy)
    await loadOverview()
    return
  }

  // Expand
  try {
    const { data } = await graphAPI.expand(uid)
    expandedNodes.add(uid)

    // Get current nodes from simulation
    const currentNodes = sim.nodes()
    const currentEdges = sim.force('link').links()
    const existingIds = new Set(currentNodes.map(n => n.uid))
    const existingEdges = new Set(currentEdges.map(e => `${e.from || e.source?.uid}-${e.to || e.target?.uid}`))

    // Add new nodes
    const newNodes = []
    for (const n of (data.nodes || [])) {
      if (!existingIds.has(n.uid)) {
        n.x = nodeData.x + (Math.random() - 0.5) * 150
        n.y = nodeData.y + (Math.random() - 0.5) * 150
        newNodes.push(n)
        existingIds.add(n.uid)
      }
    }

    // Add new edges
    const newEdges = []
    for (const e of (data.edges || [])) {
      const key = `${e.from}-${e.to}`
      if (!existingEdges.has(key)) {
        newEdges.push({ source: e.from, target: e.to, type: e.type, priority: e.priority })
        existingEdges.add(key)
      }
    }

    const allNodes = [...currentNodes, ...newNodes]
    const allEdges = [...currentEdges, ...newEdges]
    drawGraph(allNodes, allEdges)
  } catch (e) { console.error('展开失败:', e) }
}

function zoomIn() {
  currentTransform = currentTransform.scale(1.2)
  svg.transition().duration(300).call(d3.zoom().transform, currentTransform)
}
function zoomOut() {
  currentTransform = currentTransform.scale(0.8)
  svg.transition().duration(300).call(d3.zoom().transform, currentTransform)
}
function resetView() {
  const w = container.value?.clientWidth || 900; const h = container.value?.clientHeight || 600
  currentTransform = d3.zoomIdentity.translate(w / 2 - 400, h / 2 - 300).scale(0.6)
  svg.transition().duration(500).call(d3.zoom().transform, currentTransform)
}
</script>

<style scoped>
.graph-panel { width: 100%; height: 100%; position: relative; background: linear-gradient(180deg, #F5F7FA 0%, #EEF1F6 100%); overflow: hidden; }
svg { width: 100%; height: 100%; }
.controls { position: absolute; top: 12px; right: 12px; display: flex; flex-direction: column; gap: 4px; }
.controls button { width: 32px; height: 32px; border-radius: 8px; border: 1px solid #D0D8E8; background: #fff; cursor: pointer; font-size: 16px; color: #002EA6; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.controls button:hover { background: #F0F4FF; border-color: #002EA6; }
.legend { position: absolute; bottom: 12px; left: 12px; display: flex; gap: 10px; background: rgba(255,255,255,0.94); padding: 6px 14px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #555; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.loading-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(245,247,250,0.7); display: flex; align-items: center; justify-content: center; }
.spinner { width: 36px; height: 36px; border: 3px solid #E8ECF1; border-top-color: #002EA6; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

:deep(.pulse) { animation: nodePulse 1.5s ease-in-out infinite; }
@keyframes nodePulse {
  0%, 100% { r: attr(r px, 7); }
  50% { r: calc(attr(r px, 7) + 3); }
}
</style>

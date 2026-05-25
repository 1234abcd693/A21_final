<template>
  <div class="graph-panel" ref="container">
    <svg ref="svgRef"></svg>
    <div class="legend">
      <span v-for="item in legend" :key="item.label" class="legend-item">
        <span class="dot" :style="{ background: item.color }"></span>{{ item.label }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import { graphAPI } from '../api/index.js'

const props = defineProps({ highlightNodes: { type: Array, default: () => [] } })
const emit = defineEmits(['node-click'])
const container = ref(null), svgRef = ref(null)

const legend = [
  { label: '设备', color: '#002EA6' }, { label: '故障', color: '#FF4D4F' },
  { label: '原因', color: '#FA8C16' }, { label: '维修', color: '#52C41A' },
  { label: '注意', color: '#722ED1' }, { label: '备件', color: '#13C2C2' }, { label: '工具', color: '#8C8C8C' },
]
const colorMap = { Equipment: '#002EA6', Symptom: '#FF4D4F', Cause: '#FA8C16', Step: '#52C41A', Precaution: '#722ED1', SparePart: '#13C2C2', Tool: '#8C8C8C' }
let sim

onMounted(async () => {
  try {
    const { data } = await graphAPI.overview()
    renderGraph(data.nodes || [], data.edges || [])
  } catch (e) { console.error(e) }
})

watch(() => props.highlightNodes, ids => {
  if (!sim) return
  d3.select(svgRef.value).selectAll('circle').attr('opacity', d => ids.includes(d.uid) ? 1 : 0.15).attr('stroke-width', d => ids.includes(d.uid) ? 3 : 2).attr('stroke', d => ids.includes(d.uid) ? '#FFE76F' : '#fff')
})

function renderGraph(nodes, edges) {
  const svg = d3.select(svgRef.value)
  const w = container.value?.clientWidth || 900, h = container.value?.clientHeight || 600
  svg.attr('viewBox', [0, 0, w, h]).selectAll('*').remove()
  const g = svg.append('g')
  svg.call(d3.zoom().scaleExtent([0.2, 4]).on('zoom', e => g.attr('transform', e.transform)))

  const link = g.selectAll('line').data(edges).join('line').attr('stroke', '#D0D8E8').attr('stroke-width', 1.5).attr('stroke-opacity', 0.6)

  const node = g.selectAll('circle').data(nodes).join('circle')
    .attr('r', d => d.label === 'Equipment' ? 12 : 7)
    .attr('fill', d => colorMap[d.label] || '#002EA6').attr('stroke', '#fff').attr('stroke-width', 2)
    .style('cursor', 'pointer')
    .on('click', async (_, d) => {
      try { const { data: detail } = await graphAPI.node(d.uid); emit('node-click', detail) } catch (e) {}
    })
    .call(d3.drag().on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null }))

  node.append('title').text(d => `${d.label}: ${d.name}`)

  const label = g.selectAll('text').data(nodes).join('text').text(d => d.name.length > 10 ? d.name.slice(0, 10) + '…' : d.name).attr('font-size', 10).attr('text-anchor', 'middle').attr('dy', 22).attr('fill', '#555').style('pointer-events', 'none')

  sim = d3.forceSimulation(nodes).force('link', d3.forceLink(edges).id(d => d.uid).distance(100)).force('charge', d3.forceManyBody().strength(-300)).force('center', d3.forceCenter(w / 2, h / 2)).force('collision', d3.forceCollide(24))
    .on('tick', () => { link.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y); node.attr('cx', d => d.x).attr('cy', d => d.y); label.attr('x', d => d.x).attr('y', d => d.y) })
}
</script>

<style scoped>
.graph-panel { width: 100%; height: 100%; position: relative; background: linear-gradient(180deg, #F5F7FA, #EEF1F6); }
svg { width: 100%; height: 100%; }
.legend { position: absolute; bottom: 12px; left: 12px; display: flex; gap: 10px; background: rgba(255,255,255,0.92); padding: 6px 14px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #555; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
</style>
